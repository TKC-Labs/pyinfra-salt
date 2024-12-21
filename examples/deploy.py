"""
Deploy Salt services using the bootstrap-salt.sh script.

This script will download the latest salt-bootstrap.sh script from the SaltStack GitHub
"""

from pyinfra import host
from pyinfra.facts.files import File, Directory
from pyinfra_salt.salt import (bootstrap_salt, download_salt_bootstrap_script)

# Download the latest salt-bootstrap.sh script if it is not present
if not host.get_fact(File, path="/usr/local/bin/bootstrap-salt.sh"):
    download_salt_bootstrap_script()

# Run the bootstrap script if the salt config directory is not present
if not host.get_fact(Directory, path="/etc/salt"):
    bootstrap_salt()
