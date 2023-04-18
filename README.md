# gzh_chatgpt
wechat微信公众号问答对接ChatGPT


readme整理中...

pip install -r requirements.txt

config/config.yml

openai_api_key: sk-

wx_jszaz_app_id: 公众号app_id

wx_jszaz_app_secret: 公众号app_secret

wx_jszaz_encoding_aes_key: 公众号aes_key

wx_jszaz_tk: 公众号token

start.sh

请求：http://localhost:8080/gzh/wx
请求参数：
signature
timestamp
nonce
echostr
xml
  FromUserName
  ToUserName
  MsgType
  MsgId
  Content
  
