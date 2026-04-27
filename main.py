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

# 2. สั่งให้ Gemini สรุปข่าว (แบบตื้อจนกว่าจะได้)
prompt = """
ช่วยสรุปข่าวอัปเดตเกี่ยวกับ สัตว์ป่าทั่วโลก ที่สำคัญ 5 ข่าวล่าสุดให้หน่อย
ขอแบบอ่านง่าย สรุปกระชับ พร้อมระบุแหล่งอ้างอิงท้ายข่าว
"""

news_summary = ""
attempt = 1

print("เริ่มการทำงานของ Routine...")

while True:
    try:
        print(f"กำลังพยายามดึงข้อมูลจาก Gemini... (ครั้งที่ {attempt})")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        news_summary = response.text
        
        if news_summary:
            print("🎉 สำเร็จ! ได้รับข้อมูลสรุปข่าวแล้ว")
            break # ถ้าได้ข้อมูลแล้ว ให้หลุดออกจาก Loop ทันที
            
    except (errors.ServerError, Exception) as e:
        # ถ้าเป็น ServerError (503) หรือ Error อื่นๆ ให้รอแล้วลองใหม่
        print(f"⚠️ พบปัญหา: {str(e)}")
        print("เซิร์ฟเวอร์อาจจะยุ่งหรือขัดข้อง จะรอ 60 วินาทีแล้วลองใหม่นะครับ...")
        time.sleep(60) # รอ 1 นาที
        attempt += 1

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
    "messages": [{"type": "text", "text": f"📰 สรุปข่าวสัตว์ป่าประจำวันที่ {today_str}\n\n{news_summary}"}]
}

try:
    res = requests.post(line_url, headers=headers, json=payload)
    print("LINE API Status:", res.status_code)
except Exception as e:
    print(f"ส่ง LINE ไม่สำเร็จ: {str(e)}")
