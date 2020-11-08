# import json
# import os
# import uuid
# import boto3
# from utils import BadTemplateException  # pylint: disable=import-error
# # import cfnlint.core
# print("sdfsdf")
# s3 = boto3.client("s3", region_name=os.environ["AWS_REGION"])
# print("sdfsdf")
# def parse_s3_url(s3_url):
#     url = s3_url.split("/")
#     return url[2], "/".join(url[3:])
# def download_template(s3, bucket, key):
#     try:
#         filename = f"/tmp/{uuid.uuid1().hex}.yaml"
#         s3.download_file(bucket, key, filename)
#         return filename
#     except Exception:
#         raise
# # def run_checks(template_name):
# #     template = cfnlint.decode.cfn_yaml.load(template_name)
# #     cfnlint.core.configure_logging(None)
# #     rules = cfnlint.core.get_rules([], [], [], [], False, [])
# #     return cfnlint.core.run_checks(
# #         template_name, template, rules, [os.environ["AWS_REGION"]]
# #     )
# def handler(event, context):
#     print(json.dumps(event, indent=4))
#     event["Valid"] = True
#     # bucket, key = parse_s3_url(event["TemplateLocation"])
#     # filename = download_template(s3, bucket, key)
#     # checks = run_checks(filename)
#     # event["Valid"] = len(checks) == 0
#     # if len(checks) > 0:
#     #     for err in checks:
#     #         print(err)
#     #     event["Error"] = {"Code": "BadTemplateException", "Cause": checks}
#     #     raise BadTemplateException(json.dumps(event["Error"]))
#     return event
