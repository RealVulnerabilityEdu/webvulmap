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

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/parse_ka.py --data_dir=${DATADIR} \
        "Software Development Fundamentals" \
        "SDF" \
        "cs2013_web_final_sdf.txt"\
        "cs2013_web_final_sdf.json"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/parse_ka.py --data_dir=${DATADIR} \
    "Information Management"\
    "IM"\
    "cs2013_web_final_im.txt"\
    "cs2013_web_final_im.json"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/parse_ka.py --data_dir=${DATADIR} \
        "Information Assurance and Security" \
        "IAS" \
        "cs2013_web_final_ias.txt"\
        "cs2013_web_final_ias.json"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/parse_ka.py --data_dir=${DATADIR} \
    "Programming Languages"\
    "PL"\
    "cs2013_web_final_pl.txt"\
    "cs2013_web_final_pl.json"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/parse_ka.py --data_dir=${DATADIR} \
    "Software Engineering"\
    "SE"\
    "cs2013_web_final_se.txt"\
    "cs2013_web_final_se.json"

PYTHONPATH=${PYTHONPATH} python ${PYTHONPATH}/parse_ka.py --data_dir=${DATADIR} \
    "Systems Fundamentals"\
    "SF"\
    "cs2013_web_final_sf.txt"\
    "cs2013_web_final_sf.json"