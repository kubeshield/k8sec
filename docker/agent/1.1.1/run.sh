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

# Block until registered
while :
do
  python2 register.py
  OUT=$?
  if [ $OUT -eq 0 ];then
    break
  fi
done

service ossec restart

tail -f /var/ossec/logs/ossec.log
