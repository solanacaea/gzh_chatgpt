from wechat_sdk import WechatConf, WechatBasic
from utils.cache import access_tk_info
import requests
import hashlib
import json
import time
from utils.logger import get_out_logger


logger = get_out_logger()


def init_wechat():
    from utils.cache import get_conf
    app_id = get_conf("wx_jszaz_app_id")
    app_secret = get_conf("wx_jszaz_app_secret")

    conf = WechatConf(
        token=get_conf("wx_jszaz_tk"),
        appid=app_id,
        appsecret=app_secret,
        encrypt_mode='normal',
        encoding_aes_key=get_conf("wx_jszaz_encoding_aes_key")
    )
    wechat = WechatBasic(conf=conf)
    return wechat


async def _req_token():
    from utils.cache import get_conf
    app_id = get_conf("wx_jszaz_app_id")
    app_secret = get_conf("wx_jszaz_app_secret")
    res = requests.get(url=get_conf("wx_url_token"), params={
             "grant_type": 'client_credential',
             'appid': app_id,
             'secret': app_secret,
             }).json()
    return res.get('access_token')


async def check_signature(token, timestamp, nonce, signature):
    tmp = [token, timestamp, nonce]
    tmp.sort()
    res = hashlib.sha1("".join(tmp).encode("utf8")).hexdigest()
    return True if res == signature else False


async def _generate_token():
    if access_tk_info["tk"] == "":
        access_tk_info["tk"] = await _req_token()
        access_tk_info["time"] = time.time()
    if time.time() - access_tk_info["time"] > 7000:
        access_tk_info["tk"] = await _req_token()
        access_tk_info["time"] = time.time()


async def send_to_user(to_user, resp_text):
    from utils.cache import get_conf
    await _generate_token()
    body = {
        "touser": to_user,
        "msgtype": "text",
        "text": {
            "content": resp_text
        }
    }
    res = requests.post(url=get_conf("wx_url_msg"), params={
        'access_token': access_tk_info["tk"]
    }, data=json.dumps(body, ensure_ascii=False).encode('utf-8'))
    logger.info(f"sent to user: {resp_text}")
    return res
