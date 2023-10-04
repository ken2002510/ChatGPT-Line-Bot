from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)

from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            ImageSendMessage, AudioMessage, QuickReply,
                            QuickReplyButton, MessageAction, FileMessage)
import os
import uuid
import re

from src.find import test, test2, sign
from src.writeexcel import append_to_excel, write_to_google_sheets, read_to_google_sheets, write_content, read_practice, write_report
from src.writecsv import append_to_csv
from src.RepairOrder import _quickreply, checkdata
from src.models import OpenAIModel
from src.memory import Memory
from src.logger import logger
from src.storage import Storage, FileStorage, MongoStorage
from src.utils import get_role_and_content
from src.service.youtube import Youtube, YoutubeTranscriptReader
from src.service.website import Website, WebsiteReader
from src.mongodb import mongodb
from src.read_excel import find_next_row_by_first_row_value

load_dotenv('.env')

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
storage = None
youtube = Youtube(step=4)
website = Website()
content = ""

memory = Memory(system_message=os.getenv('SYSTEM_MESSAGE'),
                memory_message_count=2)
model_management = {}
api_keys = {}


@app.route("/callback", methods=['POST'])
def callback():
  signature = request.headers['X-Line-Signature']
  body = request.get_data(as_text=True)
  app.logger.info("Request body: " + body)
  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    print(
      "Invalid signature. Please check your channel access token/channel secret."
    )
    abort(400)
  return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
  user_id = event.source.user_id
  text = event.message.text.strip()
  logger.info(f'{user_id}: {text}')

  try:
    if text.startswith('/註冊'):
      api_key = text[3:].strip()
      model = OpenAIModel(
        api_key="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")
      is_successful, _, _ = model.check_token_valid()
      if not is_successful:
        raise ValueError('Invalid API token')
      response_msg = write_to_google_sheets(api_key)
      model_management[user_id] = model
      storage.save(
        {user_id: "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"})
      storage2.save({user_id: api_key})
      msg = TextSendMessage(text=response_msg)

    
    elif text.startswith('/工令'):
      # 更改系統為格式機器人
      memory.change_system_message(
        user_id,
        '''你是一個處理維修單格式的客服人員，當我輸入資料時，請按照格式進行輸出。並詢問客人是否有誤，每一次回答都要附上目前修正完的資料，當客人回答你使你得到全部資料(包括舊的型號及維修內容)資料內容必須完整呈現，每一個步驟都要執行過不可以跳過且輸出格式記得在資料前後都要用---當分隔　如果沒有錯誤一定必須要詢問客人的型號及維修內容(預測舊的客人型號及維修內容內的資料清空)，請依照步驟的順序執行  若資料無誤請到必須詢問型號及維修內容.
---
"工令":"內容",
"區域":"內容",
"案名":"內容",
"聯絡人":"姓名及電話",
"地址":"內容"
"型號":"內容"
"維修內容":"內容"
---
以下是執行步驟
STEP1.
你好以下是您的資料 請確認是否正確
---
"工令":"1100129-7",
"區域":"臺中市東區",
"案名":"臺中三井(1/4)",
"聯絡人":"紀仁宗先生0952-800-789",
"地址":"臺中市東區復興東一街糖廠旁工地",
"型號":"",
"維修內容":""
---
STEP2.
首先先詢問工令、區域、案名、聯絡人、地址是否有錯誤，若資料有錯誤協助更改，
STEP3.
詢問需要填寫的型號及維修內容
STEP4.
最後列印出目前修改所有資料(包括格式按照下面
---
"工令":"內容",
"區域":"內容",
"案名":"內容",
"聯絡人":"姓名及電話",
"地址":"內容"
"型號":"內容"
"維修內容":"內容"
---
並詢問我若資料沒有錯誤請回復完畢
''')
      # 取得工令
      prompt = text[3:].strip()
      order_storage.save({user_id: prompt})
      # 取得代號
      tt = storage2.load().get(user_id)
      print(tt)
      # 用TEST測試工令跟代號是否符合最後丟符合的資料到quickreply生成

      quick = test(tt, prompt)
      if quick == None:
        msg = TextSendMessage(text='工令錯誤', )
      else:
        msg = TextSendMessage(
          text='請選擇區域以及案名',
          # quick_reply=_quickreply(test(tt,prompt))
          quick_reply=_quickreply(quick))
    elif text.startswith('-!'):
      tt = storage2.load().get(user_id)
      workorder = order_storage.load().get(user_id)
      prompt = text[2:].strip()
      content = test2(prompt, tt, workorder)
      memory.addcontent(user_id, content)
      msg = TextSendMessage(
        text=content + '\n請確認資料是否正確',
        # quick_reply=_quickreply(test(tt,prompt))
        quick_reply=checkdata())
    elif text.startswith('資料無誤'):
      user_model = model_management[user_id]
      memory.append(user_id, 'user', text)
      content = memory.getcontent(user_id)
      print(content)
      if content == "":
        msg = TextSendMessage(text="查無資料")
      else:
        memory.excel_data(user_id, content)
        print(memory.get(user_id))
        is_successful, response, error_message = user_model.chat_completions(
          memory.get(user_id), os.getenv('OPENAI_MODEL_ENGINE'))
        if not is_successful:
          raise Exception(error_message)
        role, response = get_role_and_content(response)
        msg = TextSendMessage(text=response)
        memory.append(user_id, role, response)
    elif text.startswith('填寫完畢') or text.startswith('完畢') or text.startswith(
        'ok') or text.startswith('Ok') or text.startswith('OK'):
      print(memory.getgptsort(user_id))
      text = memory.getgptsort(user_id)
      append_to_excel(text)
      append_to_csv(text, 'check.csv')
      print(text)
      write_report(text)
      msg = TextSendMessage(text="已完成填寫")
    elif text.startswith('/系統訊息'):
      memory.change_system_message(user_id, text[5:].strip())
      msg = TextSendMessage(text='輸入成功')

    elif text.startswith('註冊說明') or text.startswith('操作說明'):
      print(0)

    elif text.startswith('檔案下載'):

      msg = TextSendMessage(
        text=
        "https://docs.google.com/spreadsheets/d/1ODLnfk_sGhgXgNkwHDsFq5YPd1xRbf4bQweMAg0wiMA/edit#gid=0"
      )
    elif text.startswith('/清除'):
      memory.remove(user_id)
      msg = TextSendMessage(text='歷史訊息清除成功')
    else:
      user_model = model_management[user_id]
      memory.append(user_id, 'user', text)
      url = website.get_url_from_text(text)
      if url:
        if youtube.retrieve_video_id(text):
          is_successful, chunks, error_message = youtube.get_transcript_chunks(
            youtube.retrieve_video_id(text))
          if not is_successful:
            raise Exception(error_message)
          youtube_transcript_reader = YoutubeTranscriptReader(
            user_model, os.getenv('OPENAI_MODEL_ENGINE'))
          is_successful, response, error_message = youtube_transcript_reader.summarize(
            chunks)
          if not is_successful:
            raise Exception(error_message)
          role, response = get_role_and_content(response)
          msg = TextSendMessage(text=response)
        else:
          chunks = website.get_content_from_url(url)
          if len(chunks) == 0:
            raise Exception('無法撈取此網站文字')
          website_reader = WebsiteReader(user_model,
                                         os.getenv('OPENAI_MODEL_ENGINE'))
          is_successful, response, error_message = website_reader.summarize(
            chunks)
          if not is_successful:
            raise Exception(error_message)
          role, response = get_role_and_content(response)
          msg = TextSendMessage(text=response)
      else:
        name = storage2.load().get(user_id)
        response_msg = write_content(name, text)
        content = memory.getcontent(user_id)
        memory.excel_data(user_id, content)
        print(memory.get(user_id))
        is_successful, response, error_message = user_model.chat_completions(
          memory.get(user_id), os.getenv('OPENAI_MODEL_ENGINE'))
        if not is_successful:
          raise Exception(error_message)
        role, response = get_role_and_content(response)
        msg = TextSendMessage(text=response)
      memory.append(user_id, role, response)
      print(str(response))
      if '---' in str(response):
        print(1)
        match = re.search(r'---\n(.*)\n---', response, re.DOTALL)
        print(match)
        if match:
          result = match.group(1)
          print(result)
          memory.addgptsort(user_id, result)
  except ValueError:
    msg = TextSendMessage(text='請先註冊 Token，格式為 /註冊公司代號')
  except KeyError:
    msg = TextSendMessage(text='請先註冊 Token，格式為 /註冊公司代號')
  except Exception as e:
    memory.remove(user_id)
    if str(e).startswith('Incorrect API key provided'):
      msg = TextSendMessage(text='OpenAI API Token 有誤，請重新註冊。')
    elif str(e).startswith(
        'That model is currently overloaded with other requests.'):
      msg = TextSendMessage(text='已超過負荷，請稍後再試')
    else:
      msg = TextSendMessage(text=str(e))
  line_bot_api.reply_message(event.reply_token, msg)


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
  user_id = event.source.user_id
  audio_content = line_bot_api.get_message_content(event.message.id)
  input_audio_path = f'{str(uuid.uuid4())}.m4a'
  with open(input_audio_path, 'wb') as fd:
    for chunk in audio_content.iter_content():
      fd.write(chunk)

  try:
    if not model_management.get(user_id):
      raise ValueError('Invalid API token')
    else:
      is_successful, response, error_message = model_management[
        user_id].audio_transcriptions(input_audio_path, 'whisper-1')
      if not is_successful:
        raise Exception(error_message)
      memory.append(user_id, 'user', response['text'])
      is_successful, response, error_message = model_management[
        user_id].chat_completions(memory.get(user_id), 'gpt-3.5-turbo')
      if not is_successful:
        raise Exception(error_message)
      role, response = get_role_and_content(response)
      memory.append(user_id, role, response)
      msg = TextSendMessage(text=response)
  except ValueError:
    msg = TextSendMessage(text='請先註冊 Token，格式為 /註冊公司代號')
  except KeyError:
    msg = TextSendMessage(text='請先註冊 Token，格式為 /註冊公司代號')
  except Exception as e:
    memory.remove(user_id)
    if str(e).startswith('Incorrect API key provided'):
      msg = TextSendMessage(text='OpenAI API Token 有誤，請重新註冊。')
    else:
      msg = TextSendMessage(text=str(e))
  os.remove(input_audio_path)
  line_bot_api.reply_message(event.reply_token, msg)


@app.route("/", methods=['GET'])
def home():
  return 'Hello World'


if __name__ == "__main__":
  if os.getenv('USE_MONGO'):
    mongodb.connect_to_database()
    storage = Storage(MongoStorage(mongodb.db))
  else:
    # API
    storage = Storage(FileStorage('db.json'))
    # 公司代號
    storage2 = Storage(FileStorage('db2.json'))
    # 工令
    order_storage = Storage(FileStorage('work_order.json'))
  try:
    data = storage.load()
    for user_id in data.keys():
      model_management[user_id] = OpenAIModel(api_key=data[user_id])
  except FileNotFoundError:
    pass
  app.run(host='0.0.0.0', port=8080)
