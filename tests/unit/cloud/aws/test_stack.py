# from cli.cloud.aws.stack import CfnStack
# def read_template(self):
#     """Read CFN template as text file"""
#     with open(self.config['location'], "r") as stream:
#         self.template = stream.read()
# def prepare_packages(self):
#     """Prepare lambda packages and update stack parameters"""
#     for idx, lambd in enumerate(self.config['lambdas']):
#         uname = datetime.now().strftime(
#             lambd["name"] + "_" + "%Y%m%d_%H%M_" + uuid.uuid1().hex + ".zip"
#         )
#         self.config['template'][lambd["template-attribute"]] = (
#             self.config['template'][lambd["template-attribute"]] + uname
#         )
#         self.config['lambdas'][idx]["filename"] = uname
#         self.config['lambdas'][idx]["key"] = self.config['template'][lambd["template-attribute"]]
# def _format_config(self):
#     conf = {
#         "AwsRegion": self.config["aws"]["region"],
#         "AwsAccountId": self.config["aws"]["account-id"],
#     }
#     if "deployment-role" in self.config["aws"]:
#         conf["AwsDeploymentRole"] = self.config["aws"]["deployment-role"]
#     for param, val in self.config['template'].items():
#         conf["".join(x.title() for x in param.split("-"))] = val
#     if "parameters" in self.config['template']:
#         for param, val in self.config['template']["parameters"].items():
#             conf["".join(x.title() for x in param.split("-"))] = val
#     return conf
# def _format_cfn_parameters(self, parameters):
#     """Format parmeters camel case"""
#     return [
#         {
#             "ParameterKey": "".join([x.title() for x in key.split("-")]),
#             "ParameterValue": val,
#         }
#         for key, val in parameters.items()
#     ]
# def _compress_folder(self, location, filename):
#     """Compress a folder"""
#     rootlen = len(location)
#     zipf = zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)
#     for root, _, files in os.walk(location):
#         for f in files:
#             fn = os.path.join(root, f)
#             zipf.write(fn, fn[rootlen:])
#     zipf.close()
#     return filename
# def _format_test_template_location(self, location):
#     template = location.split("/")[-1]
#     key = (
#         "/".join(location.split("/")[3:-1])
#         + "/_tests/"
#         + location.split("/")[-1]
#     )
#     return template, key
# def _file_exists(self, file_path):
#     """Check if a file exists"""
#     return os.path.exists(os.path.expanduser(file_path))
# def _read_yaml(self, filename):
#     """Read a YAML file"""
#     with open(filename, "r") as stream:
#         return yaml.safe_load(stream)
# def _write_yaml(self, obj, filename):
#     """Write a YAML file"""
#     with open(filename, "w+") as stream:
#         yaml.dump(obj, stream)
