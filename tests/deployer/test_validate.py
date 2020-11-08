import pytest



event = {
        "TemplateName": "smlf-dataengineering-cfn-deployer-service",
        "TemplateLocation": "s3://smlf-dataengineering-deployer-artifact-bucket//templates/smlf-dataengineering-cfn-deployer-service/20201102_1633_2518c3da1d2911eb89e30242ac110002.yaml",
        "Action": "CREATE_OR_UPDATE_STACK",
        "Test": False,
        "NotifyOnFailure": "",
        "Parameters": {
            "DeployerCodebuildServiceName": "smlf-dataengineering-template-deployer-service",
            "DeployerArtifactBucket": "smlf-dataengineering-deployer-artifact-bucket",
            "DeployerStateArn": "arn:aws:states:ap-southeast-1:908177370303:stateMachine:smlf-dataengineering-cfn-deployer",
            "DeployerTriggerLambdaName": "smlf-dataengineering-deployer-trigger-service"
        }
    }
    