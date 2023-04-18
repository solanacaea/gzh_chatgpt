import yaml
from utils.helper import PROJECT_PATH_NAME


def load_config():
    with open(f"{PROJECT_PATH_NAME}/config/config.yml", 'r', encoding="utf-8")as f:
        conf_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
        return conf_yaml


