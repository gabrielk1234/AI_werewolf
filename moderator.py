from werewolves_character import WerewolfCharacter
class Moderator():
    def __init__(self, players: list[WerewolfCharacter]):
        self.night = 1
        
        self.players = players
        self.left_players = players.copy()
        
        # Initial player memory
        for player in players:
            player.memory['night'] = self.night
            player.memory['player_alive'] = [p.name for p in players if p.is_alive]
            
        # Split the players into teams
        self.good_team = [p for p in players if p.role != 'werewolf']
        self.werewolf_team = [p for p in players if p.role == 'werewolf']

    def set_vote_history(self, left_players: list[WerewolfCharacter], vote: dict):
        for player in left_players:
            if player.memory['vote_history'].get(f"night {self.night}") is None:
                player.memory['vote_history'][f"night {self.night}"] = {}
            
            # 如果投票者是自己，更改key名稱至“我”
            if player.name == list(vote.keys())[0]:
                player.memory['vote_history'][f"night {self.night}"]['我'] = list(vote.values())[0]
            else:
                player.memory['vote_history'][f"night {self.night}"][list(vote.keys())[0]] = list(vote.values())[0]

    def set_statement(self, left_players: list[WerewolfCharacter], statement: dict):
        for player in left_players:
            if player.memory['statement_history'].get(f"night {self.night}") is None:
                player.memory['statement_history'][f"night {self.night}"] = {}
            
            # 如果該發言是自己，更改key名稱至“我”
            if player.name == list(statement.keys())[0]:
                player.memory['statement_history'][f"night {self.night}"]['我'] = list(statement.values())[0]
            else:
                player.memory['statement_history'][f"night {self.night}"][list(statement.keys())[0]] = list(statement.values())[0]
            
    def set_night_status(self):
        for player in self.left_players:
            player.memory['night'] = self.night

    def set_potion_status(self, potion_type: str, person: str = None):
        for player in self.left_players: #   其他玩家的藥水知情度和女巫的不一樣
            if player.name != 'witch':
                player.memory['potion_history'][potion_type]['night'] = self.night
            else:
                player.memory['potion_history'][potion_type]['night'] = self.night
                player.memory['potion_history'][potion_type]['person'] = person

    def set_team_status(self):
        self.good_team = [p for p in self.left_players if p.role != 'werewolf']
        self.werewolf_team = [p for p in self.left_players if p.role == 'werewolf']

    def update_kill_history(self,players:list[WerewolfCharacter],killed:WerewolfCharacter,kill_type:str):
        # 更新被殺害的玩家的狀態
        killed.is_alive = False
        for player in players:
            if player.name != killed.name: # 讓其餘玩家更新被殺害的人
                if player.memory['kill_history'].get(f"night {self.night}") is None:
                    player.memory['kill_history'][f"night {self.night}"] = {}
                player.memory['kill_history'][f"night {self.night}"][killed.name] = kill_type
                player.memory['player_alive'] = [p.name for p in self.left_players if p.is_alive]
        
            