FROM docker.elastic.co/elasticsearch/elasticsearch:8.10.4
COPY analytics_plugin-1.3.ES.8.10.4.zip /tmp/analytics_plugin-1.3.ES.8.10.4.zip
RUN bin/elasticsearch-plugin install file:///tmp/analytics_plugin-1.3.ES.8.10.4.zip