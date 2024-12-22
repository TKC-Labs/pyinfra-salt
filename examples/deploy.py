"""
Deploy Salt services using the bootstrap-salt.sh script.

This script will download the latest salt-bootstrap.sh script from the SaltStack GitHub
"""

import os

from pyinfra import host, logger
from pyinfra.operations import files, systemd
from pyinfra.facts.files import Directory, File, FindFiles

from pyinfra_salt.salt import bootstrap_salt, download_salt_bootstrap_script


def deploy_files(files_dir, destination_dir):
    """
    Copy files from the specified files directory to the specified
    destination directory.

    Remove files from the specified destination directory that do not exist
    in the specified files directory.

    Collect a list of changes made and return the operation return objects
    """
    changes = []

    # Deploy files from files_dir to destination_dir
    for filename in os.listdir(files_dir):
        if os.path.isfile(os.path.join(files_dir, filename)):
            changes.append(
                files.put(
                    name=f"Deploying file {destination_dir}/{filename}",
                    src=os.path.join(files_dir, filename),
                    dest=os.path.join(destination_dir, filename),
                    mode="644",
                    _sudo=True,
                )
            )

    # Prepare to remove files from destination_dir that do not exist
    # in files_dir
    source_files = set(os.listdir(files_dir))
    destination_files = set(
        os.path.basename(file)
        for file in host.get_fact(FindFiles, path=destination_dir)
    )

    # Remove specific files from the destination_files set
    # These are files deployed by the bootstrap-salt.sh script that
    # we don't want to "manage" with pyinfra
    for bootstrap_file in [
        "99-master-address.conf",
        "_schedule.conf",
    ]:
        if bootstrap_file not in source_files:
            destination_files.discard(bootstrap_file)

    # Build our list of files to remove
    files_to_remove = destination_files - source_files

    # Remove any files on the files_to_remove list from the
    # destination directory
    if files_to_remove:
        logger.info(f"Removing files {destination_dir}/{files_to_remove}")

        for filename in files_to_remove:
            changes.append(
                files.file(
                    name=f"Removing file {filename}",
                    path=os.path.join(destination_dir, filename),
                    present=False,
                    _sudo=True,
                )
            )

    return changes


# Download the latest salt-bootstrap.sh script if it is not present
if not host.get_fact(File, path="/usr/local/bin/bootstrap-salt.sh"):
    download_salt_bootstrap_script()
else:
    logger.info(
        "File /usr/local/bin/bootstrap-salt.sh already exists, skipping download"
    )


# Run the bootstrap script if the salt config directory is not present
if not host.get_fact(Directory, path="/etc/salt"):
    bootstrap_salt()
else:
    logger.info("Directory /etc/salt already exists, skipping bootstrap-salt.sh script")


config_options = host.data.get("options", {})
config_install_options = config_options.get("install", {})


# Deploy configuration files from files/master.d
if config_install_options.get("master", None):
    logger.info("Deploying controller config from files/master.d")
    files_dir = "files/master.d"
    destination_dir = "/etc/salt/master.d"
    master_changes = deploy_files(files_dir, destination_dir)

    # Customize the /etc/salt/master configuration
    if host.get_fact(File, path="/etc/salt/master"):
        logger.info("Customizing /etc/salt/master configuration")
        salt_master_user = files.line(
            name="Ensure salt-master runs as root rather than salt",
            path="/etc/salt/master",
            line=r"user: salt",
            replace="user: root",
            _sudo=True,
        )

    # Handle controller service restarts
    if any(change.changed for change in master_changes) or salt_master_user.changed:
        master_restart = systemd.service(
            name="Restart salt-master service",
            service="salt-master",
            running=True,
            restarted=True,
            _sudo=True,
        )


# Deploy configuration files from files/minion.d
if config_install_options.get("minion", False):
    logger.info("Deploying minion config from files/minion.d")
    files_dir = "files/minion.d"
    destination_dir = "/etc/salt/minion.d"
    minion_changes = deploy_files(files_dir, destination_dir)

    # Handle minion service restarts
    if any(change.changed for change in minion_changes):
        minion_restart = systemd.service(
            name="Restart salt-minion service",
            service="salt-minion",
            running=True,
            restarted=True,
            _sudo=True,
        )
