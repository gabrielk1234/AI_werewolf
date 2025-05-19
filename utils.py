# 抓取json内容
import json
import re

def extract_json(text):
    try:
        # 嘗試直接載入
        return json.loads(text)
    except:
        # 用正則抓 JSON 區塊
        match = re.search(r'\{[\s\S]*?\}', text)
        if match:
            try:
                return json.loads(match.group())
            except:
                print(("無法解析 JSON:", match.group()))
                return None
    return None