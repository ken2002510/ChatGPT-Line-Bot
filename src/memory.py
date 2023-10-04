from typing import Dict
from collections import defaultdict



class MemoryInterface:
    def append(self, user_id: str, message: Dict) -> None:
        pass

    def get(self, user_id: str) -> str:
        return ""

    def remove(self, user_id: str) -> None:
        pass


class Memory(MemoryInterface):
    def __init__(self, system_message, memory_message_count):
        self.storage = defaultdict(list)
        self.system_messages = defaultdict(str)
        self.default_system_message = system_message
        self.memory_message_count = memory_message_count
        self.exceldata=defaultdict(str)
        self.content=defaultdict(str)
        # gptsort是GPT整理完的內容
        self.gptsort=defaultdict(str)
    def _initialize(self, user_id: str):
        self.storage[user_id] = [{
            'role': 'system', 'content': self.system_messages.get(user_id) or self.default_system_message
        }]
    def _drop_message(self, user_id: str):
        if len(self.storage.get(user_id)) >= (self.memory_message_count + 1) * 2 + 1:
            print("g")
            return [self.storage[user_id][0]] + self.storage[user_id][-(self.memory_message_count * 2):]
        return self.storage.get(user_id)

    def change_system_message(self, user_id, system_message):
        self.system_messages[user_id] = system_message
        self.remove(user_id)

    def append(self, user_id: str, role: str, content: str) -> None:
        if self.storage[user_id] == []:
            self._initialize(user_id)
        self.storage[user_id].append({
            'role': role,
            'content': content
        })
        self._drop_message(user_id)

    def get(self, user_id: str) -> str:
        if self.exceldata[user_id]=="":
          return self.storage[user_id]
        else:
          return self.storage[user_id][:1] + self.exceldata[user_id] + self.storage[user_id][1:]
        

    def remove(self, user_id: str) -> None:
        self.storage[user_id] = []
    def excel_data(self, user_id, excel_message) :
        self.exceldata[user_id]=[{
            'role': "assistant",
            'content': excel_message
          }]
    def addcontent(self, user_id, _content) :
        self.content[user_id]=_content
    def addgptsort(self, user_id, _content) :
        self.gptsort[user_id]=_content
    def getcontent(self,user_id) :
        return self.content[user_id]
    def getchatgpt(self,user_id):
        return self.storage[user_id][-1:][0]
    def getgptsort(self,user_id):
        return self.gptsort[user_id]