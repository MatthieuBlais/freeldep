#!/bin/bash

export CODEBUILD_GIT_BRANCH=`git symbolic-ref HEAD --short 2>/dev/null`
if [ "$CODEBUILD_GIT_BRANCH" == "" ] ; then
  CODEBUILD_GIT_BRANCH=`git branch -a --contains HEAD | sed -n 2p | awk '{ printf $1 }'`
  export CODEBUILD_GIT_BRANCH=${CODEBUILD_GIT_BRANCH#remotes/origin/}
fi

echo $CODEBUILD_GIT_BRANCH;

aws s3 cp . s3://$ARTIFACTS_BUCKET/$CODEBUILD_GIT_BRANCH/deployer/ --recursive --exclude "*" --include "*.yaml" --include "*.py" --include "*.sh"


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

python3 compiler/service/main.py
