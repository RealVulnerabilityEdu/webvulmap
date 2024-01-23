#!/bin/bash

if [ -z ${PYTHONPATH+x} ];
then
    echo "PYTHONPATH is unset";
    exit 1
else
    echo "PYTHONPATH is set to '${PYTHONPATH}'";
fi

if [ -z ${DATADIR+x} ];
then
    echo "DATADIR is unset";
    exit 1
else
    echo "DATADIR is set to '${DATADIR}'";
fi

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/flatten_ka.py --data_dir=${DATADIR} \
        "cs2013_web_final_sdf.json" \
        "cs2013_web_final_sdf.csv"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/flatten_ka.py --data_dir=${DATADIR} \
        "cs2013_web_final_im.json" \
        "cs2013_web_final_im.csv"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/flatten_ka.py --data_dir=${DATADIR} \
        "cs2013_web_final_ias.json" \
        "cs2013_web_final_ias.csv"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/flatten_ka.py --data_dir=${DATADIR} \
    "cs2013_web_final_pl.json" \
    "cs2013_web_final_pl.csv"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/flatten_ka.py --data_dir=${DATADIR} \
    "cs2013_web_final_se.json" \
    "cs2013_web_final_se.csv" 

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/flatten_ka.py --data_dir=${DATADIR} \
    "cs2013_web_final_sf.json" \
    "cs2013_web_final_sf.csv"
