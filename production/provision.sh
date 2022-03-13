#!/bin/bash
# Used via cloud-init in terraform/modules/digitalocean_droplet/main.tf

# Update packages, and install fail2ban
echo "UPDATING PACKAGES"
apt-get update -y
# TODO: investigate getting through post upgrade interactivity from ssh-server.
# apt-get upgrade -y

echo "INSTALLING FAIL2BAN"
apt-get install fail2ban -y

# Create finder and deploy user, then add them to sudo without requiring password. 
# Flags will disable password and iteractive form
echo "ADDING USERS"
adduser --disabled-password --gecos "" finder
adduser --disabled-password --gecos "" deploy
usermod -aG sudo finder
usermod -aG sudo deploy
echo 'finder ALL=(ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo
echo 'deploy ALL=(ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo

# Copy over ssh keys
echo "COPYING KEYS"
install -d -m 0700 -o finder -g finder /home/finder/.ssh
head -1 /root/.ssh/authorized_keys >> /home/finder/.ssh/authorized_keys
install -d -m 0700 -o deploy -g deploy /home/deploy/.ssh
tail -1 /root/.ssh/authorized_keys >> /home/deploy/.ssh/authorized_keys

# Disable Root login
echo "UPDATING SSH SERVICE"
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
service ssh restart

# Add docker and docker-compose
echo "ADDING DOCKER AND DOCKER-COMPOSE"
apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
apt update
apt install docker-ce -y

usermod -aG docker finder
usermod -aG docker deploy

curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add Haveged to help with low entropy situations and hanging of docker-compose
echo "ADDING HAVEGED"
apt install haveged
