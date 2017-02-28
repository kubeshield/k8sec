FROM appscode/node:argon

ENV HIDS_VER 1.1.1
ENV API_VER 1.2.1

# Update repositories, install git, gcc, wget, make and java8 and
# clone down the latest OSSEC build from the official Github repo.

RUN set -x \
  && apt-get update \
  && apt-get install --no-install-recommends -y ca-certificates curl gcc make libssl-dev

RUN set -x && cd root && mkdir ossec_tmp && cd ossec_tmp

# Copy the unattended installation config file from the build context
# and put it where the OSSEC install script can find it. Then copy the
# process. Then run the install script, which will turn on just about
# everything except e-mail notifications

## Para cuando se publique
RUN set -x \
  && curl -fSOL https://github.com/wazuh/ossec-wazuh/archive/v$HIDS_VER.tar.gz \
  && tar xzf v$HIDS_VER.tar.gz \
  && mv ossec-wazuh-$HIDS_VER /root/ossec_tmp/ossec-wazuh \
  && rm v$HIDS_VER.tar.gz
#ADD ossec-wazuh /root/ossec_tmp/ossec-wazuh
COPY preloaded-vars.conf /root/ossec_tmp/ossec-wazuh/etc/preloaded-vars.conf

RUN /root/ossec_tmp/ossec-wazuh/install.sh

# Forked wazuh-api to correctly pass the ca.crt of the k8s cluster
# https://github.com/appscode/wazuh-API/commit/ddf951acdefbedea996670c49e694b94482f42ef
RUN set -x \
  && mkdir -p /var/ossec/api \
  && cd /var/ossec/api \
  && curl -fSOL https://github.com/appscode/wazuh-API/archive/v${API_VER}-ac.tar.gz \
  && tar xzf v${API_VER}-ac.tar.gz --strip-component=1 \
  && rm -rf v${API_VER}-ac.tar.gz

RUN set -x \
  && apt-get purge -y --auto-remove ca-certificates gcc make \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man /tmp/*

# Set persistent volumes for the /etc and /log folders so that the logs
# and agent keys survive a start/stop and expose ports for the
# server/client ommunication (1514) and the syslog transport (514)

COPY default_agent /var/ossec/default_agent
RUN set -x \
  && service ossec restart \
  && /var/ossec/bin/manage_agents -f /default_agent \
  && rm /var/ossec/default_agent \
  && service ossec stop \
  && echo -n "" /var/ossec/logs/ossec.log

COPY data_dirs.env /data_dirs.env
COPY init.bash /init.bash
# Sync calls are due to https://github.com/docker/docker/issues/9547
RUN set -x \
  && chmod 755 /init.bash \
  && sync && /init.bash \
  && sync && rm /init.bash

COPY run.sh /tmp/run.sh
RUN set -x && chmod 755 /tmp/run.sh

RUN set -x && mkdir -p /var/ossec/data

# Run supervisord so that the container will stay alive
ENTRYPOINT ["/tmp/run.sh"]
EXPOSE 55000/tcp 1514/udp 1515/tcp 515/udp
