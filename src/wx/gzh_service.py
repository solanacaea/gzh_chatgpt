from wx.gzh import check_signature, send_to_user
from utils.cache import user_ask
from gpt.chaggpt import ask_gpt35_by_sdk
import xmltodict
import time
from utils.logger import get_out_logger

RESPONSE_EMPTY = "EMPTY"
RESPONSE_ECHO = "ECHO"
RESPONSE_NEXT = "NEXT"
RESPONSE_RESULT = "RESULT"

RESPONSE_TYPE_PUSH = "push"
RESPONSE_TYPE_NO_PUSH = "no_push"
logger = get_out_logger()


class GzhService:
    def __init__(self):
        pass

    async def _pre_check(self, request):
        signature = request.args.get("signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        echostr = request.args.get("echostr")
        if signature is None or timestamp is None or nonce is None:
            return RESPONSE_EMPTY, "", None

        from utils.cache import get_conf
        wx_jszaz_tk = str(get_conf("wx_jszaz_tk"))
        valid = await check_signature(wx_jszaz_tk, timestamp, nonce, signature)
        if valid is False:
            return RESPONSE_EMPTY, "", None
        if echostr:
            return RESPONSE_ECHO, echostr, None

        data = request.body.decode("utf-8")
        doc = xmltodict.parse(data)  # 解析xml数据
        # print(doc)
        from_user = doc["xml"]["FromUserName"]  # 发送方帐号（一个OpenID）
        if doc["xml"]["MsgType"] != "text":  # 文本消息处理
            return RESPONSE_EMPTY, "", None

        # 当前用户缓存
        cache_curr_user = {}
        if from_user in user_ask:
            cache_curr_user = user_ask[from_user]
        else:
            user_ask[from_user] = cache_curr_user

        # 当前用户-当次缓存
        msg_id = doc["xml"]["MsgId"]
        if msg_id in cache_curr_user:
            cache_curr_user_msg = cache_curr_user[msg_id]
            cache_curr_user_msg["count"] += 1
        else:
            cache_curr_user_msg = {"count": 1}

        if "result" in cache_curr_user_msg:
            resp = cache_curr_user_msg["result"]
            del cache_curr_user[msg_id]
            logger.info(f"从缓存取得请求结果, msg_id={msg_id}")
            return RESPONSE_RESULT, resp, None
        elif cache_curr_user_msg["count"] > 1:
            return RESPONSE_EMPTY, "", None
        else:
            return RESPONSE_NEXT, "next", doc

    async def ask_once(self, request):
        return await self._ask(request)

    async def ask_with_callback(self, request):
        return await self._ask(request, response_type=RESPONSE_TYPE_PUSH)

    async def _ask(self, request, response_type=RESPONSE_TYPE_NO_PUSH):
        valid, resp, doc = await self._pre_check(request)
        if valid == RESPONSE_EMPTY or valid == RESPONSE_ECHO:
            return resp
        if valid == RESPONSE_RESULT:
            resp_dict = await self._consolidate_resp(doc, resp)
            return xmltodict.unparse(resp_dict)

        msg_id = doc["xml"]["MsgId"]
        to_user = doc["xml"]["ToUserName"]
        from_user = doc["xml"]["FromUserName"]
        msg = doc["xml"]["Content"]
        resp_text = await ask_gpt35_by_sdk(msg, from_user)
        resp_dict = await self._consolidate_resp(doc, resp_text)

        if from_user not in user_ask:
            return xmltodict.unparse(resp_dict)
        if msg_id not in user_ask[from_user]:
            return xmltodict.unparse(resp_dict)

        timestamp = request.args.get("timestamp")
        if time.time() - timestamp > 15:
            logger.info(f"请求超时啦，删除缓存, msg_id={msg_id}, msg={msg}")
            if response_type == RESPONSE_TYPE_PUSH:
                await send_to_user(to_user, resp_text)
            del user_ask[from_user][msg_id]
        else:
            user_ask[from_user][msg_id]["result"] = resp_text
            logger.info(f"从缓存取结果, msg_id={msg_id}, msg={msg}")
            return xmltodict.unparse(resp_dict)

    @staticmethod
    async def _consolidate_resp(doc, resp_text):
        to_user = doc["xml"]["ToUserName"]  # 开发者微信号
        from_user = doc["xml"]["FromUserName"]  # 发送方帐号（一个OpenID）
        resp_dict = {
            "xml": {
                "ToUserName": from_user,
                "FromUserName": to_user,
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": resp_text
            }
        }
        return resp_dict
