from wx.gzh import check_signature, send_to_user
from gpt.chaggpt import ask_gpt35_by_sdk
import xmltodict
import time
from utils.logger import get_out_logger

RESPONSE_EMPTY = "EMPTY"
RESPONSE_ECHO = "ECHO"
RESPONSE_NEXT = "NEXT"
RESPONSE_RESULT = "RESULT"
RESPONSE_TIMEOUT = "TIMEOUT"

RESPONSE_TYPE_PUSH = "push"
RESPONSE_TYPE_NO_PUSH = "no_push"
MSG_TIMEOUT = "请求超时，请稍后再试。"
logger = get_out_logger()


class GzhService:
    def __init__(self, user_ask, doc):
        self.user_ask = user_ask
        self.doc = doc

    async def _pre_check(self, request):
        logger.info(f"args={request.args}")
        signature = request.args.get("signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        echostr = request.args.get("echostr")
        if signature is None or timestamp is None or nonce is None:
            return RESPONSE_EMPTY, "", None

        if echostr:
            logger.info(f"echostr={echostr}")
            return RESPONSE_ECHO, echostr, None

        from utils.cache import get_conf
        wx_jszaz_tk = str(get_conf("wx_jszaz_tk"))
        valid = await check_signature(wx_jszaz_tk, timestamp, nonce, signature)
        if valid is False:
            return RESPONSE_EMPTY, "", None

        # print(doc)
        from_user = self.doc["xml"]["FromUserName"]  # 发送方帐号（一个OpenID）
        if self.doc["xml"]["MsgType"] != "text":  # 文本消息处理
            return RESPONSE_EMPTY, "", None

        # 当前用户缓存
        cache_curr_user = {}
        if from_user in self.user_ask:
            cache_curr_user = self.user_ask[from_user]
        else:
            self.user_ask[from_user] = cache_curr_user

        # 当前用户-当次缓存
        msg_id = self.doc["xml"]["MsgId"]
        if msg_id in cache_curr_user:
            cache_curr_user_msg = cache_curr_user[msg_id]
            cache_curr_user_msg["count"] += 1
        else:
            cache_curr_user[msg_id] = {"count": 1}
            cache_curr_user_msg = cache_curr_user[msg_id]

        if "result" in cache_curr_user_msg:
            resp = cache_curr_user_msg["result"]
            del cache_curr_user[msg_id]
            logger.info(f"从缓存取得请求结果, msg_id={msg_id}, resp={resp}")
            return RESPONSE_RESULT, resp, self.doc
        elif cache_curr_user_msg["count"] > 3:
            return RESPONSE_TIMEOUT, MSG_TIMEOUT, None
        elif cache_curr_user_msg["count"] > 1:
            return RESPONSE_EMPTY, "", None
        else:
            return RESPONSE_NEXT, "next", self.doc

    async def ask_once(self, request):
        return await self._ask(request)

    async def ask_with_callback(self, request):
        return await self._ask(request, response_type=RESPONSE_TYPE_PUSH)

    async def _ask(self, request, response_type=RESPONSE_TYPE_NO_PUSH):
        valid, resp, doc = await self._pre_check(request)
        if valid == RESPONSE_EMPTY or valid == RESPONSE_ECHO:
            return resp
        if valid == RESPONSE_RESULT or valid == RESPONSE_TIMEOUT:
            resp_dict = await self._consolidate_resp(doc, resp)
            return xmltodict.unparse(resp_dict)

        msg_id = doc["xml"]["MsgId"]
        to_user = doc["xml"]["ToUserName"]
        from_user = doc["xml"]["FromUserName"]
        msg = doc["xml"]["Content"]
        resp_text = await ask_gpt35_by_sdk(msg, from_user)
        resp_dict = await self._consolidate_resp(doc, resp_text)

        if from_user not in self.user_ask:
            return xmltodict.unparse(resp_dict)
        if msg_id not in self.user_ask[from_user]:
            return xmltodict.unparse(resp_dict)

        timestamp = request.args.get("timestamp")
        gap_time = time.time() - float(timestamp)
        logger.info(f"执行时间, start={timestamp}, end={time.time()}, gap={gap_time}, msg_id={msg_id}, msg={msg}")
        if gap_time > 15:
            logger.info(f"请求超时啦，删除缓存, msg_id={msg_id}, msg={msg}")
            if response_type == RESPONSE_TYPE_PUSH:
                await send_to_user(to_user, resp_text)
                del self.user_ask[from_user][msg_id]
            return xmltodict.unparse(resp_dict)
        else:
            self.user_ask[from_user][msg_id]["result"] = resp_text
            logger.info(f"从缓存取结果, msg_id={msg_id}, msg={msg}")
            # del self.user_ask[from_user][msg_id]
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
