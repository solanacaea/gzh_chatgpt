import time
from utils.logger import get_out_logger
from utils.helper import PROJECT_PATH_NAME


logger = get_out_logger()
access_tk_info = {
    "tk": "",
    "time": time.time()
}


class Configuration:
    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def set_all(self, conf):
        for k, v in conf.items():
            self.set(k, v)


InMemConf = Configuration()


def init_in_men_conf(props):
    global InMemConf
    InMemConf.set_all(props)


def get_conf(k):
    if len(InMemConf.store) == 0:
        logger.info(f"initialized when getting {k}")
        from utils.configuration import load_config
        configuration = load_config()
        InMemConf.set_all(configuration)
        logger.info("reload config...")
    return InMemConf.get(k)



def init_user_ask():
    globals()["user_ask"] = {}


user_ask = {}
def get_user_cache(user_id):
    user_ask.get(user_id)


def set_user_cache(user_id, user_cache):
    user_ask[user_id] = user_cache


