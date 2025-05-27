from fpdf import FPDF

class GameLogPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("noto", "", "fonts/NotoSansTC-Regular.ttf", uni=True)

    def header(self):
        self.set_font("noto", size=20)
        self.cell(0, 10, "遊戲記錄", ln=True, align="C")
        self.ln(5)
        
    def write(self,content:dict):
        safe_text = content["value"]
        if content["type"] == "system":
            self.set_text_color(100, 100, 100)
            self.set_font("noto", size=11)
            self.multi_cell(0, 6, f"[系統] {safe_text}", ln=True)
        elif content["type"] == "player":
            self.set_text_color(0, 0, 0)
            self.set_font("noto", size=12)

            self.multi_cell(0, 6, f"[{content['player_name']}] {safe_text}", ln=True)
        elif content["type"] == "god":
            self.set_text_color(200, 0, 0)
            self.set_font("noto", "", 11)
            self.multi_cell(0, 6, f"[上帝視角] {safe_text}", ln=True)