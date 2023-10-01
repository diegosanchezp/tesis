#!/bin/bash

# This script is used for the deploy

[ "$SSH_KEY" = "" ] && echo "Error SSH_KEY not set" && exit 1
[ "$SSH_HOST" = "" ] && echo "Error SSH_HOST not set" && exit 1
[ "$SSH_USER" = "" ] && echo "Error SSH_USER not set" && exit 1

mkdir -p ~/.ssh/
echo "$SSH_KEY" > ~/.ssh/production.key
chmod 600 ~/.ssh/production.key
cat >>~/.ssh/config <<END
Host production
HostName $SSH_HOST
User $SSH_USER
IdentityFile ~/.ssh/production.key
StrictHostKeyChecking no
END
