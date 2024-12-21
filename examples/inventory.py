"""
Inventory file for the pyinfra_salt example deploy.py
"""
import copy


# Define defaults to use for the defployment.
DEFAULTS = {
    "ssh_user": "tkcadmin",
    "ssh_key": "~/.ssh/id_ed25519",
    "install_type": "stable",  # testing, git, onedir, onedir_rc
    "salt_version": "3006.9",
    "options": {
        "master_fqdn": "salt.local",  # -A Set master DNS name or IP
        "debug:": False,  # -D Show debug output
        "no_colors": False,  # -n No colours
        "post_install_start": False,  # -X Do not start daemons after installation
        "disable_service_checks": False,  # -d Disable checking enabled services
        "install": {
            "cloud": False,  # -L Also install salt-cloud and required python-libcloud package
            "master": False,  # -M Also install salt-master
            "syndic": False,  # -S Also install salt-syndic
            "api": False,  # -W Also install salt-api
            "minion": True,  # -N Do not install salt-minion
        },
    },
}


def deep_merge(defaults, overrides):
    """
    Merge two dictionaries of dictionaries.
    """
    for key, value in defaults.items():
        if key in overrides:
            if isinstance(value, dict) and isinstance(overrides[key], dict):
                deep_merge(value, overrides[key])
            else:
                defaults[key] = overrides[key]

    return defaults



# Hosts to run the bootstrap-salt.sh script on
deploy_targets = [
    (
        "salt-ssh.local",
        deep_merge(
            copy.deepcopy(DEFAULTS),
            {
                "ssh_user": "crow",
                "options": {"master_fqdn": "127.0.0.1", "install": {"master": True, "api": True}},
            },
        ),
    ),
    ("target01.tkclabs.io", deep_merge(copy.deepcopy(DEFAULTS), {})),
]
