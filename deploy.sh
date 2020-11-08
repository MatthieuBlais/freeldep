#!/bin/bash

cd ./compiler/deployer/
rm -f deployer.zip
zip -r9 deployer.zip . -x \*.git\* -x \*.pyc\* -x \*__pycache__\*

mkdir ./packages
pip3 install -r requirements.txt --target packages
cd packages
zip -g -r ../deployer.zip .
cd ..
rm -rf packages

cd ../..
python compiler/main.py
