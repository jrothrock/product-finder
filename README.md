# Item finder

Looks for retail arbitrage via scraping aliexpress and amazon looking for both arbitrage in the item itself, but more importantly, potentially finding arbitrage within categories.

Right now the category titles are generated by looking at the nouns and pronouns of the scraped item title on aliexpress.

Having scraped 1,000s of items and categories I'll say that improving this would be very helpful.

One way of doing this is by adding the top one or two adjectives to the title (using TFIDF on the description + title), then adding it
to the pronouns and nouns. For example, "red stuffed elephant" is quite different than "elephant".

There is a titling version column on the category record for this reason.

# Design
The more I've progressed through this project, the more I dislike how I did/wrote things. 

However, to give fairness to myself, this first started as a few scripts using SQLAlchemy writing to a sqlite database.

**Things that for sure need to be improved:**

While there are many things that need to be improved, here are a few that are pretty big takeaways from this:

First off, using a RDBMS was the wrong move. I only have two tables in a predominantly write heavy workload. I probably should have gone with Cassandra.

Secondly, having higher test coverage. This is hard to do given the nature of scraping, as there are known exceptions that do occur under certain scenarios.

## Local

There are two ways that this app can be run:

### Virtualenv
Requires python 3.10, firefox being installed locally, as well a local running redis server. 
Records will be saved in a sqlite database in the `./database` directory.

To start the application:
1. `pip3 install poetry`
2. `poetry install`
3. `poetry run start`
4. `celery -A tasks worker -l info`

### Docker
Requires both docker and docker-compose. Records will be stored in postgreSQL.
1. `docker-compose up -d --force-recreate`

### Testing
Some tests have been marked to be skipped as full mocking for them hasn't been completed.

To run these tests alongside the rest of the test suite (will require a local redis-server running):

`python -m pytest --no-skips`

## Production

Due to wanting to keep costs low and for simplicity sake, I've decided to use docker-compose in production.

### Deploying

Terraform is set up to create a digitalocean droplet, firewalls, and updating the dns records. Additionally, cloud-init
is used to provision the server and install both docker and docker-compose - see provision.sh.

1. Change into the terraform directory and run `terraform apply` which will create the infrastructure - will ask for DO token.
After this has been completed, it takes another 2-3 minutes for cloud-init to complete the provision process.

2. Run `terraform output droplet_ipv4 > ./../production/.host`. This will create a .host file in the production directory which is used by
the deploy script.

3. Run the `./production/deploy.sh` script. This will create a new directory on the server, rsync over the files (may want to switch to a deploy key),
stop prior docker containers, start the new ones, and delete the oldest deploy directory if there are more than 5.

#### Note
There is an issue on first deploy where nginx will fail to start as it is unable to find the ssl certs. The current work around is to comment out the ssl
server section, have certbot create the certificates, then uncomment and redeploy. A long term solution is to generate fake ssl certs so that nginx will
start up, then have certbot create the actual ones.

This uses `s-2vcpu-2gb` - a $15 droplet. It's pretty much not possible to run this on a lower resource droplet.

### Useful commands
* Latest deploy directory: 

`cd deploys/current;`

* List docker containers:

`docker ps`

* Get logs from a container:

`docker-compose -f ~/deploys/current/production/docker-compose.production.yml logs --tail 250 celery`

* Access the shell of a container (note, cache/redis uses Alpine which doesn't have bash and will need `/bin/sh`)

`docker-compose -f ~/deploys/current/production/docker-compose.production.yml exec web /bin/bash`
