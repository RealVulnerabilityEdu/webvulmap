#!/bin/bash
pushd curriculum/data/
    bash curriculum/data/ka_pdf_to_txt.sh
popd

PYTHONPATH=curriculum/ DATADIR=curriculum/data/ bash curriculum/data/ka_txt_to_json.sh
PYTHONPATH=curriculum/ DATADIR=curriculum/data/ bash curriculum/data/ka_json_to_csv.sh
PYTHONPATH=curriculum/ DATADIR=curriculum/data/ python curriculum/data/combine_csv.py
PYTHONPATH=curriculum/ DATADIR=curriculum/data/ python curriculum/data/add_mapping.py
