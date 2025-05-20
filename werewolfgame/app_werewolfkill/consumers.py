import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "連線成功，WebSocket 已建立！"
        }))

    async def disconnect(self, close_code):
        print(f"❌ WebSocket 關閉, code={close_code}")

    async def receive(self, text_data):
        print(f"📩 收到訊息：{text_data}")
        await self.send(text_data=json.dumps({
            'message': f"Echo: {text_data}"
        }))