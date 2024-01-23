#!/bin/bash

if ! -f cs2013_web_final.pdf; then
    wget https://www.acm.org/binaries/content/assets/education/cs2013_web_final.pdf -O cs2013_web_final.pdf
fi

pdftotext -layout -raw -f 100 -l 114  cs2013_web_final.pdf cs2013_web_final_ias.txt
pdftotext -layout -raw -f 158 -l 169  cs2013_web_final.pdf cs2013_web_final_pl.txt
pdftotext -layout -raw -f 170 -l 174  cs2013_web_final.pdf cs2013_web_final_sdf.txt
pdftotext -layout -raw -f 175 -l 188  cs2013_web_final.pdf cs2013_web_final_se.txt
pdftotext -layout -raw -f 189 -l 194  cs2013_web_final.pdf cs2013_web_final_sf.txt
