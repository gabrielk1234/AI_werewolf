# your_app/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio

class UserInfoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        # 收到前端的啟動訊號後，回傳姓名
        await self.send(text_data=json.dumps({
            'type': 'name',
            'value': '小明'
        }))
        # 模擬延遲
        await asyncio.sleep(2)
        await self.send(text_data=json.dumps({
            'type': 'student_id',
            'value': 'A123456'
        }))

    async def disconnect(self, close_code):
        print("WebSocket disconnected")
