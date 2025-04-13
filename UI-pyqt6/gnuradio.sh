#!/bin/bash

set -e
ARG="$1"

source "/home/starrloc/miniconda3/etc/profile.d/conda.sh"
conda activate base

python3 "/home/starrloc/Documents/STARR-LOC/radio/GNU Radio/Autocorrelation Voice Squelch/HAM/fm_rx.py" "$ARG"