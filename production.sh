#!/bin/bash
# Used via cloud-init in terraform/modules/digitalocean_droplet/main.tf

# Update packages, and install fail2ban
echo "UPDATING PACKAGES"
apt-get update -y
# TODO: investigate getting through post upgrade interactivity from ssh-server.
# apt-get upgrade -y

echo "INSTALLING FAIL2BAN"
apt-get install fail2ban -y

# Create finder and deploy user, then add them to sudo. 
# Flags will disable password and iteractive form
echo "ADDING USERS"
adduser --disabled-password --gecos "" finder
adduser --disabled-password --gecos "" deploy
usermod -aG sudo finder
usermod -aG sudo deploy

# Copy over ssh keys
echo "COPYING KEYS"
install -d -m 0700 -o finder -g finder /home/finder/.ssh
head -1 /root/.ssh/authorized_keys >> /home/finder/.ssh/authorized_keys
install -d -m 0700 -o deploy -g deploy /home/deploy/.ssh
tail -1 /root/.ssh/authorized_keys >> /home/deploy/.ssh/authorized_keys

echo "UPDATING SSH SERVICE"
# Disable Root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
service ssh restart
