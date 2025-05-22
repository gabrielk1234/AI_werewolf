import yaml
import time
import random
import json
import os

from openai import OpenAI
from app_werewolfkill.game_logic.config import api_key, system_prompt
from app_werewolfkill.game_logic.werewolves_character import WerewolfCharacter
from app_werewolfkill.game_logic.moderator import Moderator
from app_werewolfkill.game_logic.utils import extract_json

class GameMaster():
    def __init__(self,messages):
        self.wolf1 = WerewolfCharacter(name="Alex", role="werewolf", teammate="Anson")
        self.wolf2 = WerewolfCharacter(name="Anson", role="werewolf", teammate="Alex")
        self.villager1 = WerewolfCharacter(name="Bob", role="villager")
        self.villager2 = WerewolfCharacter(name="Charlie", role="villager")
        self.seer = WerewolfCharacter(name="Diana", role="seer")
        self.witch = WerewolfCharacter(name="Eve", role="witch")

        self.moderator = Moderator([self.wolf1, self.wolf2, self.villager1, self.villager2, self.seer, self.witch])
        self.messages = messages

    def game_start(self):
        messages_to_send = [
            {'type': 'system', 'value': self.messages['game_start']},
            {'type': 'system', 'value': self.messages['distribute_chac']}
        ]
        
        # ✅ 回傳前端訊息
        return messages_to_send
