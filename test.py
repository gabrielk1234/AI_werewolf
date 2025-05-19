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

game_is_running = True

# Game Start
print(messages['game_start'])
print(messages['distribute_chac'])

while game_is_running:
    # Set Status
    moderator.set_night_status()
    use_heal = False
    killed_dict = {}
    
    # -------------------------------Night-----------------------------------
    # Day and Night Cycle
    print(messages['night'])
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
        if kill_target not in [player.name for player in moderator.left_players]:
            print(f"{rdm_wolf.name}選擇的殺人目標不在存活名單中")
            
        print(f"{rdm_wolf.name}選擇了{kill_target}作為殺人目標")
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
    print(messages['witch_stage1'].format(player=kill_target))
    if witch.is_alive and witch.has_heal_potion: # 女巫還活著且有解藥的情況下
        response = witch.night_action(killed_player=kill_target, potion_type='heal')
        try:
            print(response) # 查看女巫選擇的邏輯

            use_heal = extract_json(response)['use_heal']
            if use_heal: # 女巫選擇使用解藥
                # 更新解藥狀態
                witch.has_heal_potion = False
                witch.memory['potion_history']['heal']['person'] = kill_target
                witch.memory['potion_history']['heal']['night'] = moderator.night
                moderator.set_potion_status(potion_type='heal')
                
                print(f"女巫{witch.name}選擇使用了解藥，救了{kill_target}")
                
            else: # 女巫選擇不使用解藥
                print(f"女巫{witch.name}選擇不使用解藥")
                killed_dict[kill_target] = 'kill_by_wolf'
        except json.JSONDecodeError:
            print("女巫-救人步驟解析錯誤")
            print(response)

    print(messages['witch_stage2'])
    
    if witch.is_alive and witch.has_poison_potion and not use_heal: # 女巫還活著，有毒藥，以及沒使用過解藥的情況下
        response = witch.night_action(killed_player=kill_target, potion_type='poison')
        try:
            # print(response) # 查看女巫選擇的邏輯
            response = extract_json(response)
            use_poison = response['use_poison']
            poison_target = response['poison_target']
            if use_poison:
                if poison_target not in [player.name for player in moderator.left_players]:
                    print(f"{witch.name}選擇的毒藥目標不在存活名單中")
                poison_target = [player for player in moderator.left_players if player.name == poison_target][0].name
                killed_dict[poison_target] = 'kill_by_poison'
                # 更新毒藥狀態
                moderator.set_potion_status(potion_type='poison',person=poison_target)
                witch.has_poison_potion = False
                print(f"女巫{witch.name}選擇使用了毒藥，毒死了{poison_target}")
        except json.JSONDecodeError:
            print("女巫-毒藥步驟解析錯誤")
            print(response)
            
    # -------------------------------Night End--------------------------------
    
    # --------------------------------Day-----------------------------------
    print(messages['day'])
            
    # 更新狀態，如果有2個人死亡，只有女巫和狼人知道死因
    if len(killed_dict) > 1:
        roles = [player for player in moderator.left_players if (player.role == 'werewolf') or (player.role == 'witch')]
        roles_other = [player for player in moderator.left_players if (player.role != 'werewolf') and (player.role != 'witch')]
        for killed_player, kill_reason in killed_dict.items():
            moderator.update_kill_history(roles,killed_player, kill_reason)
            moderator.update_kill_history(roles_other,killed_player, '不確定被狼人殺死或者是被毒殺')

        print(messages['killed'].format(player=','.join([player.name for player in killed_dict.keys()])))
        print()
    elif len(killed_dict) == 1:# 只有一個人死亡
        for killed_player, kill_reason in killed_dict.items():
            moderator.update_kill_history(moderator.left_players,killed_player, kill_reason)
        print(messages['killed'].format(player=','.join([player.name for player in killed_dict.keys()])))
    else: # 沒有死亡
        print(messages['safe'])
    break

    if (len(moderator.werewolf_team) >= len(moderator.good_team)) or len(moderator.werewolf_team) == 0:
        game_is_running = False
        print(messages['game_over'].format(winner="werewolves" if len(moderator.werewolf_team) >= len(moderator.good_team) else "good_team"))