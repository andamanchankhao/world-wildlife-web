import os
import requests
import datetime
from google import genai

# 1. ตั้งค่าตัวแปร
gemini_api_key = os.environ.get("GEMINI_API_KEY")
line_token = os.environ.get("LINE_CHANNEL_TOKEN")
line_user_id = os.environ.get("LINE_USER_ID")

# ตั้งค่า Client ของ Google GenAI
client = genai.Client(api_key=gemini_api_key)
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

# 2. สั่งให้ Gemini สรุปข่าว
prompt = """
ช่วยสรุปข่าวอัปเดตเกี่ยวกับ AI ที่สำคัญ 5 ข่าวล่าสุดให้หน่อย
ขอแบบอ่านง่าย สรุปกระชับ พร้อมระบุแหล่งอ้างอิงท้ายข่าว
"""

# เรียกใช้โมเดลเวอร์ชันใหม่
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
)
news_summary = response.text

# 3. บันทึกผลลัพธ์ลงไฟล์ .md
file_name = f"news_{today_str}.md"
with open(file_name, "w", encoding="utf-8") as f:
    f.write(news_summary)

# 4. ส่งข้อความเข้า LINE Messaging API
line_url = "https://api.line.me/v2/bot/message/push"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {line_token}"
}
payload = {
    "to": line_user_id,
    "messages": [{"type": "text", "text": f"📰 สรุปข่าว AI ประจำวันที่ {today_str}\n\n{news_summary}"}]
}

res = requests.post(line_url, headers=headers, json=payload)
print("LINE API Status:", res.status_code)