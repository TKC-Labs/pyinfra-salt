# pyinfra code for TKC Labs

This repository contains code related to pyinfra deployments and management in TKC Labs

## Preparation

Get pyinfra via virtualenv

```bash
# Create Python Virtual Environment
python3 -m venv path/to/venvs/pyinfra

# Activate it
source path/to/venvs/pyinfra/bin/activate

# Update pip in the virutal environment
pip install --upgrade pip

# Install pyinfra in the virtual environment
pip install pyinfa
```

## Usage

### Adhoc commands

Commands run like `pyinfra INVENTORY OPERATIONS`

```bash
# Execute over SSH
pyinfra my-server.net exec -- echo "hello world"

# Execute within a new docker container
pyinfra @docker/ubuntu:18.04 exec -- echo "hello world"

# Execute on the local machine (MacOS/Linux only - for now)
pyinfra @local exec -- echo "hello world"
```

### Deploys

The examples directory holds a deployment that I use directly from the repo to deploy Salt for local testing.

First, adjust `inventory.py` to match the hostnames you want to deploy salt on and then adjust the options for each master or minion in the `deploy_targets` list.

Then, run the deployment.

This deployment assumes the SSH user will have an active public key in the `~/.ssh/authorized_keys` for passwordless SSH access to the target machines.

It is also assumed that the user being used for SSH access will have passwordless `sudo` on the target machines.

````bash
# Run the deploy to download and execute the bootstrap-salt.sh script on the
# hosts defined in inventory.py
pyinfra inventory.py deploy.py
````
