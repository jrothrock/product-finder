FROM certbot:v1.8.0

# # Add HTTP basic auth
# RUN apt-get update
# RUN apt-get install apache2-utils -y
# RUN htpasswd -cb /etc/nginx/.htpasswd finder 1TeMpPaSsWoRd1

# # Copy over Nginx configurations
# RUN rm /etc/nginx/conf.d/default.conf
# COPY nginx.conf /etc/nginx/conf.d

# # Install letsencrypt
RUN certbot certonly -n --webroot --webroot-path /var/www/certbot/ --agree-tos -d finder.jackrothrock.com  -m  jrothrock14@gmail.com
