FROM nginxinc/nginx-unprivileged@sha256:c97ff0bf7cbae369953c6da1232ec14ad9f971d66360c5698db0856a4cd657a0
COPY state/runtime /usr/share/nginx/runtime
COPY state/preview /usr/share/nginx/preview
COPY club/vendor /usr/share/nginx/vendor
COPY club/nginx.conf /etc/nginx/nginx.conf
USER 101:101
ENTRYPOINT ["nginx", "-g", "daemon off;"]
