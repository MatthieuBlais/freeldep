#!/bin/bash

export CODEBUILD_GIT_BRANCH=`git symbolic-ref HEAD --short 2>/dev/null`
if [ "$CODEBUILD_GIT_BRANCH" == "" ] ; then
  CODEBUILD_GIT_BRANCH=`git branch -a --contains HEAD | sed -n 2p | awk '{ printf $1 }'`
  export CODEBUILD_GIT_BRANCH=${CODEBUILD_GIT_BRANCH#remotes/origin/}
fi

echo $CODEBUILD_GIT_BRANCH;

if [ -f ./bin/package.sh ];
then
  /bin/bash ./bin/package.sh;
fi

if [ -f ./config.yaml ];
then
  python3 main.py;
fi
