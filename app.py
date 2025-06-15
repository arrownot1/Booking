import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, time
import hashlib
import io
from PIL import Image
import base64

# กำหนดค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบจองห้องกิจกรรม",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ฟังก์ชันสำหรับการเชื่อมต่อฐานข้อมูล
def init_database():
    conn = sqlite3.connect('room_booking.db')
    c = conn.cursor()
    
    # สร้างตารางผู้ใช้
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  full_name TEXT NOT NULL,
                  room_number TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  status TEXT NOT NULL,
                  profile_image BLOB,
                  approval_status TEXT DEFAULT 'pending',
                  is_admin INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # สร้างตารางห้อง
    c.execute('''CREATE TABLE IF NOT EXISTS rooms
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  open_time TEXT NOT NULL,
                  close_time TEXT NOT NULL,
                  max_duration INTEGER NOT NULL,
                  advance_booking_hours INTEGER NOT NULL,
                  min_people INTEGER NOT NULL,
                  max_people INTEGER NOT NULL,
                  special_conditions TEXT,
                  is_active INTEGER DEFAULT 1)''')
    
    # สร้างตารางการจอง
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  room_id INTEGER NOT NULL,
                  booking_date TEXT NOT NULL,
                  start_time TEXT NOT NULL,
                  end_time TEXT NOT NULL,
                  people_count INTEGER NOT NULL,
                  contact_name TEXT NOT NULL,
                  contact_room TEXT NOT NULL,
                  contact_phone TEXT NOT NULL,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  FOREIGN KEY (room_id) REFERENCES rooms (id))''')
    
    # เพิ่มข้อมูลห้องเริ่มต้น
    rooms_data = [
        ("Brain Storming room", "06:00", "21:00", 1, 3, 2, 5, "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง"),
        ("E-Sport room", "06:00", "21:00", 1, 3, 1, 3, "จำกัดผู้ใช้งาน ไม่เกิน 3 เครื่อง ต่อครั้ง จากทั้งหมด 8 เครื่อง"),
        ("Pool Table", "06:00", "21:00", 1, 3, 1, 4, "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง"),
        ("Music & Dance room", "06:00", "21:00", 1, 3, 1, 5, "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง"),
        ("Meeting C", "06:00", "21:00", 1, 120, 5, 12, "จองก่อนใช้งานจริง 5 วัน"),
        ("Movie & Karaoke", "07:00", "21:00", 2, 3, 1, 7, "จองได้ครั้งละ 2 ชั่วโมง/ครั้ง")
    ]
    
    for room in rooms_data:
        c.execute("INSERT OR IGNORE INTO rooms (name, open_time, close_time, max_duration, advance_booking_hours, min_people, max_people, special_conditions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", room)
    
    # สร้างผู้ดูแลระบบเริ่มต้น
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, full_name, room_number, phone, status, approval_status, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              ("admin", admin_password, "ผู้ดูแลระบบ", "ADMIN", "000-000-0000", "ผู้ดูแลระบบ", "approved", 1))
    
    conn.commit()
    conn.close()

# ฟังก์ชันสำหรับการเข้ารหัสรหัสผ่าน
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ฟังก์ชันสำหรับการตรวจสอบการล็อกอิน
def authenticate_user(username, password):
    conn = sqlite3.connect('room_booking.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT * FROM users WHERE (username = ? OR phone = ?) AND password = ?", (username, username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user

# ฟังก์ชันสำหรับการแปลงรูปภาพเป็น base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ฟังก์ชันสำหรับการแสดงรายการห้อง
def display_rooms():
    conn = sqlite3.connect('room_booking.db')
    rooms_df = pd.read_sql_query("SELECT * FROM rooms WHERE is_active = 1", conn)
    conn.close()
    
    st.title("🏢 รายการห้องกิจกรรม")
    
    for _, room in rooms_df.iterrows():
        with st.expander(f"📍 {room['name']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"⏰ **เวลาเปิด:** {room['open_time']} - {room['close_time']} น.")
                st.write(f"⏱️ **ระยะเวลาจอง:** {room['max_duration']} ชั่วโมง/ครั้ง")
                st.write(f"📅 **จองล่วงหน้า:** {room['advance_booking_hours']} ชั่วโมง")
                st.write(f"👥 **จำนวนผู้ใช้:** {room['min_people']} - {room['max_people']} คน")
                if room['special_conditions']:
                    st.write(f"📋 **เงื่อนไข:** {room['special_conditions']}")
            
            with col2:
                if st.session_state.get('user_id'):
                    if st.button(f"จองห้อง", key=f"book_{room['id']}"):
                        st.session_state.selected_room = room['id']
                        st.session_state.page = 'booking_form'
                        st.rerun()
                else:
                    if st.button(f"จองห้อง", key=f"book_{room['id']}"):
                        st.warning("กรุณาเข้าสู่ระบบก่อนทำการจอง")
                        st.session_state.page = 'login'
                        st.rerun()

# ฟังก์ชันสำหรับการสมัครสมาชิก
def register_page():
    st.title("📝 สมัครสมาชิก")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("ชื่อผู้ใช้ *")
            password = st.text_input("รหัสผ่าน *", type="password")
            full_name = st.text_input("ชื่อ-นามสกุล *")
            
        with col2:
            room_number = st.text_input("ห้องเลขที่ (เช่น 54/999) *")
            phone = st.text_input("เบอร์โทรศัพท์ *")
            status = st.selectbox("สถานะ *", ["ผู้เช่า", "เจ้าของ"])
        
        profile_image = st.file_uploader("อัพโหลดรูปภาพสำหรับยืนยันตัวตน", type=['png', 'jpg', 'jpeg'])
        
        submitted = st.form_submit_button("สมัครสมาชิก")
        
        if submitted:
            if not all([username, password, full_name, room_number, phone]):
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                conn = sqlite3.connect('room_booking.db')
                c = conn.cursor()
                
                # ตรวจสอบชื่อผู้ใช้ซ้ำ
                c.execute("SELECT username FROM users WHERE username = ?", (username,))
                if c.fetchone():
                    st.error("ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาเลือกชื่อใหม่")
                else:
                    image_data = None
                    if profile_image:
                        image = Image.open(profile_image)
                        image_data = image_to_base64(image)
                    
                    hashed_password = hash_password(password)
                    c.execute("""INSERT INTO users (username, password, full_name, room_number, phone, status, profile_image)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                             (username, hashed_password, full_name, room_number, phone, status, image_data))
                    conn.commit()
                    conn.close()
                    
                    st.success("สมัครสมาชิกสำเร็จ! กรุณารอการอนุมัติจากผู้ดูแลระบบ")
                    st.session_state.page = 'login'
                    st.rerun()

# ฟังก์ชันสำหรับการเข้าสู่ระบบ
def login_page():
    st.title("🔐 เข้าสู่ระบบ")
    
    # ตรวจสอบว่ามีข้อมูลการจำรหัสผ่านหรือไม่
    saved_username = st.session_state.get('saved_username', '')
    saved_password = st.session_state.get('saved_password', '')
    
    with st.form("login_form"):
        username = st.text_input("ชื่อผู้ใช้หรือเบอร์โทรศัพท์", value=saved_username)
        password = st.text_input("รหัสผ่าน", type="password", value=saved_password)
        remember_me = st.checkbox("จดจำรหัสผ่าน")
        
        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button("เข้าสู่ระบบ")
        with col2:
            register_button = st.form_submit_button("สมัครสมาชิก")
    
    if login_submitted:
        if username and password:
            user = authenticate_user(username, password)
            if user:
                if user[8] == 'approved':  # approval_status
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.full_name = user[3]
                    st.session_state.is_admin = user[9]
                    
                    if remember_me:
                        st.session_state.saved_username = username
                        st.session_state.saved_password = password
                    
                    st.success(f"เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ {user[3]}")
                    st.session_state.page = 'dashboard'
                    st.rerun()
                elif user[8] == 'pending':
                    st.warning("บัญชีของคุณยังไม่ได้รับการอนุมัติ กรุณารอการอนุมัติจากผู้ดูแลระบบ")
                else:  # rejected
                    st.error("การลงทะเบียนของคุณถูกปฏิเสธ")
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            st.error("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
    
    if register_button:
        st.session_state.page = 'register'
        st.rerun()

# ฟังก์ชันสำหรับการสร้างช่วงเวลา
def generate_time_slots(open_time, close_time, duration):
    slots = []
    start = datetime.strptime(open_time, "%H:%M")
    end = datetime.strptime(close_time, "%H:%M")
    
    current = start
    while current + timedelta(hours=duration) <= end:
        slot_end = current + timedelta(hours=duration)
        slots.append((current.strftime("%H:%M"), slot_end.strftime("%H:%M")))
        current += timedelta(hours=duration)
    
    return slots

# ฟังก์ชันสำหรับการตรวจสอบช่วงเวลาว่าง
def get_available_slots(room_id, booking_date):
    conn = sqlite3.connect('room_booking.db')
    c = conn.cursor()
    
    # ดึงข้อมูลห้อง
    c.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    room = c.fetchone()
    
    # ดึงการจองที่มีอยู่แล้ว
    c.execute("""SELECT start_time, end_time FROM bookings 
                WHERE room_id = ? AND booking_date = ? AND status != 'cancelled'""",
             (room_id, booking_date))
    booked_slots = c.fetchall()
    
    conn.close()
    
    # สร้างช่วงเวลาทั้งหมด
    all_slots = generate_time_slots(room[2], room[3], room[4])  # open_time, close_time, max_duration
    
    # กรองช่วงเวลาที่ว่าง
    available_slots = []
    for slot in all_slots:
        is_available = True
        for booked in booked_slots:
            if not (slot[1] <= booked[0] or slot[0] >= booked[1]):
                is_available = False
                break
        if is_available:
            available_slots.append(f"{slot[0]} - {slot[1]}")
    
    return available_slots

# ฟังก์ชันสำหรับฟอร์มจองห้อง
def booking_form():
    room_id = st.session_state.get('selected_room')
    if not room_id:
        st.error("ไม่พบข้อมูลห้องที่เลือก")
        return
    
    conn = sqlite3.connect('room_booking.db')
    c = conn.cursor()
    c.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    room = c.fetchone()
    
    # ดึงข้อมูลผู้ใช้
    c.execute("SELECT * FROM users WHERE id = ?", (st.session_state.user_id,))
    user = c.fetchone()
    conn.close()
    
    st.title(f"📅 จองห้อง: {room[1]}")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # วันที่จอง
            min_date = datetime.now().date()
            if room[5] > 24:  # ถ้าต้องจองล่วงหน้ามากกว่า 24 ชั่วโมง
                min_date = min_date + timedelta(days=room[5]//24)
            
            booking_date = st.date_input("วันที่จอง", min_value=min_date)
            
            # ช่วงเวลา
            available_slots = get_available_slots(room_id, booking_date.strftime("%Y-%m-%d"))
            if available_slots:
                time_slot = st.selectbox("ช่วงเวลา", available_slots)
            else:
                st.warning("ไม่มีช่วงเวลาว่างในวันที่เลือก")
                time_slot = None
            
            people_count = st.number_input(f"จำนวนผู้เข้าใช้งาน ({room[6]}-{room[7]} คน)", 
                                         min_value=room[6], max_value=room[7], value=room[6])
        
        with col2:
            contact_name = st.text_input("ชื่อผู้ติดต่อ", value=user[3])
            contact_room = st.text_input("ห้องเลขที่", value=user[4])
            contact_phone = st.text_input("เบอร์โทรศัพท์", value=user[5])
        
        submitted = st.form_submit_button("ยืนยันการจอง")
        
        if submitted and time_slot:
            # ตรวจสอบเงื่อนไขการจอง
            now = datetime.now()
            booking_datetime = datetime.combine(booking_date, datetime.strptime(time_slot.split(' - ')[0], "%H:%M").time())
            
            # ตรวจสอบเวลาล่วงหน้า
            if booking_datetime - now < timedelta(hours=room[5]):
                st.error(f"ต้องจองล่วงหน้าอย่างน้อย {room[5]} ชั่วโมง")
                return
            
            # ตรวจสอบการจองซ้ำของผู้ใช้ในห้องเลขที่เดียวกัน
            conn = sqlite3.connect('room_booking.db')
            c = conn.cursor()
            
            start_time, end_time = time_slot.split(' - ')
            
            c.execute("""SELECT b.id FROM bookings b 
                        JOIN users u ON b.user_id = u.id 
                        WHERE u.room_number = ? AND b.booking_date = ? 
                        AND NOT (b.end_time <= ? OR b.start_time >= ?) 
                        AND b.status != 'cancelled'""",
                     (user[4], booking_date.strftime("%Y-%m-%d"), start_time, end_time))
            
            if c.fetchone():
                st.error("ผู้ใช้ในห้องเลขที่เดียวกันมีการจองในช่วงเวลานี้แล้ว")
                conn.close()
                return
            
            # สร้างการจอง
            c.execute("""INSERT INTO bookings (user_id, room_id, booking_date, start_time, end_time, 
                        people_count, contact_name, contact_room, contact_phone)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (st.session_state.user_id, room_id, booking_date.strftime("%Y-%m-%d"),
                      start_time, end_time, people_count, contact_name, contact_room, contact_phone))
            
            conn.commit()
            conn.close()
            
            st.success("จองห้องสำเร็จ! รอการอนุมัติจากผู้ดูแลระบบ")
            st.session_state.page = 'dashboard'
            st.rerun()

# ฟังก์ชันสำหรับ Dashboard ผู้ใช้
def user_dashboard():
    st.title(f"👋 ยินดีต้อนรับ, {st.session_state.full_name}")
    
    tab1, tab2, tab3 = st.tabs(["การจองของฉัน", "โปรไฟล์", "จองห้องใหม่"])
    
    with tab1:
        st.subheader("📋 การจองของฉัน")
        
        conn = sqlite3.connect('room_booking.db')
        bookings_df = pd.read_sql_query("""
            SELECT b.*, r.name as room_name 
            FROM bookings b 
            JOIN rooms r ON b.room_id = r.id 
            WHERE b.user_id = ? 
            ORDER BY b.booking_date DESC, b.start_time DESC
        """, conn, params=(st.session_state.user_id,))
        conn.close()
        
        if not bookings_df.empty:
            for _, booking in bookings_df.iterrows():
                with st.expander(f"{booking['room_name']} - {booking['booking_date']} {booking['start_time']}-{booking['end_time']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**สถานะ:** {booking['status']}")
                        st.write(f"**จำนวนคน:** {booking['people_count']} คน")
                        st.write(f"**ผู้ติดต่อ:** {booking['contact_name']}")
                    
                    with col2:
                        st.write(f"**ห้องเลขที่:** {booking['contact_room']}")
                        st.write(f"**เบอร์โทร:** {booking['contact_phone']}")
                        st.write(f"**วันที่สร้าง:** {booking['created_at']}")
                    
                    with col3:
                        if booking['status'] == 'pending':
                            if st.button(f"ยกเลิกการจอง", key=f"cancel_{booking['id']}"):
                                conn = sqlite3.connect('room_booking.db')
                                c = conn.cursor()
                                c.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking['id'],))
                                conn.commit()
                                conn.close()
                                st.success("ยกเลิกการจองสำเร็จ")
                                st.rerun()
        else:
            st.info("ยังไม่มีการจอง")
    
    with tab2:
        st.subheader("👤 โปรไฟล์")
        
        conn = sqlite3.connect('room_booking.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (st.session_state.user_id,))
        user = c.fetchone()
        conn.close()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**ชื่อผู้ใช้:** {user[1]}")
            st.write(f"**ชื่อ-นามสกุล:** {user[3]}")
            st.write(f"**ห้องเลขที่:** {user[4]}")
        
        with col2:
            st.write(f"**เบอร์โทร:** {user[5]}")
            st.write(f"**สถานะ:** {user[6]}")
            st.write(f"**สถานะการอนุมัติ:** {user[8]}")
        
        if user[7]:  # profile_image
            try:
                image_data = base64.b64decode(user[7])
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption="รูปโปรไฟล์", width=200)
            except:
                st.write("ไม่สามารถแสดงรูปภาพได้")
    
    with tab3:
        display_rooms()

# ฟังก์ชันสำหรับ Admin Dashboard
def admin_dashboard():
    st.title("🔧 ผู้ดูแลระบบ")
    
    tab1, tab2, tab3, tab4 = st.tabs(["จัดการการจอง", "จัดการผู้ใช้", "จัดการห้อง", "รายงาน"])
    
    with tab1:
        st.subheader("📋 จัดการการจอง")
        
        conn = sqlite3.connect('room_booking.db')
        bookings_df = pd.read_sql_query("""
            SELECT b.*, r.name as room_name, u.full_name as user_name 
            FROM bookings b 
            JOIN rooms r ON b.room_id = r.id 
            JOIN users u ON b.user_id = u.id 
            ORDER BY b.created_at DESC
        """, conn)
        conn.close()
        
        if not bookings_df.empty:
            for _, booking in bookings_df.iterrows():
                with st.expander(f"{booking['room_name']} - {booking['user_name']} - {booking['booking_date']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ห้อง:** {booking['room_name']}")
                        st.write(f"**ผู้จอง:** {booking['user_name']}")
                        st.write(f"**วันที่:** {booking['booking_date']}")
                        st.write(f"**เวลา:** {booking['start_time']}-{booking['end_time']}")
                    
                    with col2:
                        st.write(f"**จำนวนคน:** {booking['people_count']}")
                        st.write(f"**ผู้ติดต่อ:** {booking['contact_name']}")
                        st.write(f"**เบอร์โทร:** {booking['contact_phone']}")
                        st.write(f"**สถานะ:** {booking['status']}")
                    
                    with col3:
                        new_status = st.selectbox("อัปเดตสถานะ", 
                                                 ["pending", "approved", "rejected", "cancelled"],
                                                 index=["pending", "approved", "rejected", "cancelled"].index(booking['status']),
                                                 key=f"status_{booking['id']}")
                        
                        if st.button("อัปเดต", key=f"update_{booking['id']}"):
                            conn = sqlite3.connect('room_booking.db')
                            c = conn.cursor()
                            c.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking['id']))
                            conn.commit()
                            conn.close()
                            st.success("อัปเดตสถานะสำเร็จ")
                            st.rerun()
                        
                        if st.button("ลบ", key=f"delete_{booking['id']}"):
                            conn = sqlite3.connect('room_booking.db')
                            c = conn.cursor()
                            c.execute("DELETE FROM bookings WHERE id = ?", (booking['id'],))
                            conn.commit()
                            conn.close()
                            st.success("ลบการจองสำเร็จ")
                            st.rerun()
    
    with tab2:
        st.subheader("👥 จัดการผู้ใช้")
        
        conn = sqlite3.connect('room_booking.db')
        users_df = pd.read_sql_query("SELECT * FROM users WHERE is_admin = 0", conn)
        conn.close()
        
        for _, user in users_df.iterrows():
            with st.expander(f"{user['full_name']} ({user['username']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                                        st.write(f"**ชื่อผู้ใช้:** {user['username']}")
                    st.write(f"**ชื่อ-นามสกุล:** {user['full_name']}")
                    st.write(f"**ห้องเลขที่:** {user['room_number']}")
                    st.write(f"**เบอร์โทร:** {user['phone']}")
                
                with col2:
                    st.write(f"**สถานะ:** {user['status']}")
                    st.write(f"**สถานะการอนุมัติ:** {user['approval_status']}")
                    st.write(f"**วันที่สมัคร:** {user['created_at']}")
                    
                    if user['profile_image']:
                        try:
                            image_data = base64.b64decode(user['profile_image'])
                            image = Image.open(io.BytesIO(image_data))
                            st.image(image, caption="รูปโปรไฟล์", width=100)
                        except:
                            st.write("ไม่สามารถแสดงรูปภาพได้")
                
                with col3:
                    new_approval = st.selectbox("สถานะการอนุมัติ", 
                                               ["pending", "approved", "rejected"],
                                               index=["pending", "approved", "rejected"].index(user['approval_status']),
                                               key=f"approval_{user['id']}")
                    
                    if st.button("อัปเดต", key=f"update_user_{user['id']}"):
                        conn = sqlite3.connect('room_booking.db')
                        c = conn.cursor()
                        c.execute("UPDATE users SET approval_status = ? WHERE id = ?", (new_approval, user['id']))
                        conn.commit()
                        conn.close()
                        st.success("อัปเดตสถานะสำเร็จ")
                        st.rerun()
                    
                    if st.button("ลบผู้ใช้", key=f"delete_user_{user['id']}"):
                        conn = sqlite3.connect('room_booking.db')
                        c = conn.cursor()
                        c.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                        c.execute("DELETE FROM bookings WHERE user_id = ?", (user['id'],))
                        conn.commit()
                        conn.close()
                        st.success("ลบผู้ใช้สำเร็จ")
                        st.rerun()
    
    with tab3:
        st.subheader("🏢 จัดการห้อง")
        
        # เพิ่มห้องใหม่
        with st.expander("➕ เพิ่มห้องใหม่"):
            with st.form("add_room_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    room_name = st.text_input("ชื่อห้อง")
                    open_time = st.time_input("เวลาเปิด", value=time(6, 0))
                    close_time = st.time_input("เวลาปิด", value=time(21, 0))
                
                with col2:
                    max_duration = st.number_input("ระยะเวลาจองสูงสุด (ชั่วโมง)", min_value=1, value=1)
                    advance_hours = st.number_input("จองล่วงหน้า (ชั่วโมง)", min_value=1, value=3)
                    min_people = st.number_input("จำนวนคนขั้นต่ำ", min_value=1, value=1)
                    max_people = st.number_input("จำนวนคนสูงสุด", min_value=1, value=5)
                
                special_conditions = st.text_area("เงื่อนไขพิเศษ")
                
                if st.form_submit_button("เพิ่มห้อง"):
                    if room_name:
                        conn = sqlite3.connect('room_booking.db')
                        c = conn.cursor()
                        c.execute("""INSERT INTO rooms (name, open_time, close_time, max_duration, 
                                    advance_booking_hours, min_people, max_people, special_conditions)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (room_name, open_time.strftime("%H:%M"), close_time.strftime("%H:%M"),
                                  max_duration, advance_hours, min_people, max_people, special_conditions))
                        conn.commit()
                        conn.close()
                        st.success("เพิ่มห้องสำเร็จ")
                        st.rerun()
                    else:
                        st.error("กรุณากรอกชื่อห้อง")
        
        # แสดงรายการห้องทั้งหมด
        conn = sqlite3.connect('room_booking.db')
        rooms_df = pd.read_sql_query("SELECT * FROM rooms", conn)
        conn.close()
        
        for _, room in rooms_df.iterrows():
            with st.expander(f"🏢 {room['name']} ({'เปิดใช้งาน' if room['is_active'] else 'ปิดใช้งาน'})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**เวลาเปิด-ปิด:** {room['open_time']} - {room['close_time']}")
                    st.write(f"**ระยะเวลาจอง:** {room['max_duration']} ชั่วโมง")
                    st.write(f"**จองล่วงหน้า:** {room['advance_booking_hours']} ชั่วโมง")
                
                with col2:
                    st.write(f"**จำนวนคน:** {room['min_people']} - {room['max_people']} คน")
                    if room['special_conditions']:
                        st.write(f"**เงื่อนไขพิเศษ:** {room['special_conditions']}")
                
                with col3:
                    # สวิตช์เปิด/ปิดห้อง
                    is_active = st.checkbox("เปิดใช้งาน", 
                                           value=bool(room['is_active']), 
                                           key=f"active_{room['id']}")
                    
                    if st.button("อัปเดต", key=f"update_room_{room['id']}"):
                        conn = sqlite3.connect('room_booking.db')
                        c = conn.cursor()
                        c.execute("UPDATE rooms SET is_active = ? WHERE id = ?", (int(is_active), room['id']))
                        conn.commit()
                        conn.close()
                        st.success("อัปเดตห้องสำเร็จ")
                        st.rerun()
                    
                    if st.button("ลบห้อง", key=f"delete_room_{room['id']}"):
                        conn = sqlite3.connect('room_booking.db')
                        c = conn.cursor()
                        c.execute("DELETE FROM rooms WHERE id = ?", (room['id'],))
                        c.execute("DELETE FROM bookings WHERE room_id = ?", (room['id'],))
                        conn.commit()
                        conn.close()
                        st.success("ลบห้องสำเร็จ")
                        st.rerun()
    
    with tab4:
        st.subheader("📊 รายงาน")
        
        # สถิติการจอง
        conn = sqlite3.connect('room_booking.db')
        
        # จำนวนการจองตามสถานะ
        status_df = pd.read_sql_query("""
            SELECT status, COUNT(*) as count 
            FROM bookings 
            GROUP BY status
        """, conn)
        
        if not status_df.empty:
            st.subheader("📈 สถิติการจองตามสถานะ")
            st.bar_chart(status_df.set_index('status'))
        
        # การจองตามห้อง
        room_booking_df = pd.read_sql_query("""
            SELECT r.name, COUNT(b.id) as booking_count 
            FROM rooms r 
            LEFT JOIN bookings b ON r.id = b.room_id 
            GROUP BY r.id, r.name
        """, conn)
        
        if not room_booking_df.empty:
            st.subheader("🏢 การจองตามห้อง")
            st.bar_chart(room_booking_df.set_index('name'))
        
        # ส่งออกข้อมูล Excel
        st.subheader("📥 ส่งออกข้อมูล")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("ส่งออกข้อมูลการจอง"):
                bookings_export_df = pd.read_sql_query("""
                    SELECT b.id, r.name as room_name, u.full_name as user_name, 
                           b.booking_date, b.start_time, b.end_time, b.people_count,
                           b.contact_name, b.contact_room, b.contact_phone, b.status, b.created_at
                    FROM bookings b 
                    JOIN rooms r ON b.room_id = r.id 
                    JOIN users u ON b.user_id = u.id 
                    ORDER BY b.created_at DESC
                """, conn)
                
                # แสดงตารางข้อมูล
                st.dataframe(bookings_export_df)
        
        with col2:
            if st.button("ส่งออกข้อมูลผู้ใช้"):
                users_export_df = pd.read_sql_query("""
                    SELECT id, username, full_name, room_number, phone, status, 
                           approval_status, created_at
                    FROM users 
                    WHERE is_admin = 0
                    ORDER BY created_at DESC
                """, conn)
                
                # แสดงตารางข้อมูล
                st.dataframe(users_export_df)
        
        conn.close()

# ฟังก์ชันหลัก
def main():
    # เริ่มต้นฐานข้อมูล
    init_database()
    
    # เริ่มต้น session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    # แสดง Sidebar
    with st.sidebar:
        st.title("🏢 ระบบจองห้องกิจกรรม")
        
        if st.session_state.user_id:
            st.success(f"เข้าสู่ระบบแล้ว: {st.session_state.full_name}")
            
            if st.session_state.is_admin:
                if st.button("🔧 ผู้ดูแลระบบ"):
                    st.session_state.page = 'admin_dashboard'
                    st.rerun()
            
            if st.button("📊 Dashboard"):
                st.session_state.page = 'dashboard'
                st.rerun()
            
            if st.button("🏠 หน้าแรก"):
                st.session_state.page = 'home'
                st.rerun()
            
            if st.button("🚪 ออกจากระบบ"):
                # ล้าง session state
                for key in list(st.session_state.keys()):
                    if key not in ['saved_username', 'saved_password']:
                        del st.session_state[key]
                st.session_state.page = 'home'
                st.rerun()
        else:
            if st.button("🏠 หน้าแรก"):
                st.session_state.page = 'home'
                st.rerun()
            
            if st.button("🔐 เข้าสู่ระบบ"):
                st.session_state.page = 'login'
                st.rerun()
            
            if st.button("📝 สมัครสมาชิก"):
                st.session_state.page = 'register'
                st.rerun()
        
        # แสดงสถิติพื้นฐาน
        st.markdown("---")
        st.subheader("📊 สถิติระบบ")
        
        conn = sqlite3.connect('room_booking.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
        user_count = c.fetchone()[0]
        st.metric("ผู้ใช้ทั้งหมด", user_count)
        
        c.execute("SELECT COUNT(*) FROM rooms WHERE is_active = 1")
        room_count = c.fetchone()[0]
        st.metric("ห้องที่เปิดใช้งาน", room_count)
        
        c.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
        pending_bookings = c.fetchone()[0]
        st.metric("การจองรออนุมัติ", pending_bookings)
        
        conn.close()
    
    # แสดงเนื้อหาหลักตามหน้าที่เลือก
    if st.session_state.page == 'home':
        display_rooms()
    elif st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    elif st.session_state.page == 'dashboard':
        if st.session_state.user_id:
            user_dashboard()
        else:
            st.error("กรุณาเข้าสู่ระบบก่อน")
            st.session_state.page = 'login'
            st.rerun()
    elif st.session_state.page == 'admin_dashboard':
        if st.session_state.user_id and st.session_state.is_admin:
            admin_dashboard()
        else:
            st.error("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
            st.session_state.page = 'home'
            st.rerun()
    elif st.session_state.page == 'booking_form':
        if st.session_state.user_id:
            booking_form()
        else:
            st.error("กรุณาเข้าสู่ระบบก่อน")
            st.session_state.page = 'login'
            st.rerun()

# เพิ่ม CSS สำหรับแต่งหน้าตา
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stExpander > div > div > div > div {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stMetric > div {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

