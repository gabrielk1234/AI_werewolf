# your_app/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
import yaml
import asyncio
from app_werewolfkill.game_logic.test import GameMaster

class Myconsumer(AsyncWebsocketConsumer):
    def load_messages(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "game_logic/message.yaml")

        # Load Message
        with open(file_path, "r", encoding="utf-8") as f:
            self.messages = yaml.safe_load(f)

    async def connect(self):
        await self.accept()
        self.load_messages()
        self.gm = GameMaster(self.messages)

    async def disconnect(self, close_code):
        print("WebSocket disconnected")

    async def receive(self, text_data):
        # Start Game
        if text_data == "game_start":
            msg_to_send = self.gm.game_start()
            for msg in msg_to_send:
                await self.send(text_data=json.dumps(msg))
                await asyncio.sleep(2)
            
        # Night Routine
        while not self.gm.end:
            for msg in self.gm.night_routine():
                await self.send(text_data=json.dumps(msg))
                await asyncio.sleep(2)
            
        
