#!/bin/bash
CURRENT_TIME=$(date '+%s')
DROPLET_IP=`cat ./.host | tr -d '"'`

# This assumes the ssh key is added and the host is known.
ssh deploy@$DROPLET_IP "mkdir -p ~/deploys/$CURRENT_TIME"

# Copy current code to application -- may want to update to using a deploy key.
rsync -avz --exclude=.venv --exclude=terraform/.terraform ./ deploy@$DROPLET_IP:~/deploys/$CURRENT_TIME/

# Stop all previous docker containers.
ssh deploy@$DROPLET_IP "docker stop $(docker ps -q)"

# Start docker containers.
ssh deploy@$DROPLET_IP "cd ~/deploys/$CURRENT_TIME/; docker-compose up -d"

# Remove the oldest directory if there are more than 5.
ssh deploy@$DROPLET_IP 'cd deploys; if [[ $(ls | wc -l) -gt 5 ]]; then rm -rf $(ls -t1 | tail -n 1); fi'
