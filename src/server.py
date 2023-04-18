from sanic import Sanic
from utils.logger import get_out_logger
from utils.helper import get_ip, SERVER_FORMAT
from view import view
from utils.helper import PROJECT_PATH_NAME
import yaml
import logging

log_config = None
with open(f"{PROJECT_PATH_NAME}/config/logger.yml", 'r', encoding="utf-8")as f:
    logging_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config=logging_yaml)

logger = get_out_logger()


app = Sanic(__name__, log_config=log_config)
app.blueprint(view)

# from sanic_cors import CORS
# CORS(app)


def start_server(port):
    logger.info(f"server started on {SERVER_FORMAT.format('http', get_ip(), port)}")
    app.run(host="0.0.0.0", port=port, workers=1)
