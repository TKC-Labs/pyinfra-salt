"""
pyinfra deploys for deploying salt controllers and minions
"""
import requests

from pyinfra import host
from pyinfra import logger
from pyinfra.api.deploy import deploy
from pyinfra.operations import files, server


def _get_latest_boostrap_salt_url():
    """
    Get the latest salt-bootstrap release URL from the salt-bootstrap GitHub
    """
    release = requests.head(
        "https://github.com/saltstack/salt-bootstrap/releases/latest"
    )

    try:
        latest_build_tag = release.headers.get("location", None).split("/")[-1]
        bootstrap_salt_url = f"https://github.com/saltstack/salt-bootstrap/releases/download/{latest_build_tag}/bootstrap-salt.sh"
    except Exception as e:
        logger.error(
            f"Error getting latest salt-bootstrap release URL, returning default. Error was, {e}"
        )
        bootstrap_salt_url = "https://github.com/saltstack/salt-bootstrap/releases/download/v2024.12.12/bootstrap-salt.sh"

    return bootstrap_salt_url


@deploy("Download Salt Bootstrap Script")
def download_salt_bootstrap_script(bootstrap_url=_get_latest_boostrap_salt_url()):
    """Download the latest salt-bootstrap script"""

    # Get the content of the sha256 file for validating the script
    sha256_response = requests.get(f"{bootstrap_url}.sha256")
    sha256_response.raise_for_status()

    files.download(
        src=bootstrap_url,
        dest="/usr/local/bin/bootstrap-salt.sh",
        user="root",
        group="root",
        mode="0700",
        force=False,
        cache_time=31536000,
        sha256sum=sha256_response.text.strip(),
        _sudo=True,
    )

    return


@deploy("Bootstrap Salt")
def bootstrap_salt():
    """
    Deploy the salt-bootstrap script and run it if the salt config directory is not present

    Example of config_options from the host.data['options'] dictionary:

    {
        "ssh_user": "tkcadmin",               # SSH user to use
        "ssh_key": "~/.ssh/id_ed25519",       # Path to the SSH key to use
        "install_type": "stable",             # testing, git, onedir, onedir_rc
        "salt_version": "3006.9",             # Version of salt to install
        "options": {
            "master_fqdn": "salt.local",      # -A Set master DNS name or IP
            "debug:": False,                  # -D Show debug output
            "no_colors": False,               # -n No colours
            "post_install_start": False,      # -X Do not start daemons after installation
            "disable_service_checks": False,  # -d Disable checking enabled services
            "install": {
                "cloud": False,   # -L Also install salt-cloud and required python-libcloud package
                "master": False,  # -M Also install salt-master
                "syndic": False,  # -S Also install salt-syndic
                "api": False,     # -W Also install salt-api
                "minion": True,   # -N Do not install salt-minion
            },
        },
    }

    """
    # Build install options list
    cmdline_options = list()

    config_options = host.data.get("options", {})
    config_install_options = config_options.get("install", {})

    if config_options.get("master_fqdn", None):
        cmdline_options.append(f"-A {config_options.get("master_fqdn", 'salt')}")

    if config_options.get("minion_id", None):
        cmdline_options.append(
            f"-i {config_options.get("minion_id", server.Hostname)}"
        )

    if config_options.get("debug", None):
        cmdline_options.append("-D")

    if config_options.get("no_colors", None):
        cmdline_options.append("-n")

    if config_options.get("post_install_start", None):
        cmdline_options.append("-X")

    if config_options.get("disable_service_checks", None):
        cmdline_options.append("-d")

    if config_install_options.get("cloud", None):
        cmdline_options.append("-L")

    if config_install_options.get("master", None):
        cmdline_options.append("-M")

    if config_install_options.get("syndic", None):
        cmdline_options.append("-S")

    if config_install_options.get("api", None):
        cmdline_options.append("-W")

    if not config_install_options.get("minion", False):
        cmdline_options.append("-N")

    server.shell(
        name="Execute bootstrap-salt.sh",
        commands=[
            " ".join(
                ["/usr/local/bin/bootstrap-salt.sh"]
                + cmdline_options
                + [host.data.get("install_type", "stable")]
                + [host.data.get("salt_version", "3006.9")]
            )
        ],
        _sudo=True,
    )
