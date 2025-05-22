from openai import OpenAI
import time
from app_werewolfkill.game_logic.config import url,api_key,system_prompt,action_prompt

class WerewolfCharacter:
    def __init__(self, name:str, role:str, teammate=None):
        self.name = name
        self.role = role
        
        self.memory = {}              # 玩家對其他人的印象/懷疑程度
        self.is_alive = True          # 是否仍在場上
        self.teammate = teammate      # 若為狼人，知道同伴

        self.memory = {
            'name': name,
            'role': role,
            'night':None, # set by moderator
            'teammate': teammate if role == 'werewolf' else None,
            'vote_history': {}, # set by moderator
            'player_alive': [], # set by moderator
            'kill_history': {}, # set by moderator
            'statement_history': {}, # set by moderator
            'potion_history': {'heal':{'night':None},
                               'poison':{'night':None}
                               } # set by moderator
        }

        # 女巫的特殊能力
        if self.role == 'witch':
            self.has_heal_potion = True
            self.has_poison_potion = True
            self.memory['potion_history'] = {
                'heal': {'person':None,'night':None},
                'poison': {'person':None,'night':None}
            }

        # 預言家的特殊能力
        if self.role == 'seer':
            self.memory['investigate_history'] = []
            
        self.client = OpenAI(
            base_url=url,
            api_key=api_key
        )
        
        self.set_system_prompt()

    def set_system_prompt(self):
        self.last_msg_prompt = system_prompt[self.role]['last_msg'].format(name=self.name)
        self.speech_prompt = system_prompt[self.role]['speech'].format(name=self.name)
        self.vote_prompt = system_prompt[self.role]['vote'].format(name=self.name)
        if self.role == 'werewolf':
            self.night_prompt = system_prompt[self.role]['night'].format(teammate=self.teammate,name=self.name)
        elif self.role != 'villager':
            self.night_prompt = system_prompt[self.role]['night'].format(name=self.name) # 村民沒有夜晚的行動

    def speak(self):
        if self.role == 'werewolf':
            speech_msg_context = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"teammate":self.teammate,"statement_history":self.memory['statement_history']}
        elif self.role == 'seer':
            speech_msg_context = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"statement_history":self.memory['statement_history'],"investigate_history":self.memory['investigate_history']}  
        elif self.role == 'witch' or self.role == 'villager':
            # 村民和女巫的 speech_msg_context 內容相同
            speech_msg_context = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"statement_history":self.memory['statement_history']}  

        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": self.speech_prompt},
                {"role": "user", "content": action_prompt[self.role]['action_info'].format(**speech_msg_context)},
            ]
        )
        time.sleep(2)
        answer = response.choices[0].message.content
        return answer
    
    def night_action(self,killed_player=None,potion_status=None,potion_type=None):
        if self.role == 'werewolf':
            heal_used = potion_status['has_heal']
            poition_used = potion_status['has_poison']
            prompt = action_prompt['werewolf']['kill'].format(player_alive=self.memory['player_alive'], 
                                                              teammate=self.teammate, 
                                                              statement_history=self.memory['statement_history'],
                                                              has_heal_potion=heal_used,
                                                              has_poison_potion=poition_used
                                                              )
        if self.role == 'seer':
            prompt = action_prompt['seer']['investigate'].format(player_alive=self.memory['player_alive'], 
                                                                 statement_history=self.memory['statement_history'],
                                                                 investigate_history=self.memory['investigate_history'])
        
        if self.role == 'witch':
            if potion_type == 'heal':
                prompt = action_prompt['witch']['use_heal'].format(killed_player=killed_player,
                                                                   player_alive=self.memory['player_alive'],
                                                                   statement_history=self.memory['statement_history'],
                                                                   has_heal_potion=self.has_heal_potion)
            elif potion_type == 'poison':
                prompt = action_prompt['witch']['use_poison'].format(killed_player=killed_player,
                                                                   player_alive=self.memory['player_alive'],
                                                                   statement_history=self.memory['statement_history'],
                                                                   has_poison_potion=self.has_poison_potion)
        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": self.night_prompt},
                {"role": "user", "content": prompt},
            ]
        )
        time.sleep(2)
        answer = response.choices[0].message.content
        return answer

    def vote(self):
        if self.role == 'werewolf':
            vote_info = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"teammate":self.teammate,"statement_history":self.memory['statement_history']}
        elif self.role == 'seer':
            vote_info = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"statement_history":self.memory['statement_history'],"investigate_history":self.memory['investigate_history']}  
        elif self.role == 'witch' or self.role == 'villager':
            # 村民和女巫的 speech_msg_context 內容相同
            vote_info = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"statement_history":self.memory['statement_history']}  

        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": self.vote_prompt},
                {"role": "user", "content": action_prompt[self.role]['action_info'].format(**vote_info)},
            ]
        )
        time.sleep(2)
        answer = response.choices[0].message.content
        return answer
    
    def last_msg(self):
        if self.role == 'werewolf':
            last_msg_context = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"teammate":self.teammate,"statement_history":self.memory['statement_history']}
        elif self.role == 'seer':
            last_msg_context = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"statement_history":self.memory['statement_history'],"investigate_history":self.memory['investigate_history']}  
        elif self.role == 'witch' or self.role == 'villager':
            # 村民和女巫的 last_msg_context 內容相同
            last_msg_context = {"night":self.memory['night'],"killed_players":self.memory['kill_history'],"player_alive":self.memory['player_alive'],"potion_history":self.memory['potion_history'],"statement_history":self.memory['statement_history']}  

        response = self.client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": self.last_msg_prompt},
                {"role": "user", "content": action_prompt[self.role]['action_info'].format(**last_msg_context)},
            ]
        )
        time.sleep(2)
        answer = response.choices[0].message.content
        return answer
    