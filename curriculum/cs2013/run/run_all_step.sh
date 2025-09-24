#!/bin/bash

pushd curriculum/data/ || exit 1
bash curriculum/data/ka_pdf_to_txt.sh
popd || exit 1

export PYTHONPATH=curriculum/
export DATADIR=curriculum/data/
bash curriculum/data/ka_txt_to_json.sh
bash curriculum/data/ka_json_to_csv.sh
python curriculum/data/combine_csv.py
python curriculum/data/add_mapping.py
