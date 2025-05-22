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

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "message.yaml")

# Load Message
with open(file_path, "r", encoding="utf-8") as f:
    messages = yaml.safe_load(f)

# Initialize Character
wolf1 = WerewolfCharacter(name="Alex", role="werewolf", teammate="Anson")
wolf2 = WerewolfCharacter(name="Anson", role="werewolf", teammate="Alex")
villager1 = WerewolfCharacter(name="Bob", role="villager")
villager2 = WerewolfCharacter(name="Charlie", role="villager")
seer = WerewolfCharacter(name="Diana", role="seer")
witch = WerewolfCharacter(name="Eve", role="witch")

moderator = Moderator([wolf1, wolf2, villager1, villager2, seer, witch])

def night():
    moderator.set_night_status()
    use_heal = False
    killed_dict = {}
    # Day and Night Cycle
    return(messages['night'] + "今天是第" + str(moderator.night) + "晚")