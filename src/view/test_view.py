from functools import wraps
from sanic import Blueprint
from sanic.response import text
from wx.gzh_service import send_to_user
import xmltodict
import time
from utils.logger import get_out_logger, TraceLogger

logger = get_out_logger()
bp_test = Blueprint("test", url_prefix="gzh")
file_name = "test"


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


@bp_test.route('/')
@trace_log("hello_world")
async def hello_world(request):
    return text('Hello World!')


@bp_test.route('/wx1', methods=["GET", "POST"])
@trace_log("wx1")
async def wx1(request):
    xml_form = """
            <xml>
            <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
            <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
            <CreateTime>{CreateTime}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{Content}]]></Content>
            </xml>
            """

    resp_dict = {
        "xml": {
            "ToUserName": "from_user",
            "FromUserName": "to_user",
            "CreateTime": int(time.time()),
            "MsgType": "text",
            "Content": "resp_text"
        }
    }

    return text(xmltodict.unparse(resp_dict))


@bp_test.route('/sent', methods=["GET", "POST"])
@trace_log("sent")
async def test(request):
    q = request.json.get("question")
    await send_to_user("wxid", q)
