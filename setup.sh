#!/bin/bash
    cd api/
    git clone https://github.com/Lu-Yi-Hsun/iqoptionapi.git
    cd iqoptionapi/
    python setup.py install
    cd ../../
    pip install -r requirements.txt
