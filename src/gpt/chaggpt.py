import openai
import requests
from utils.logger import get_out_logger, get_trace_logger
from utils.cache import get_conf

logger = get_out_logger()
trace_logger = get_trace_logger()
openai.api_key = get_conf("openai_api_key")
max_tokens = 200
REQUEST_MSG_APPEND = "，请返回最多280个字符。"


async def ask_davinci(content, device_id):
    response = await openai.Completion.acreate(
        engine="text-davinci-003",
        prompt=content,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        timeout=30,
        user=device_id
    )
    resp_text = response['choices'][0]['text']
    return resp_text


async def ask_gpt35_by_url(content, device_id):
    from utils.cache import get_conf
    openai_gpt35_url = get_conf("openai_gpt35_url")
    openai_api_key = get_conf("openai_api_key")

    param = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": content}],
        "user": device_id,
        "max_tokens": max_tokens,
        "timeout": 30
    }
    header = {
        'Authorization': 'Bearer ' + openai_api_key,
        'Content-Type': 'application/json'
    }
    resp = requests.post(openai_gpt35_url, json=param, headers=header)
    resp_json = resp.json()
    trace_logger.info(f"q: {content}\n answer:{resp_json}")
    return resp_json["choices"][0]["message"]["content"].strip()


async def ask_gpt35_by_sdk(content, device_id):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": content + REQUEST_MSG_APPEND}],
        user=device_id,
        max_tokens=max_tokens,
        timeout=30,
    )
    resp_text = completion['choices'][0]["message"]["content"].strip()
    trace_logger.info(f"q: {content}\n answer:{resp_text}")
    logger.info(f"q: {content}\n completion:{completion}")
    return resp_text
