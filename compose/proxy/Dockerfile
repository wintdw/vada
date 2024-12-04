# SPDX-FileCopyrightText: Copyright 2022, Arquivei
# SPDX-License-Identifier: BSD-3-Clause

# from-source: https://github.com/mordaha/docker-nginx-vts/blob/master/Dockerfile
# unpriviledged: https://github.com/nginxinc/docker-nginx-unprivileged/blob/main/stable/alpine-slim/Dockerfile

ARG NGINX_VERSION="1.27"
FROM nginx:${NGINX_VERSION}

ENV NGINX_VTS_VERSION "0.2.2"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y gnupg2 dpkg-dev --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives \
  && curl http://nginx.org/packages/keys/nginx_signing.key | apt-key add -

RUN mkdir -p /opt/rebuildnginx && chmod 0777 /opt/rebuildnginx
WORKDIR /opt/rebuildnginx

RUN echo "deb-src http://nginx.org/packages/debian/ bullseye nginx" >> /etc/apt/sources.list \
  && apt-get update \
  && su --preserve-environment -s /bin/bash -c "apt-get source nginx=${NGINX_VERSION}" _apt \
  && apt-get build-dep -y nginx="${NGINX_VERSION}" \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives

WORKDIR /opt

RUN curl -sL "https://github.com/vozlt/nginx-module-vts/archive/v${NGINX_VTS_VERSION}.tar.gz" | tar -xz -C /opt \
  && sed -i -r -e "s/\.\/configure(.*)/.\/configure\1 --add-module=\/opt\/nginx-module-vts-${NGINX_VTS_VERSION}/" "/opt/rebuildnginx/nginx-${NGINX_VERSION}/debian/rules"
  
WORKDIR /opt/rebuildnginx/nginx-${NGINX_VERSION} 
RUN dpkg-buildpackage -b 

WORKDIR /opt/rebuildnginx 
RUN dpkg --install nginx_"${NGINX_VERSION}-1~bullseye_amd64.deb" \
  && apt-get remove --purge -y dpkg-dev && apt-get -y --purge autoremove && rm -rf /var/lib/apt/lists/*

RUN rm -Rf /opt/rebuildnginx 

WORKDIR /opt

#implement changes required to run NGINX as an unprivileged user
#hadolint ignore=SC3028
RUN sed -i '/user  nginx;/d' /etc/nginx/nginx.conf \
    && sed -i 's,/var/run/nginx.pid,/tmp/nginx.pid,' /etc/nginx/nginx.conf \
    && sed -i "/^http {/a \    vhost_traffic_status_zone;\n    proxy_temp_path /tmp/proxy_temp;\n    client_body_temp_path /tmp/client_temp;\n    fastcgi_temp_path /tmp/fastcgi_temp;\n    uwsgi_temp_path /tmp/uwsgi_temp;\n    scgi_temp_path /tmp/scgi_temp;\n" /etc/nginx/nginx.conf \
# nginx user must own the cache and etc directory to write cache and tweak the nginx config
    && chown -R $UID:0 /var/cache/nginx \
    && chmod -R g+w /var/cache/nginx \
    && chown -R $UID:0 /etc/nginx \
    && chmod -R g+w /etc/nginx