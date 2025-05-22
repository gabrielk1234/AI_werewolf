import json
import re

def extract_json(text):
    try:
        return json.loads(text)
    except Exception as e:
        # 嘗試用正則抓 JSON 區塊
        match = re.search(r'\{[\s\S]*?\}', text)
        if match:
            try:
                return json.loads(match.group())
            except Exception as e2:
                print("無法解析 JSON:", match.group())
                print("錯誤訊息:", e2)
                return None
    return None
