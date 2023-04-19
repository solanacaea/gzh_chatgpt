from sanic import Blueprint
from sanic.response import text
from wx.gzh_service import GzhService
from functools import wraps
from utils.logger import TraceLogger


bp_gzh = Blueprint("gzh", url_prefix="gzh")
file_name = "gzh"


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


@bp_gzh.route('/wx', methods=["GET", "POST"])
@trace_log("wx")
async def wechat(request):
    return text(await GzhService().ask_once(request))

