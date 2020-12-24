import os


class DeploymentManagerValidation:
    @classmethod
    def validate_config(cls, config):
        """Validate section of the template config"""
        if "gcp" not in config:
            raise KeyError("gcp is required in a stack definition")
        else:
            cls._validate_gcp_config(config["gcp"])

        if "location" not in config:
            raise KeyError("location is required in a stack definition")
        elif not cls._file_exists(os.path.expanduser(config["location"])):
            raise FileNotFoundError(f"Template {config['location']} does not exist")

        if "template" not in config:
            raise KeyError("template is required in a stack definition")
        else:
            cls._validate_template_config(config["template"])

        if "functions" in config:
            cls._validate_functions_config(config["functions"])

    @classmethod
    def _validate_gcp_config(cls, config):
        """Validate section of the template config"""
        if type(config) != dict:
            raise ValueError("gcp must be a dict")
        if "account-id" not in config:
            raise KeyError("gcp.account-id is required in template definition")
        if "project" not in config:
            raise KeyError("gcp.project is required in template definition")
        if "zone" not in config:
            raise KeyError("gcp.zone is required in template definition")

    @classmethod
    def _validate_template_config(cls, config):
        """Validate section of the template config"""
        if type(config) != dict:
            raise ValueError("template must be a dict")
        if "name" not in config:
            raise KeyError("template.name is required in stack definition")
        if type(config["name"]) != str:
            raise ValueError("template.name must be a string")
        if "parameters" in config and type(config["parameters"]) != dict:
            raise ValueError("template.parameters must be a dict")

    @classmethod
    def _validate_functions_config(cls, config):
        """Validate section of the stack config"""
        for function in config:
            if "name" not in function:
                raise KeyError("Function must have a name")
            if "location" not in function:
                raise KeyError("Function must have a location")
            if "template-attribute" not in function:
                raise KeyError("Function must have a template-attribute")
            if "bucket" not in function:
                raise KeyError("Function must have an artifact bucket location")
            if (
                type(function["name"]) != str
                or type(function["template-attribute"]) != str
                or type(function["bucket"]) != str
            ):
                raise ValueError(
                    "One of these parameters is not a string: name, template-attribute, bucket"
                )
            if not os.path.isdir(function["location"]):
                raise ValueError("Function package is not found")

    @classmethod
    def _file_exists(cls, file_path):
        """Check if a file exists"""
        return os.path.exists(os.path.expanduser(file_path))
