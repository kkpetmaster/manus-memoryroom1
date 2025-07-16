FROM nginx:latest
COPY ./conf/default.conf /etc/nginx/conf.d/default.conf
COPY ./ssl /etc/nginx/ssl
EXPOSE 80 443

