# Mentorship social network

This repository contains the source code of the web app for the mentorship social network, all of the current work can be tracked in a board located on [Github Projects](https://github.com/diegosanchezp/tesis/projects).

# Setup development environment

## Install system dependencies
These system dependencies are required, **Linux OS** is preferred.

| System dependency | Version | Usage                   |
|-------------------|---------|-------------------------|
| bash              | >= 5    | Setup scripts           |
| docker            | >= 24   | Build images            |
| docker-compose    | >= 2    | Development environment |

## Docker config
Docker has to be able run as a non root user, for more info check

[Post-installation steps for Linux | Docker Documentation](https://docs.docker.com/engine/install/linux-postinstall/)

## Initial Setup

If you are using Linux, put this into your bashrc `.bashrc` OR `.zhsrc`, it's needed for the file permissions.

```bash
export UID=$(id -u)
export GID=$(id -g)
```

Run the command below, to setup the development environment

```bash
bash ./shscripts/setup_dev.sh
```

Add HTTPS certificate `mkcert/rootCA.pem` to your browser, please visit these webpages for the steps.

- [Add a Root Certificate in Mozilla Firefox](https://docs.vmware.com/en/VMware-Adapter-for-SAP-Landscape-Management/2.1.0/Installation-and-Administration-Guide-for-VLA-Administrators/GUID-0CED691F-79D3-43A4-B90D-CD97650C13A0.html)

- [Add a Root Certificate in Google Chrome](https://docs.vmware.com/en/VMware-Adapter-for-SAP-Landscape-Management/2.1.0/Installation-and-Administration-Guide-for-VLA-Administrators/GUID-D60F08AD-6E54-4959-A272-458D08B8B038.html)

Load development command utilities with

```bash
source shscripts/dev.sh
```

Activate the server, to test if everything has worked.

```bash
runserver
```

Visit `https://127.0.0.1:8000` in your web browser.

# Development
It is recommend to check the commands of `shscripts/dev.sh` as it has a ton of useful commands.

If you want to source the commands

```bash
source shscripts/dev.sh
```

# Deployment

- CI/CD is currently made with Github Actions and it is docker based.
- If you don't want a specific action it can be [disabled](https://docs.github.com/en/actions/managing-workflow-runs/disabling-and-enabling-a-workflow).
