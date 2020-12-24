# Freeldep: Infra-as-code deployment

[![Build Status](https://travis-ci.com/MatthieuBlais/freeldep.svg?branch=main)](https://travis-ci.com/MatthieuBlais/freeldep) [![Coverage Status](https://coveralls.io/repos/github/MatthieuBlais/freeldep/badge.svg?branch=main)](https://coveralls.io/github/MatthieuBlais/freeldep?branch=main)

Infrastructure-as-code increase speed of setting up and maintaining IT environment. If you are using AWS and Cloudformation, Freeldep helps to version control your templates and test your infrastructure. It integrates with CodeCommit, CodeBuild and Step Function to deploy your infrastructure and use taskcat to test your templates. Freeldep also helps you quickly setting up this CI/CD pipeline.

## Architecture



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You must have AWS access on your machine. If not, configure your credentials using

```
aws configure
```

Install freeldep

```
virtualenv venv
source venv/bin/activate
pip install freeldep
```

### Installing

All these commands can be executed with the flags **--dryrun** and **--output-location <foldername>** if you don't want to deploy anything.

First step is to create a new deployer:

```
freeldep create deployer mydemo --cloud AWS
```

Replace mydemo by the name of your deployer. This command will create a S3 bucket used to store deployment artifacts and a dynamoDB table to keep track of the deployments. You can specify resource names using:

```
freeldep create deployer mydemo --cloud AWS --artifact-bucket <bucket> --registry-table <registry>
```

Currently, AWS cloud is the only stable cloud supported. There is work in progress to support GCP.


Deploy the core deployer Step Function:

```
freeldep deploy core --deployer mydemo --wait
```

Deploy the service to configure CI/CD for your projects:

```
freeldep deploy service --deployer mydemo --wait
```

More options for CLI can be found [here](cli/README.md) file for details

## Creating a new project using your deployment service


```
freeldep create myproject --deployer mydemo
```

This command creates a new CodeCommit repository and configure a trigger on each git push. If you want to limit the branches triggering deployment, use:

```
freeldep create myproject --deployer mydemo --branches dev,uat,master
```

## Development and running the tests

Clone this repository and install dependencies. Setup your CLI:

```
pip install --editable .
```

Tests can be executed using pytest and coverage:

```
coverage run -m pytest tests/ && coverage report -m
```
