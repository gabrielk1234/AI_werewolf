import yaml
import time
import random
import json

from openai import OpenAI
from config import api_key,system_prompt
from werewolves_character import WerewolfCharacter
from moderator import Moderator
from utils import extract_json

# Load Message
with open("message.yaml", "r", encoding="utf-8") as f:
    messages = yaml.safe_load(f)

wolf1 = WerewolfCharacter(name="Alex", role="werewolf", teammate="Anson")
wolf2 = WerewolfCharacter(name="Anson", role="werewolf", teammate="Alex")
villager1 = WerewolfCharacter(name="Bob", role="villager")
villager2 = WerewolfCharacter(name="Charlie", role="villager")
seer = WerewolfCharacter(name="Diana", role="seer")
witch = WerewolfCharacter(name="Eve", role="witch")

moderator = Moderator([wolf1, wolf2, villager1, villager2, seer, witch])

# Game Start
print(messages['game_start'])
print(messages['distribute_chac'])

while True:
    # Set Status
    moderator.set_night_status()
    use_heal = False
    killed_dict = {}
    # Day and Night Cycle
    print(messages['night'] + "今天是第" + str(moderator.night) + "晚")
    if moderator.night == 1:
        print(messages['wolf_stage1'])
    
    # Get The potion status
    potion_status = {'has_heal':witch.has_heal_potion, 'has_poison':witch.has_poison_potion}
    
    # Random selection of the werewolf
    rdm_wolf = random.choice(moderator.werewolf_team)
    response = rdm_wolf.night_action(potion_status=potion_status)
    
    # Werewolf action --------------------------------------
    try:
        print(response) # 查看狼人選擇的邏輯
        
        kill_target = extract_json(response)['kill_target']
        kill_target = [player for player in moderator.left_players if player.name == kill_target][0]
        if kill_target.name not in [player.name for player in moderator.left_players]:
            print(f"{rdm_wolf.name}選擇的殺人目標不在存活名單中")
            
        print(f"{rdm_wolf.name}選擇了{kill_target.name}作為殺人目標")
    except json.JSONDecodeError:
        print("狼人-殺人步驟解析錯誤")
        print(response)
    # werewolf action end -----------------------------------

    # seer action --------------------------------------
    print(messages['seer_stage1'])
    if seer.is_alive: #預言家還活著的情況下
        response = seer.night_action()
        try:
            # print(response) # 查看預言家選擇的邏輯
            
            investigate_target = extract_json(response)['investigate_target']
            if investigate_target not in [player.name for player in moderator.left_players]:
                print(f"{seer.name}選擇的查驗目標不在存活名單中")
                
            print(messages['seer_stage2'].format(investigate_target))
            # 查驗結果
            if investigate_target in [player.name for player in moderator.werewolf_team]:
                result = "werewolf"
            else:
                result = "goodteam"
            
            # 將查驗結果寫入預言家的記憶中
            seer.memory['investigate_history'].append({investigate_target:result})
        except json.JSONDecodeError:
            print("預言家-查驗步驟解析錯誤")
            print(response)
    else: # 預言家已經死了的情況下
        print(messages['seer_stage2'].format('...'))
    # seer action end -----------------------------------

    # witch action --------------------------------------
    print(messages['witch_stage1'].format(player=kill_target.name))
    if witch.is_alive and witch.has_heal_potion: # 女巫還活著且有解藥的情況下
        response = witch.night_action(killed_player=kill_target.name, potion_type='heal')
        try:
            print(response) # 查看女巫選擇的邏輯

            use_heal = extract_json(response)['use_heal']
            if use_heal: # 女巫選擇使用解藥
                # 更新解藥狀態
                witch.has_heal_potion = False
                witch.memory['potion_history']['heal']['person'] = kill_target.name
                witch.memory['potion_history']['heal']['night'] = moderator.night
                moderator.set_potion_status(potion_type='heal')

                print(f"女巫{witch.name}選擇使用了解藥，救了{kill_target.name}")

            else: # 女巫選擇不使用解藥
                print(f"女巫{witch.name}選擇不使用解藥")
                killed_dict[kill_target] = '被狼人殺死'
        except json.JSONDecodeError:
            print("女巫-救人步驟解析錯誤")
            print(response)
    elif witch.is_alive and not witch.has_heal_potion: # 女巫還活著，但沒有解藥的情況下
        print("女巫沒有解藥了")
        killed_dict[kill_target] = '被狼人殺死'

    print(messages['witch_stage2'])
    
    if witch.is_alive and witch.has_poison_potion and not use_heal: # 女巫還活著，有毒藥，以及沒使用過解藥的情況下
        response = witch.night_action(killed_player=kill_target.name, potion_type='poison')
        try:
            print(response) # 查看女巫選擇的邏輯
            response = extract_json(response)
            use_poison = response['use_poison']
            poison_target = response['poison_target']
            if use_poison:
                if poison_target not in [player.name for player in moderator.left_players]:
                    print(f"{witch.name}選擇的毒藥目標不在存活名單中")
                poison_target = [player for player in moderator.left_players if player.name == poison_target][0]
                killed_dict[poison_target] = '被毒殺'
                # 更新毒藥狀態
                moderator.set_potion_status(potion_type='poison',person=poison_target.name)
                witch.has_poison_potion = False
                print(f"女巫{witch.name}選擇使用了毒藥，毒死了{poison_target.name}")
        except json.JSONDecodeError:
            print("女巫-毒藥步驟解析錯誤")
            print(response)
    
    if not witch.is_alive:
        killed_dict[kill_target] = '被狼人殺死'
    
    print(messages['day'])
            
    # 更新狀態，如果有2個人死亡，只有女巫和狼人知道死因
    if len(killed_dict) > 1:
        roles = [player for player in moderator.left_players if (player.role == 'werewolf') or (player.role == 'witch')]
        roles_other = [player for player in moderator.left_players if (player.role != 'werewolf') and (player.role != 'witch')]
        for killed_player, kill_reason in killed_dict.items():
            moderator.update_kill_history(roles,killed_player, kill_reason)
            moderator.update_kill_history(roles_other,killed_player, '不確定被狼人殺死或者是被毒殺')
        print(messages['killed'].format(player=','.join([player.name for player in killed_dict.keys()])))
        
    elif len(killed_dict) == 1:# 只有一個人死亡
        for killed_player, kill_reason in killed_dict.items():
            moderator.update_kill_history(moderator.left_players,killed_player, kill_reason)
        print(messages['killed'].format(player=','.join([player.name for player in killed_dict.keys()])))
    else: # 沒有死亡
        print(messages['safe'])
        
    # 第一晚遺言階段（第一晚被毒被殺才有遺言）
    if moderator.night == 1:
        for killed_p in killed_dict.keys():
            print(messages['last_msg'].format(player=player.name))

            last_msg = killed_p.last_msg()
            # 儲存遺言記錄
            statement = {killed_p.name: last_msg}
            moderator.set_statement(moderator.left_players,statement)
            print(last_msg)

    # 更新存活名單
    moderator.left_players = [player for player in moderator.left_players if player.is_alive]
    moderator.set_team_status()

    # 確認游戲是否結束
    print(f"good_team:{len(moderator.good_team)}, werewolf_team:{len(moderator.werewolf_team)}")
    if (len(moderator.werewolf_team) >= len(moderator.good_team)) or len(moderator.werewolf_team) == 0:
        print(messages['game_over'].format(winner="werewolves" if len(moderator.werewolf_team) >= len(moderator.good_team) else "good_team"))
        break

    # 發言階段，從剩餘玩家開始發言
    for player in moderator.left_players:
        print(messages['speech'].format(player=player.name))

        speech = player.speak()
        # 儲存發言記錄
        statement = {player.name: speech}
        moderator.set_statement(moderator.left_players,statement)
        print(speech)
    print(messages['speech_end'])

    # 投票階段
    print(messages['vote_stage1'])
    vote_dict = {player: 0 for player in moderator.left_players}
    for player in moderator.left_players:
        response = player.vote()
        response = extract_json(response)
        vote_target = response['vote_target']
        vote_target = [p for p in moderator.left_players if p.name == vote_target][0]
        vote_dict[vote_target] += 1

        if vote_target.name not in [player.name for player in moderator.left_players]:
            print(f"{player.name}選擇的投票目標不在存活名單中")
            AssertionError(f"{player.name}選擇的投票目標不在存活名單中")

        # 儲存投票記錄
        statement = {player.name: vote_target.name}
        moderator.set_vote_history(moderator.left_players,statement)
    # 計算投票結果
    print("投票結果為：\n" + '，'.join([f"{player.name}:{vote}" for player,vote in vote_dict.items()]))
    out_player = max(vote_dict,key=vote_dict.get)
    print(messages['vote_stage3'].format(player=out_player.name))

    # 被投玩家發表遺言
    print(messages['last_msg'].format(player=out_player.name))
    last_msg = out_player.last_msg()
    # 儲存遺言記錄
    statement = {out_player.name: last_msg}
    moderator.set_statement(moderator.left_players,statement)
    print(last_msg)

    # 更新被投票玩家的狀態
    moderator.update_kill_history(moderator.left_players,out_player, '被投票出局')
    

    moderator.night += 1
    moderator.set_night_status()