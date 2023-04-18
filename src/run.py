from utils.logger import load_logger
from utils.configuration import load_config
from server import start_server
from wx.gzh import init_wechat
from utils.cache import init_in_men_conf

configuration = load_config()
init_in_men_conf(configuration)


def run():
    # load_logger()
    init_wechat()
    start_server(configuration["server_port"])


if __name__ == '__main__':
    run()
