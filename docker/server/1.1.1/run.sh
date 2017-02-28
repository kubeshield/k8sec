#!/bin/bash

source /data_dirs.env
DATA_PATH=/var/ossec/data

for ossecdir in "${DATA_DIRS[@]}"; do
  if [ ! -e "${DATA_PATH}/${ossecdir}" ]
  then
    echo "Installing ${ossecdir}"
    cp -pr /var/ossec/${ossecdir}-template ${DATA_PATH}/${ossecdir}
  fi
done

touch ${DATA_PATH}/process_list
chgrp ossec ${DATA_PATH}/process_list
chmod g+rw ${DATA_PATH}/process_list

function ossec_shutdown(){
  /var/ossec/bin/ossec-control stop;
}

# Trap exit signals and do a proper shutdown
trap "ossec_shutdown; exit" SIGINT SIGTERM

chmod -R g+rw ${DATA_PATH}

LAST_OK_DATE=`date +%s`

cd /root/ossec_tmp/ossec-wazuh/extensions/elasticsearch/
curl -XPUT "http://elasticsearch-logging:9200/_template/ossec/" -d "@elastic-ossec-template.json" || true

/usr/local/bin/node /var/ossec/api/app.js > /var/ossec/logs/api.log &

service ossec restart


tail -f /var/ossec/logs/ossec.log
