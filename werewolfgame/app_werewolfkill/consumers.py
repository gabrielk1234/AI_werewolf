# your_app/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
import yaml
import re
import datetime
import asyncio
from app_werewolfkill.game_logic.gamemaster import GameMaster
from app_werewolfkill.game_logic.gamelog import GameLogPDF

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
        self.pdf = GameLogPDF()
        self.pdf.add_page()

    async def disconnect(self, close_code):
        print("WebSocket disconnected")

    async def receive(self, text_data):
        # Load Pdf
        if text_data == 'load_pdf':
            all_pdf,all_date = self.load_all_pdf()
            await self.send(text_data=json.dumps({'type':'load_pdf','pdf':all_pdf,'date':all_date}))
        
        # Start Game
        if text_data == "game_start":
            msg_to_send = self.gm.game_start()
            for msg in msg_to_send:
                self.pdf.write(msg)
                await self.send(text_data=json.dumps(msg))
                await asyncio.sleep(2)
            
            # Night Routine
            while not self.gm.end:
                for msg in self.gm.night_routine():
                    self.pdf.write(msg)
                    await self.send(text_data=json.dumps(msg))
                    await asyncio.sleep(2)
                
            # Game End
            pdf_file_path = "media/GameLog"
            file_name = f'/game_log_{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}'
            self.pdf.output(pdf_file_path+file_name+'.pdf', "F")
            date = file_name.split('_')[-1]
            date = datetime.datetime.strptime(date,"%Y-%m-%d-%H-%M-%S").strftime("%Y-%m-%d %H:%M")
            await self.send(text_data=json.dumps({'type':'pdf','filename':f'{file_name[1:]}.pdf','date':date}))

    def load_all_pdf(self):
        all_pdf = os.listdir('media/GameLog')
        all_date = [self.get_date(pdf) for pdf in all_pdf]
        return all_pdf,all_date
    
    def get_date(self,filename):
        match = re.search(r"game_log_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\.pdf", filename)
        if match:
            datetime_str = match.group(1)
            date = datetime.datetime.strptime(datetime_str,"%Y-%m-%d-%H-%M-%S").strftime("%Y-%m-%d %H:%M")
            return date