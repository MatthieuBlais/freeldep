import os
import subprocess


class CodebuildHelper:

    BRANCH_EXTRACT_SCRIPT = """
        export CODEBUILD_GIT_BRANCH=`git symbolic-ref HEAD --short 2>/dev/null`
        if [ "$CODEBUILD_GIT_BRANCH" == "" ] ; then
            CODEBUILD_GIT_BRANCH=`git branch -a --contains HEAD | sed -n 2p | awk '{ printf $1 }'`
            export CODEBUILD_GIT_BRANCH=${CODEBUILD_GIT_BRANCH#remotes/origin/}
        fi
        echo $CODEBUILD_GIT_BRANCH;
    """

    @classmethod
    def is_codebuild(cls):
        return os.environ.get("CODEBUILD_SOURCE_REPO_URL", "") != ""

    @classmethod
    def get_project(cls):
        return os.environ["CODEBUILD_SOURCE_REPO_URL"].split("/")[-1]

    @classmethod
    def get_branch(cls):
        return subprocess.getoutput(cls.BRANCH_EXTRACT_SCRIPT)
