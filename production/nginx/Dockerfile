FROM nginx:1.21.6

# Add HTTP basic auth
RUN apt-get update
RUN apt-get install apache2-utils -y
RUN htpasswd -cb /etc/nginx/.htpasswd finder 1TeMpPaSsWoRd1

# Copy over Nginx configurations
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

