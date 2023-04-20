from sanic import Blueprint
from sanic.response import text
from wx.gzh_service import GzhService
from functools import wraps
from utils.logger import TraceLogger, get_trace_logger
import xmltodict


bp_gzh = Blueprint("gzh", url_prefix="gzh")
file_name = "gzh"
trace_logger = get_trace_logger()


def trace_log(name):
    def wrapper(func):
        @wraps(func)
        async def inner_wrapper(*args, **kwargs):
            request = args[0]
            caller_name = f"{file_name}-{name}"
            log = TraceLogger(caller_name, request)
            log.start()
            resp = await func(*args, **kwargs)
            log.end_log()
            return resp
        return inner_wrapper
    return wrapper


user_ask = {}


@bp_gzh.route('/wx', methods=["GET", "POST"])
# @trace_log("wx")
async def wechat(request):
    trace_logger.info(f"user_ask={user_ask}")
    data = request.body.decode("utf-8")
    doc = xmltodict.parse(data)  # 解析xml数据
    caller_name = f"{file_name}-wechat"
    log = TraceLogger(caller_name, request, doc)
    log.start()
    res = await GzhService(user_ask, doc).ask_once(request)
    log.end_log()
    return text(res)
