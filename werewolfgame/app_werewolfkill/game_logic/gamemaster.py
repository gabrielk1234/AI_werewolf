import random
import json

from app_werewolfkill.game_logic.werewolves_character import WerewolfCharacter
from app_werewolfkill.game_logic.moderator import Moderator
from app_werewolfkill.game_logic.utils import extract_json

""" 
回傳信息種類（type）
system：系統訊息
god：上帝視角
player：玩家發言or投票
"""
class GameMaster():
    def __init__(self,messages):
        # Game Record Initialize
        names = ['Alex','Anson','Bob','Charlie','Diana','Eve']
        random.shuffle(names)
        
        self.wolf1 = WerewolfCharacter(name="Alex", role="werewolf", teammate="Anson")
        self.wolf2 = WerewolfCharacter(name="Anson", role="werewolf", teammate="Alex")
        self.villager1 = WerewolfCharacter(name="Bob", role="villager")
        self.villager2 = WerewolfCharacter(name="Charlie", role="villager")
        self.seer = WerewolfCharacter(name="Diana", role="seer")
        self.witch = WerewolfCharacter(name="Eve", role="witch")
        
        # self.wolf1 = WerewolfCharacter(name=names.pop(), role="werewolf", teammate="Anson")
        # self.wolf2 = WerewolfCharacter(name=names.pop(), role="werewolf", teammate="Alex")
        # self.villager1 = WerewolfCharacter(name=names.pop(), role="villager")
        # self.villager2 = WerewolfCharacter(name=names.pop(), role="villager")
        # self.seer = WerewolfCharacter(name=names.pop(), role="seer")
        # self.witch = WerewolfCharacter(name=names.pop(), role="witch")

        self.moderator = Moderator([self.wolf1, self.wolf2, self.villager1, self.villager2, self.seer, self.witch])
        self.messages = messages

        # Inital Status
        self.end = False
        self.used_heal = False # 這晚是否使用解藥了？
        self.killed_dict = {} # 這晚被殺害的人是？
        self.potion_status = {} # 女巫的解藥和毒藥是否被用過了

    def game_start(self):
        messages_to_send = [
            {'type': 'system', 'value': self.messages['game_start']},
            {'type': 'system', 'value': self.messages['distribute_chac']}
        ]
        return messages_to_send
    
    def night_routine(self,first_night=True):
        # Set Status
        self.moderator.set_night_status() # 設定玩家天數狀態
        self.used_heal = False # 這晚用過解藥了嗎
        self.killed_dict = {}
        random.shuffle(self.moderator.left_players)
        
        msg = {'type':'system','value':self.messages['night'] + "今天是第" + str(self.moderator.night) + "晚\n"}
        yield msg

        if self.moderator.night == 1:
            msg = {'type':'system','value':self.messages['wolf_stage1']}
            yield msg
        
        # Get The potion status
        self.potion_status = {'has_heal':self.witch.has_heal_potion, 'has_poison':self.witch.has_poison_potion}

        # Wolf Action
        wolf_act,kill_target,reason = self.wolf_action()
        msg = {'type':'god','value':wolf_act,'reason':reason} # 狼人選擇殺人目標
        yield msg

        # Seer Action
        msg = {'type':'system','value':self.messages['seer_stage1']}
        yield msg
        if self.seer.is_alive:
            seer_act = self.seer_action()
            msg = {'type':'god','value':seer_act} # 預言家查驗
        else: # 預言家已經死了的情況下
            seer_act = self.messages['seer_stage2'].format('...')
            msg = {'type':'god','value':seer_act} # 預言家查驗
        yield msg

        # Witch Action
        msg = {'type':'system','value':self.messages['witch_stage1']}
        yield msg        
        msg = {'type':'god','value':self.messages['witch_stage1_god'].format(player=kill_target.name)}
        yield msg

        # Heal Stage
        witch_heal_msg = self.witch_action_heal(kill_target)
        msg = {'type':'god','value':witch_heal_msg}
        yield msg

        # 女巫是否要用毒藥
        msg = {'type':'system','value':self.messages['witch_stage2']}
        yield msg

        # Poison Stage
        witch_poison_msg = self.witch_action_poison(kill_target)
        msg = {'type':'god','value':witch_poison_msg}
        yield msg

        # Day ....
        msg = {'type':'system','value':self.messages['day']}
        yield msg

        # Renew left player dict
        killed_list = self.renew_killed_list()
        for content in killed_list:
            if len(content) == 3: # player message
                msg = {'type':content[0],'player_name':content[1],'value':content[2]}
            else:
                msg = {'type':content[0],'value':content[1]}
            yield msg

        # Confirm is Game Over?
        msg = {'type':'god','value':f"good_team:{len(self.moderator.good_team)}, werewolf_team:{len(self.moderator.werewolf_team)}"}
        yield msg
        
        if (len(self.moderator.werewolf_team) >= len(self.moderator.good_team)) or len(self.moderator.werewolf_team) == 0:
            msg = {'type':'system','value':self.messages['game_over'].format(winner="werewolves" if len(self.moderator.werewolf_team) >= len(self.moderator.good_team) else "good_team")}
            self.end = True
            yield msg
        
        if not self.end:
            # 發言階段，從剩餘玩家開始發言
            for content in self.speech_stage():
                if len(content) == 3: # player message
                    msg = {'type':content[0],'player_name':content[1],'value':content[2]}
                    yield msg
                else:
                    msg = {'type':content[0],'value':content[1]}
                    yield msg

            # 投票階段
            for content in self.vote_stage():
                if len(content) == 3:
                    msg = {'type':content[0],'player_name':content[1],'value':content[2]}
                else:
                    msg = {'type':content[0],'value':content[1]}
                yield msg
                
            self.moderator.night += 1

    def vote_stage(self):
        yield 'system',self.messages['vote_stage1']
        vote_dict = {player: 0 for player in self.moderator.left_players}
        for player in self.moderator.left_players:
            response = player.vote()
            response = extract_json(response)
            vote_target = response['vote_target']
            vote_target = [p for p in self.moderator.left_players if p.name == vote_target][0]
            vote_dict[vote_target] += 1

            if vote_target.name not in [player.name for player in self.moderator.left_players]:
                print(f"{player.name}選擇的投票目標不在存活名單中")
                AssertionError(f"{player.name}選擇的投票目標不在存活名單中")

            # 儲存投票記錄
            statement = {player.name: vote_target.name}
            self.moderator.set_vote_history(self.moderator.left_players,statement)
        # 計算投票結果
        yield 'system',"投票結果為：\n" + '，'.join([f"{player.name}:{vote}" for player,vote in vote_dict.items()])
        out_player = max(vote_dict,key=vote_dict.get)
        yield 'system',self.messages['vote_stage3'].format(player=out_player.name)

        # 被投玩家發表遺言
        yield 'system',self.messages['last_msg'].format(player=out_player.name)
        last_msg = out_player.last_msg()
        # 儲存遺言記錄
        statement = {out_player.name: last_msg}
        self.moderator.set_statement(self.moderator.left_players,statement)
        yield 'player',out_player.name,last_msg

        # 更新被投票玩家的狀態
        self.moderator.update_kill_history(self.moderator.left_players,out_player, '被投票出局')

    def speech_stage(self):
        # 發言階段，從剩餘玩家開始發言
        random.shuffle(self.moderator.left_players)
        for player in self.moderator.left_players:
            yield 'system',self.messages['speech'].format(player=player.name)

            speech = player.speak()
            # 儲存發言記錄
            statement = {player.name: speech}
            self.moderator.set_statement(self.moderator.left_players,statement)
            yield 'player',player.name,speech
        yield 'system',self.messages['speech_end']

    def wolf_action(self):
        # Werewolf action --------------------------------------
        rdm_wolf = random.choice(self.moderator.werewolf_team)
        response = rdm_wolf.night_action(potion_status=self.potion_status)
        
        try:
            # print(response) # 查看狼人選擇的邏輯 (for testing)
            result = extract_json(response)
            reason = result['reason']
            kill_target = result['kill_target']
            kill_target = [player for player in self.moderator.left_players if player.name == kill_target][0]
            if kill_target.name not in [player.name for player in self.moderator.left_players]:
                print(f"{rdm_wolf.name}選擇的殺人目標不在存活名單中")
                assert False,f"{rdm_wolf.name}選擇的殺人目標不在存活名單中"
            
            return f"{rdm_wolf.name}選擇了{kill_target.name}作為殺人目標",kill_target,reason
        except json.JSONDecodeError as e:
            print("狼人-殺人步驟解析錯誤")
            print(response)
            assert e
        # werewolf action end -----------------------------------

    def seer_action(self):
        # seer action --------------------------------------
        response = self.seer.night_action()
        try:
            # print(response) # 查看預言家選擇的邏輯
            
            investigate_target = extract_json(response)['investigate_target']
            if investigate_target not in [player.name for player in self.moderator.left_players]:
                print(f"{self.seer.name}選擇的查驗目標不在存活名單中")
                assert False,f"{self.seer.name}選擇的查驗目標不在存活名單中"
            
            # 查驗結果
            if investigate_target in [player.name for player in self.moderator.werewolf_team]:
                result = "werewolf"
            else:
                result = "goodteam"
            
            # 將查驗結果寫入預言家的記憶中
            self.seer.memory['investigate_history'].append({investigate_target:result})
            return self.messages['seer_stage2'].format(investigate_target)
        except json.JSONDecodeError as e:
            print("預言家-查驗步驟解析錯誤")
            print(response)
            assert e
        # seer action end -----------------------------------

    def witch_action_heal(self,kill_target):
        # witch action --------------------------------------
        if self.witch.is_alive and self.witch.has_heal_potion: # 女巫還活著且有解藥的情況下
            response = self.witch.night_action(killed_player=kill_target.name, potion_type='heal')
            try:
                # print(response) # 查看女巫選擇的邏輯

                self.use_heal = extract_json(response)['use_heal']
                if self.use_heal: # 女巫選擇使用解藥
                    # 更新解藥狀態
                    self.witch.has_heal_potion = False
                    self.witch.memory['potion_history']['heal']['person'] = kill_target.name
                    self.witch.memory['potion_history']['heal']['night'] = self.moderator.night
                    self.moderator.set_potion_status(potion_type='heal')

                    msg = f"女巫{self.witch.name}選擇使用了解藥，救了{kill_target.name}"
                    self.used_heal = True
                else: # 女巫選擇不使用解藥
                    msg = f"女巫{self.witch.name}選擇不使用解藥"
                    self.killed_dict[kill_target] = '被狼人殺死'

            except json.JSONDecodeError as e:
                print("女巫-救人步驟解析錯誤")
                print(response)
                assert e
        elif self.witch.is_alive and not self.witch.has_heal_potion: # 女巫還活著，但沒有解藥的情況下
            msg = "女巫沒有解藥了"
            self.killed_dict[kill_target] = '被狼人殺死'

        elif not self.witch.is_alive:
            msg = "女巫已經被殺了，無法使用解藥"
            self.killed_dict[kill_target] = '被狼人殺死'


        return msg

        
    def witch_action_poison(self,kill_target):  
        if self.witch.is_alive and self.witch.has_poison_potion and not self.used_heal: # 女巫還活著，有毒藥，以及這局沒使用過解藥的情況下
            response = self.witch.night_action(killed_player=kill_target.name, potion_type='poison')
            try:
                # print(response) # 查看女巫選擇毒藥的邏輯
                response = extract_json(response)
                use_poison = response['use_poison']
                poison_target = response['poison_target']
                if use_poison:
                    if poison_target not in [player.name for player in self.moderator.left_players]:
                        print(f"女巫選擇的毒藥目標不在存活名單中")
                        assert False,f"女巫選擇的毒藥目標不在存活名單中"
                    poison_target = [player for player in self.moderator.left_players if player.name == poison_target][0]
                    self.killed_dict[poison_target] = '被毒殺'
                    # 更新毒藥狀態
                    self.moderator.set_potion_status(potion_type='poison',person=poison_target.name)
                    self.witch.has_poison_potion = False
                    msg = f"女巫{self.witch.name}選擇使用了毒藥，毒死了{poison_target.name}"
                    return msg
                else:
                    return "女巫不選擇使用毒藥"
            except json.JSONDecodeError as e:
                print("女巫-毒藥步驟解析錯誤")
                print(response)
                assert e

        elif not self.witch.is_alive:
            return "女巫已經被殺了，無法使用毒藥"
        
        else:
            return "女巫已經使用過解藥了"
           
    def renew_killed_list(self):
        # 更新狀態，如果有2個人死亡，只有女巫和狼人知道死因
        if len(self.killed_dict) > 1:
            roles = [player for player in self.moderator.left_players if (player.role == 'werewolf') or (player.role == 'witch')]
            roles_other = [player for player in self.moderator.left_players if (player.role != 'werewolf') and (player.role != 'witch')]
            for killed_player, kill_reason in self.killed_dict.items():
                self.moderator.update_kill_history(roles,killed_player, kill_reason)
                self.moderator.update_kill_history(roles_other,killed_player, '不確定被狼人殺死或者是被毒殺')
            yield ('system',self.messages['killed'].format(player=','.join([player.name for player in self.killed_dict.keys()])))
            
        elif len(self.killed_dict) == 1:# 只有一個人死亡
            for killed_player, kill_reason in self.killed_dict.items():
                self.moderator.update_kill_history(self.moderator.left_players,killed_player, kill_reason)
            yield ('system',self.messages['killed'].format(player=','.join([player.name for player in self.killed_dict.keys()])))
        else: # 沒有死亡
            yield ('system',self.messages['safe'])
        
        # 更新存活名單
        self.moderator.left_players = [player for player in self.moderator.left_players if player.is_alive]
        self.moderator.set_team_status()

        # 第一晚遺言階段（第一晚被毒被殺才有遺言）
        if self.moderator.night == 1:
            for killed_p in self.killed_dict.keys():
                yield ('system',self.messages['last_msg'].format(player=killed_p.name))

                last_msg = killed_p.last_msg()
                # 儲存遺言記錄
                statement = {killed_p.name: last_msg}
                self.moderator.set_statement(self.moderator.left_players,statement)
                yield 'player',killed_p.name,last_msg
        

