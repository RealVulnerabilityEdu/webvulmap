#!/bin/bash

if ! -f cs2013_web_final.pdf; then
    wget http://www.sci.brooklyn.cuny.edu/~chen/uploads/research/cscurriculum/cs2013_web_final.pdf -O cs2013_web_final.pdf
fi

pdftotext -layout -raw -f 58 -l 64  cs2013_web_final.pdf cs2013_web_final_al.txt
pdftotext -layout -raw -f 65 -l 70  cs2013_web_final.pdf cs2013_web_final_ar.txt
pdftotext -layout -raw -f 100 -l 114  cs2013_web_final.pdf cs2013_web_final_ias.txt
pdftotext -layout -raw -f 100 -l 114  cs2013_web_final.pdf cs2013_web_final_ias.txt
pdftotext -layout -raw -f 115 -l 123  cs2013_web_final.pdf cs2013_web_final_im.txt
pdftotext -layout -raw -f 158 -l 169  cs2013_web_final.pdf cs2013_web_final_pl.txt
pdftotext -layout -raw -f 170 -l 174  cs2013_web_final.pdf cs2013_web_final_sdf.txt
pdftotext -layout -raw -f 175 -l 188  cs2013_web_final.pdf cs2013_web_final_se.txt
pdftotext -layout -raw -f 189 -l 194  cs2013_web_final.pdf cs2013_web_final_sf.txt
pdftotext -layout -raw -f 195 -l 206  cs2013_web_final.pdf cs2013_web_final_sp.txt
