FROM nginx:1.27-alpine

#RUN rm /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/conf.d/default.conf && mkdir -p /etc/nginx/sites-enabled && printf 'include /etc/nginx/sites-enabled/*.conf;\n' > /etc/nginx/conf.d/zz-sites-enabled.conf

COPY sites-enabled/*.conf /etc/nginx/sites-enabled/ 
#ADD sites-enabled/ /etc/nginx/sites-enabled
