import os
import requests
import datetime
from anthropic import Anthropic

# 1. ตั้งค่าต่างๆ
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
line_token = os.environ.get("LINE_CHANNEL_TOKEN")
line_user_id = os.environ.get("LINE_USER_ID")

client = Anthropic(api_key=anthropic_api_key)
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

# 2. สั่งให้ Claude สรุปข่าว
prompt = """
ช่วยสรุปข่าวอัปเดตเกี่ยวกับ สัตว์ป่า ที่สำคัญทั่วโลก 5 ข่าวล่าสุดให้หน่อย
ขอแบบอ่านง่าย สรุปกระชับ พร้อมระบุแหล่งอ้างอิงท้ายข่าว
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}]
)
news_summary = response.content[0].text

# 3. บันทึกผลลัพธ์เก็บไว้ใน GitHub (สร้างไฟล์ .md)
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