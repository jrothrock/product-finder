# Item finder.

Finds whether a certain item on Aliexpress or Alibaba can be sold on Amazon profitably. Use ahrefs to calculate whether there is significant search volume if in niche area

# Design

## Deploying.

Terraform is set up to create a digitalocean droplet, firewalls, and updating the dns records. Additionally, cloud-init
is used to provision the server and install both docker and docker-compose - see provision.sh.

1. Change into the terraform directory and run `terraform apply` which will create the infrastructure - will ask for DO token.
After this has been completed, it takes another 2-3 minutes for cloud-init to complete the provision process.

2. Run `terraform output droplet_ipv4 > ./../.host`. This will create a .host file in the root of the directory which is used by
the deploy script.

3. Run the `./.deploy` script. This will create a new directory on the server, rsync over the files (may want to switch to a deploy key),
stop prior docker containers, start the new ones, and delete the oldest deploy directory if there are more than 5.
