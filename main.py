import os
import requests
import datetime
import time
from google import genai
from google.genai import errors

# ==========================================
# 1. ตั้งค่าตัวแปร (Environment Variables)
# ==========================================
gemini_api_key = os.environ.get("GEMINI_API_KEY")
line_token = os.environ.get("LINE_CHANNEL_TOKEN")
line_user_id = os.environ.get("LINE_USER_ID")

client = genai.Client(api_key=gemini_api_key)
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 2. เตรียมข้อมูลประวัติเปเปอร์ที่เคยสรุปไปแล้ว
# ==========================================
history_file = "paper_history.txt"
try:
    with open(history_file, "r", encoding="utf-8") as f:
        past_papers = f.read().strip()
        if not past_papers:
            past_papers = "ยังไม่มีงานวิจัยที่เคยสรุป"
except FileNotFoundError:
    past_papers = "ยังไม่มีงานวิจัยที่เคยสรุป"

# ==========================================
# 3. กำหนด Prompt สำหรับให้ Gemini สรุปงานวิจัย
# ==========================================
prompt = f"""
ทำหน้าที่เป็นผู้ช่วยนักวิจัยระดับปริญญาเอกด้านนิเวศวิทยาสัตว์ป่า (Wildlife Ecology Research Assistant)

ช่วยค้นหาและสรุปงานวิจัย (Paper) ล่าสุดที่ตีพิมพ์ในช่วงปี 2025-2026 จำนวน 1 เรื่อง โดยมีเงื่อนไขดังต่อไปนี้:

1. ขอบเขตเนื้อหา: เน้นงานวิจัยที่เกี่ยวข้องกับการสร้างแบบจำลองถิ่นที่อยู่อาศัย (Habitat Suitability Modeling), การประเมินมวลชีวภาพของพืชอาหาร (Forage Biomass Estimation), หรือการติดตามประชากรสัตว์ป่า (เช่น วัวแดง, กระทิง, หมูป่า, หรือช้างเอเชีย) ซึ่งมีการประยุกต์ใช้เทคโนโลยีภาพถ่ายดาวเทียม (Remote Sensing), โดรน (UAV), หรือ Machine Learning
2. เงื่อนไขสำคัญ: ห้าม นำเสนองานวิจัยที่ซ้ำกับรายชื่อที่เคยสรุปไปแล้วดังต่อไปนี้โดยเด็ดขาด:
{past_papers}

3. รูปแบบการสรุปที่ต้องการ (ไม่ต้องใช้สัญลักษณ์ Markdown เช่น เครื่องหมายดอกจัน หรือ ชาร์ป):
ชื่อเรื่อง (Title) & ปีที่ตีพิมพ์:
วัตถุประสงค์หลัก (Core Objective): งานนี้ต้องการแก้ปัญหาหรือหาคำตอบเรื่องอะไร?
ระเบียบวิธีวิจัย (Methodology): สรุปเทคนิคที่ใช้ (เช่น อัลกอริทึม, ตัวแปรเชิงพื้นที่, หรือวิธีการเก็บข้อมูล) แบบกระชับ
ผลการศึกษาที่สำคัญ (Key Findings): ค้นพบอะไรที่น่าสนใจบ้าง?
จุดเด่นและการประยุกต์ใช้ (Application): งานวิจัยนี้มีประโยชน์อย่างไรต่อการจัดการพื้นที่อนุรักษ์ หรือสามารถนำมาต่อยอดได้อย่างไร?
"""

paper_summary = ""
attempt = 1
max_attempts = 5

print("เริ่มการทำงานของ Routine อัปเดตเปเปอร์วิจัย...")

# ==========================================
# 4. ดึงข้อมูลจาก Gemini API (พร้อมระบบ Retry)
# ==========================================
while attempt <= max_attempts:
    try:
        print(f"กำลังพยายามดึงข้อมูลจาก Gemini... (ครั้งที่ {attempt}/{max_attempts})")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        paper_summary = response.text
        
        if paper_summary:
            print("🎉 สำเร็จ! ได้รับข้อมูลสรุปเปเปอร์แล้ว")
            break
            
    except errors.APIError as e:
        print(f"⚠️ พบปัญหาจาก Gemini API ({e.code}): {e.message}")
        if e.code and e.code < 500:
            print("❌ เป็นความผิดพลาดฝั่ง Client (เช่น Key ผิด) ยุติการทำงานทันที")
            break
        print("เซิร์ฟเวอร์อาจจะยุ่ง จะรอ 60 วินาทีแล้วลองใหม่...")
        time.sleep(60)
        attempt += 1
    except Exception as e:
        print(f"⚠️ พบปัญหาอื่นๆ: {str(e)}")
        time.sleep(60)
        attempt += 1

if not paper_summary:
    print("❌ ไม่สามารถดึงข้อมูลเปเปอร์ได้ ระบบจบทำงาน")
    exit()

# ==========================================
# 5. บันทึกชื่อเรื่องลง History เพื่อกันการซ้ำซ้อนในอนาคต
# ==========================================
try:
    # ดึงเฉพาะบรรทัดแรกที่มักจะเป็นชื่อเรื่องมาใช้บันทึก
    first_line = paper_summary.strip().split('\n')[0]
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{first_line}\n")
except Exception as e:
    print(f"⚠️ ไม่สามารถบันทึกประวัติลง history ได้: {str(e)}")

# ==========================================
# 6. บันทึกผลลัพธ์ฉบับเต็มลงไฟล์ Markdown
# ==========================================
file_name = f"paper_summary_{today_str}.md"
with open(file_name, "w", encoding="utf-8") as f:
    f.write(paper_summary)

# ==========================================
# 7. ส่งข้อความเข้า LINE Messaging API
# ==========================================
full_message = f"🎓 อัปเดตเปเปอร์วิจัยใหม่ประจำวันที่ {today_str}\n\n{paper_summary}"

# ตรวจสอบขีดจำกัดจำนวนตัวอักษรของ LINE (สูงสุด 5000 ตัวอักษร)
if len(full_message) > 4900:
    full_message = full_message[:4900] + "\n\n...(ข้อความยาวเกินขีดจำกัด โปรดอ่านรายละเอียดเต็มในไฟล์ .md)"

line_url = "https://api.line.me/v2/bot/message/push"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {line_token}"
}
payload = {
    "to": line_user_id,
    "messages": [{"type": "text", "text": full_message}]
}

try:
    res = requests.post(line_url, headers=headers, json=payload)
    if res.status_code == 200:
        print("🎉 ส่งรายงานเปเปอร์วิจัยเข้า LINE สำเร็จ!")
    else:
        print(f"❌ LINE API ตอบกลับด้วยสถานะ: {res.status_code} - {res.text}")
except Exception as e:
    print(f"❌ ส่ง LINE ไม่สำเร็จเนื่องจากเกิด Error: {str(e)}")
