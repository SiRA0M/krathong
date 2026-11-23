# 🪷 Loy Krathong ASCII 3D Animation (กระทงดิจิทัล 3 มิติ)

โปรเจกต์สร้างแอนิเมชัน **กระทงลอยน้ำ 3 มิติ (Loy Krathong 3D)** ด้วยสมการคณิตศาสตร์และเรนเดอร์ในรูปแบบ **ASCII / Matrix Glow Particle** โดยใช้ภาษา **Python**

---

## 🌟 ฟีเจอร์เด่น
- **โมเดลกลีบบัว 3 มิติ (`lotus_petal`)**: คำนวณความโค้งเว้าของกลีบดอกบัวด้วยสมการตรีโกณมิติ วางเรียงซ้อนกัน 4 ชั้น
- **ฐานใบตอง & ธูปเทียน**: จำลองฐานกระทงใบตองและเทียนพร้อมเปลวไฟที่สั่นไหวแบบไดนามิก (Flickering Candle Flame)
- **ผิวน้ำ & แสงสะท้อน**: คลื่นน้ำและแสงสะท้อนของกระทงและดวงจันทร์ระยิบระยับ
- **พระจันทร์เต็มดวงและโคมลอย**: บรรยากาศคืนวันเพ็ญเดือน 12
- **รองรับ 2 รูปแบบ**:
  1. `krathong_ascii.py` — รันใน Terminal / VS Code ด้วยสี TrueColor 24-bit
  2. `krathong_web.html` — เปิดดูบนเว็บเบราว์เซอร์ได้ทันที สามารถใช้เมาส์คลิกลากหมุนดูรอบทิศ 360 องศาได้

---

## 🚀 วิธีเปิดใช้งานใน VS Code

1. เปิดโปรแกรม **VS Code**
2. ไปที่เมนู **File** -> **Open Folder...** แล้วเลือกโฟลเดอร์:
   ```
   C:\Users\Administrator\Documents\GitHub\krathong
   ```
3. เปิดไฟล์ `krathong_ascii.py`
4. เปิด Terminal ใน VS Code (`Ctrl + ~`) แล้วรันคำสั่ง:
   ```bash
   python krathong_ascii.py
   ```
   *(กด `Ctrl + C` เพื่อหยุดการทำงาน)*

---

## 🌐 วิธีเปิดดูแบบ Interactive (Web)
ดับเบิลคลิกเปิดไฟล์ `krathong_web.html` ใน Google Chrome / Edge หรือเปิดด้วย Extension **Live Server** ใน VS Code

---

## 📦 วิธี Push ขึ้น GitHub ผ่าน GitHub Desktop

1. เปิดโปรแกรม **GitHub Desktop**
2. ไปที่เมนู **File** -> **Add Local Repository...** (หรือกด `Ctrl + O`)
3. กดปุ่ม **Choose...** แล้วเลือกโฟลเดอร์:
   ```
   C:\Users\Administrator\Documents\GitHub\krathong
   ```
4. กดปุ่ม **Add Repository**
5. ตรวจสอบไฟล์ที่มุมซ้ายล่าง พิมพ์ Summary เช่น `Initial commit: Loy Krathong 3D ASCII` แล้วกด **Commit to main**
6. กดปุ่ม **Publish repository** เพื่อนำขึ้น GitHub ของคุณได้ทันที!
