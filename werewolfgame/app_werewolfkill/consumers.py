# your_app/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from app_werewolfkill.game_logic.test import night

class Myconsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        print("WebSocket disconnected")

    async def receive(self, text_data):
        # 收到前端的啟動訊號後，回傳姓名
        if text_data == "start":
            msg = night()
            await self.send(text_data=json.dumps({
                'type':'message',
                'value':msg
            }))

    
