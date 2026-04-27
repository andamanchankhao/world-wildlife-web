import os
import requests
import datetime
import time
from google import genai
from google.genai import errors

# 1. ตั้งค่าตัวแปร
gemini_api_key = os.environ.get("GEMINI_API_KEY")
line_token = os.environ.get("LINE_CHANNEL_TOKEN")
line_user_id = os.environ.get("LINE_USER_ID")

client = genai.Client(api_key=gemini_api_key)
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

# 2. สั่งให้ Gemini สรุปข่าว (พร้อมระบบ Retry ป้องกันเซิร์ฟเวอร์ยุ่ง)
prompt = """
ช่วยสรุปข่าวอัปเดตเกี่ยวกับ AI ที่สำคัญ 5 ข่าวล่าสุดให้หน่อย
ขอแบบอ่านง่าย สรุปกระชับ พร้อมระบุแหล่งอ้างอิงท้ายข่าว
"""

max_retries = 3
news_summary = ""

for attempt in range(max_retries):
    try:
        print(f"กำลังเรียกใช้ Gemini... (รอบที่ {attempt + 1}/{max_retries})")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        news_summary = response.text
        print("สรุปข่าวสำเร็จ!")
        break # สำเร็จแล้วออกจาก Loop เลย
        
    except errors.ServerError as e:
        print("เซิร์ฟเวอร์ Google กำลังยุ่ง รอ 10 วินาทีแล้วลองใหม่...")
        time.sleep(10)
        if attempt == max_retries - 1:
            news_summary = "ขออภัยครับ วันนี้ระบบ AI ของ Google มีผู้ใช้งานหนาแน่นมาก ทำให้ไม่สามารถสรุปข่าวอัตโนมัติได้ครับ 😅"
    except Exception as e:
        news_summary = f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}"
        break

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