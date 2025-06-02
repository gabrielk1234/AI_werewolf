# 🐺 AI Werewolf Game  
👤 作者：龔玖恩（F113118131）  
🏫 國立高雄科技大學 資訊管理研究所碩士班一年級  

本專案是「生成式 AI」課程的期末作品，主題為結合 **Gemini API** 的狼人殺遊戲，透過 AI 進行推理與對話，模擬真實狼人殺對局。

---

## 🔑 註冊 Gemini API 金鑰

前往官方網站申請：  
👉 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

**設定環境變數（Windows CMD）：**
```bash
setx GEMINI_API_KEY your_api_key_here
```

**確認是否設定成功：**
```bash
echo %GEMINI_API_KEY%
```

## 🛠️ 安裝教學
**1️⃣ 建立虛擬環境（使用 Conda）**
```bash
conda create --name werewolf python=3.10.0
conda activate werewolf
```

**2️⃣ 下載專案**
```bash
git clone https://github.com/gabrielk1234/AI_werewolf.git
cd AI_werewolf/
```

**3️⃣ 安裝相依套件**
```bash
pip install -r .\requirement.txt
```

**4️⃣ 啟動伺服器**
```bash
cd werewolfgame
daphne werewolfgame.asgi:application
```

**For any question： email F113118131@nkust.edu.tw**
