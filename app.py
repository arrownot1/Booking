import streamlit as st
import pandas as pd
import json
import datetime
import hashlib
import uuid
from io import BytesIO

# --- กำหนดค่าเริ่มต้นและข้อมูลห้อง (คงเดิม) ---
ROOMS_DATA = {
    "Brain Stroming room": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1, # hours
        "booking_advance_hours": 3,
        "min_users": 2,
        "max_users": 5,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 2 - 5 คน ต่อครั้ง"
    },
    "E-Sport room": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1, # hours
        "booking_advance_hours": 3,
        "max_machines": 3, # จากทั้งหมด 8 เครื่อง
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้ใช้งาน ไม่เกิน 3 เครื่อง ต่อครั้ง จากทั้งหมด 8 เครื่อง"
    },
    "Pool Table": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1, # hours
        "booking_advance_hours": 3,
        "min_users": 1,
        "max_users": 4,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 1 - 4 คน ต่อครั้ง"
    },
    "Music & Dance room": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1, # hours
        "booking_advance_hours": 3,
        "min_users": 1,
        "max_users": 5,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 1 - 5 คน ต่อครั้ง"
    },
    "Meeting C": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1, # hours
        "booking_advance_days": 5, # เปลี่ยนเป็นวัน
        "min_users": 5,
        "max_users": 12,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 5 วัน, จำกัดผู้เข้าใช้ 5 - 12 คน ต่อครั้ง"
    },
    "Movie & Karaoke": {
        "open_time": "07:00",
        "close_time": "21:00",
        "duration_per_booking": 2, # hours
        "booking_advance_hours": 3,
        "min_users": 1,
        "max_users": 7,
        "description": "จองได้ครั้งละ 2 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 1 - 7 คน ต่อครั้ง"
    }
}

# --- ไฟล์สำหรับจัดเก็บข้อมูลผู้ใช้และข้อมูลการจอง (คงเดิม) ---
USERS_FILE = 'users.json'
BOOKINGS_FILE = 'bookings.json'

# --- ฟังก์ชันช่วยจัดการข้อมูลผู้ใช้ (คงเดิม) ---
def load_users():
    """โหลดข้อมูลผู้ใช้จากไฟล์ JSON"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_users(users):
    """บันทึกข้อมูลผู้ใช้ลงในไฟล์ JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def hash_password(password):
    """เข้ารหัสรหัสผ่านด้วย SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# --- ฟังก์ชันช่วยจัดการข้อมูลการจอง (คงเดิม) ---
def load_bookings():
    """โหลดข้อมูลการจองจากไฟล์ JSON"""
    try:
        with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_bookings(bookings):
    """บันทึกข้อมูลการจองลงในไฟล์ JSON"""
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, indent=4, ensure_ascii=False)

# --- ฟังก์ชันช่วยเหลือสำหรับการล็อกอิน (คงเดิม) ---
def check_login_status():
    """ตรวจสอบสถานะการล็อกอินของผู้ใช้"""
    return st.session_state.get('logged_in', False)

def get_current_user_role():
    """รับบทบาทของผู้ใช้ปัจจุบัน"""
    return st.session_state.get('user_role', 'guest')

def get_current_username():
    """รับชื่อผู้ใช้ปัจจุบัน"""
    return st.session_state.get('username', None)

# --- หน้าหลัก (Landing Page) (คงเดิม) ---
def main_page():
    st.set_page_config(
        page_title="ระบบจองห้องกิจกรรม",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("ยินดีต้อนรับสู่ระบบจองห้องกิจกรรม")
    st.write("เลือกห้องกิจกรรมที่ต้องการเพื่อดูรายละเอียดและทำการจอง")

    st.header("รายการห้องกิจกรรม")
    cols = st.columns(2)

    for i, (room_name, room_info) in enumerate(ROOMS_DATA.items()):
        with cols[i % 2]:
            st.subheader(room_name)
            st.write(f"**เวลาเปิด:** {room_info['open_time']} - {room_info['close_time']} น.")
            st.write(f"**เงื่อนไข:** {room_info['description']}")

            if st.button(f"จองห้อง {room_name}", key=f"book_{room_name}"):
                if check_login_status():
                    users = load_users()
                    current_user_data = users.get(get_current_username())
                    if current_user_data and current_user_data.get('status') == 'approved':
                        st.session_state['current_page'] = 'booking_form'
                        st.session_state['selected_room'] = room_name
                        st.experimental_rerun()
                    elif current_user_data and current_user_data.get('status') == 'pending':
                        st.warning("บัญชีของคุณอยู่ระหว่างรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการตรวจสอบ")
                    elif current_user_data and current_user_data.get('status') == 'rejected':
                        st.error("บัญชีของคุณถูกปฏิเสธการลงทะเบียน กรุณาติดต่อผู้ดูแลระบบ")
                    else:
                        st.warning("กรุณาเข้าสู่ระบบก่อนทำการจอง")
                        st.session_state['logged_in'] = False
                        st.session_state['current_page'] = 'login'
                        st.experimental_rerun()
                else:
                    st.warning("กรุณาเข้าสู่ระบบก่อนทำการจอง")
                    st.session_state['current_page'] = 'login'
                    st.experimental_rerun()

    st.markdown("---")
    st.sidebar.title("นำทาง")
    if not check_login_status():
        if st.sidebar.button("เข้าสู่ระบบ"):
            st.session_state['current_page'] = 'login'
            st.experimental_rerun()
        if st.sidebar.button("สมัครสมาชิก"):
            st.session_state['current_page'] = 'register'
            st.experimental_rerun()
    else:
        current_username = get_current_username()
        users = load_users()
        user_data = users.get(current_username)

        if user_data:
            st.sidebar.write(f"สวัสดี, {user_data.get('full_name', current_username)}")
            if user_data.get('status') == 'approved':
                if st.sidebar.button("จัดการการจองของฉัน"):
                    st.session_state['current_page'] = 'my_bookings'
                    st.experimental_rerun()
                if get_current_user_role() == 'admin':
                    if st.sidebar.button("จัดการผู้ใช้"):
                        st.session_state['current_page'] = 'manage_users'
                        st.experimental_rerun()
                    if st.sidebar.button("จัดการห้อง"):
                        st.session_state['current_page'] = 'manage_rooms'
                        st.experimental_rerun()
                    if st.sidebar.button("ดูการจองทั้งหมด"):
                        st.session_state['current_page'] = 'admin_manage_bookings'
                        st.experimental_rerun()
            elif user_data.get('status') == 'pending':
                st.sidebar.info("บัญชีของคุณอยู่ระหว่างรอการอนุมัติ")
            elif user_data.get('status') == 'rejected':
                st.sidebar.error("บัญชีของคุณถูกปฏิเสธ")

        if st.sidebar.button("ออกจากระบบ"):
            del st.session_state['logged_in']
            if 'username' in st.session_state:
                del st.session_state['username']
            if 'user_role' in st.session_state:
                del st.session_state['user_role']
            st.session_state['current_page'] = 'main_page'
            st.info("ออกจากระบบเรียบร้อยแล้ว")
            st.experimental_rerun()

# --- หน้าเข้าสู่ระบบ (คงเดิม) ---
def login_page():
    st.title("เข้าสู่ระบบ")

    initial_username = st.session_state.get('remember_me_username', '')

    username_or_phone = st.text_input("ชื่อผู้ใช้ หรือ เบอร์โทรศัพท์", value=initial_username)
    password = st.text_input("รหัสผ่าน", type="password")

    remember_me = st.checkbox("จดจำชื่อผู้ใช้")

    if st.button("เข้าสู่ระบบ"):
        users = load_users()
        found_user = None

        if username_or_phone in users:
            found_user = users[username_or_phone]
        else:
            for user_key, user_data in users.items():
                if user_data.get('phone_number') == username_or_phone:
                    found_user = user_data
                    break

        if found_user and found_user['password'] == hash_password(password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = found_user['username']
            st.session_state['user_role'] = found_user['role']

            if remember_me:
                st.session_state['remember_me_username'] = username_or_phone
            else:
                if 'remember_me_username' in st.session_state:
                    del st.session_state['remember_me_username']

            if found_user.get('status') == 'approved':
                st.success(f"ยินดีต้อนรับ, {found_user.get('full_name', found_user['username'])}!")
                st.session_state['current_page'] = 'main_page'
                st.experimental_rerun()
            elif found_user.get('status') == 'pending':
                st.warning("บัญชีของคุณอยู่ระหว่างรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการตรวจสอบ")
                st.session_state['logged_in'] = True
                st.session_state['current_page'] = 'main_page'
                st.experimental_rerun()
            elif found_user.get('status') == 'rejected':
                st.error("บัญชีของคุณถูกปฏิเสธการลงทะเบียน กรุณาติดต่อผู้ดูแลระบบ")
                st.session_state['logged_in'] = False
                st.session_state['current_page'] = 'login'
                st.experimental_rerun()
        else:
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    st.markdown("---")
    st.write("ยังไม่มีบัญชีใช่ไหม?")
    if st.button("สมัครสมาชิก"):
        st.session_state['current_page'] = 'register'
        st.experimental_rerun()
    if st.button("กลับหน้าหลัก", key="back_from_login"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- หน้าสมัครสมาชิก (คงเดิม) ---
def register_page():
    st.title("สมัครสมาชิกใหม่")

    st.write("กรุณากรอกข้อมูลเพื่อสมัครสมาชิก:")
    new_username = st.text_input("ชื่อผู้ใช้ (ใช้สำหรับเข้าสู่ระบบ)")
    new_password = st.text_input("รหัสผ่าน", type="password")
    confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password")
    full_name = st.text_input("ชื่อ-นามสกุล")
    room_number = st.text_input("ห้องเลขที่ (เช่น 54/999)")
    phone_number = st.text_input("เบอร์โทรศัพท์ (เช่น 08XXXXXXXX)")
    user_status_options = ["ผู้เช่า", "เจ้าของ"]
    user_status = st.selectbox("สถานะ", user_status_options)
    id_photo = st.file_uploader("อัปโหลดไฟล์รูปภาพสำหรับยืนยันตัวตน (เช่น บัตรประชาชน)", type=["png", "jpg", "jpeg"])

    if st.button("สมัครสมาชิก"):
        users = load_users()
        if not new_username or not new_password or not confirm_password or not full_name or not room_number or not phone_number or not id_photo:
            st.error("กรุณากรอกข้อมูลให้ครบถ้วนและอัปโหลดรูปภาพ")
            return
        if new_password != confirm_password:
            st.error("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
            return
        if new_username in users:
            st.error("ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่อผู้ใช้อื่น")
            return
        if any(user_data.get('phone_number') == phone_number for user_data in users.values()):
            st.error("เบอร์โทรศัพท์นี้มีการลงทะเบียนแล้ว กรุณาใช้เบอร์อื่นหรือติดต่อผู้ดูแลระบบ")
            return

        users[new_username] = {
            'username': new_username,
            'password': hash_password(new_password),
            'full_name': full_name,
            'room_number': room_number,
            'phone_number': phone_number,
            'user_status': user_status,
            'id_photo_uploaded': True, # Placeholder
            'status': 'pending',
            'role': 'user'
        }
        save_users(users)
        st.success("สมัครสมาชิกสำเร็จ! โปรดรอการอนุมัติจากผู้ดูแลระบบ")
        st.session_state['current_page'] = 'login'
        st.experimental_rerun()

    st.markdown("---")
    st.write("มีบัญชีอยู่แล้วใช่ไหม?")
    if st.button("เข้าสู่ระบบ", key="login_from_register"):
        st.session_state['current_page'] = 'login'
        st.experimental_rerun()
    if st.button("กลับหน้าหลัก", key="back_from_register"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- หน้าจองห้อง (คงเดิม) ---
def booking_form_page():
    selected_room = st.session_state.get('selected_room', 'ไม่ระบุ')
    room_info = ROOMS_DATA.get(selected_room, {})
    current_username = get_current_username()
    users = load_users()
    current_user_data = users.get(current_username, {})

    st.title(f"จองห้อง: {selected_room}")
    st.write(f"**รายละเอียดห้อง:** {room_info.get('description', 'ไม่มีข้อมูล')}")

    user_full_name = st.text_input("ชื่อ-นามสกุล", value=current_user_data.get('full_name', ''), disabled=True)
    user_room_number = st.text_input("ห้องเลขที่", value=current_user_data.get('room_number', ''), disabled=True)
    user_phone_number = st.text_input("เบอร์โทรศัพท์", value=current_user_data.get('phone_number', ''), disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        booking_date = st.date_input("เลือกวันที่จอง", min_value=datetime.date.today())
    with col2:
        open_time_str = room_info.get('open_time')
        close_time_str = room_info.get('close_time')
        duration_hours = room_info.get('duration_per_booking')

        available_time_slots = []
        if open_time_str and close_time_str and duration_hours:
            open_time = datetime.datetime.strptime(open_time_str, "%H:%M").time()
            close_time = datetime.datetime.strptime(close_time_str, "%H:%M").time()

            current_datetime_for_check_advance = datetime.datetime.now()

            current_time_slot_start = datetime.datetime.combine(booking_date, open_time)

            while current_time_slot_start.time() < close_time or (current_time_slot_start.time() == open_time and current_time_slot_start.time() == close_time):
                current_time_slot_end = current_time_slot_start + datetime.timedelta(hours=duration_hours)

                if current_time_slot_end.date() > booking_date or current_time_slot_end.time() > close_time:
                    break

                is_slot_available = True
                bookings = load_bookings()
                for booking in bookings:
                    existing_booking_start_dt = datetime.datetime.strptime(f"{booking['booking_date']} {booking['start_time']}", "%Y-%m-%d %H:%M")
                    existing_booking_end_dt = datetime.datetime.strptime(f"{booking['booking_date']} {booking['end_time']}", "%Y-%m-%d %H:%M")

                    time_overlap = (current_time_slot_start < existing_booking_end_dt) and \
                                   (current_time_slot_end > existing_booking_start_dt)

                    if time_overlap and booking['status'] in ['pending', 'approved']:
                        if booking['room_name'] == selected_room:
                            is_slot_available = False
                            break

                if is_slot_available:
                    available_time_slots.append(f"{current_time_slot_start.strftime('%H:%M')} - {current_time_slot_end.strftime('%H:%M')}")
                current_time_slot_start = current_time_slot_start + datetime.timedelta(hours=duration_hours)

        if not available_time_slots:
            st.warning("ไม่มีช่วงเวลาว่างสำหรับวันที่เลือก หรือห้องปิดทำการสำหรับวันนี้")
            booking_time = st.selectbox("เลือกช่วงเวลา", ["- ไม่มีช่วงเวลาว่าง -"], disabled=True)
        else:
            booking_time = st.selectbox("เลือกช่วงเวลา", available_time_slots)

    if selected_room == "E-Sport room":
        num_users_or_machines = st.number_input(
            f"จำนวนเครื่องที่ต้องการใช้ (สูงสุด {room_info.get('max_machines', 0)} เครื่อง)",
            min_value=1,
            max_value=room_info.get('max_machines', 0),
            value=1,
            step=1
        )
    else:
        min_users = room_info.get('min_users', 1)
        max_users = room_info.get('max_users', 1)
        num_users_or_machines = st.number_input(
            f"จำนวนผู้เข้าใช้งาน (ขั้นต่ำ {min_users} คน, สูงสุด {max_users} คน)",
            min_value=min_users,
            max_value=max_users,
            value=min_users,
            step=1
        )

    if st.button("ยืนยันการจอง"):
        if not booking_date or not booking_time or booking_time == "- ไม่มีช่วงเวลาว่าง -" or not num_users_or_machines:
            st.error("กรุณากรอกข้อมูลการจองให้ครบถ้วนและเลือกช่วงเวลาที่ว่าง")
            return

        start_time_str = booking_time.split(' - ')[0]
        end_time_str = booking_time.split(' - ')[1]
        booking_datetime_start = datetime.datetime.combine(booking_date, datetime.datetime.strptime(start_time_str, "%H:%M").time())
        booking_datetime_end = datetime.datetime.combine(booking_date, datetime.datetime.strptime(end_time_str, "%H:%M").time())

        current_datetime_for_check_advance = datetime.datetime.now()
        if booking_datetime_start < current_datetime_for_check_advance:
             st.error("ไม่สามารถจองในเวลาที่ผ่านมาแล้วได้")
             return

        is_advance_ok = True
        if "booking_advance_days" in room_info:
            required_advance_date = current_datetime_for_check_advance + datetime.timedelta(days=room_info["booking_advance_days"])
            if booking_datetime_start < required_advance_date:
                st.error(f"ห้อง {selected_room} ต้องจองล่วงหน้าอย่างน้อย {room_info['booking_advance_days']} วัน (วันที่ปัจจุบันคือ {current_datetime_for_check_advance.strftime('%Y-%m-%d %H:%M')})")
                is_advance_ok = False
        elif "booking_advance_hours" in room_info:
            required_advance_time = current_datetime_for_check_advance + datetime.timedelta(hours=room_info["booking_advance_hours"])
            if booking_datetime_start < required_advance_time:
                st.error(f"ต้องจองล่วงหน้าอย่างน้อย {room_info['booking_advance_hours']} ชั่วโมง (เวลาปัจจุบันคือ {current_datetime_for_check_advance.strftime('%Y-%m-%d %H:%M')})")
                is_advance_ok = False
        if not is_advance_ok:
            return

        bookings = load_bookings()
        is_room_available = True
        is_same_house_booking_conflict = False

        for booking in bookings:
            existing_booking_start_dt = datetime.datetime.strptime(f"{booking['booking_date']} {booking['start_time']}", "%Y-%m-%d %H:%M")
            existing_booking_end_dt = datetime.datetime.strptime(f"{booking['booking_date']} {booking['end_time']}", "%Y-%m-%d %H:%M")

            time_overlap = (booking_datetime_start < existing_booking_end_dt) and \
                           (booking_datetime_end > existing_booking_start_dt)

            if time_overlap and booking['status'] in ['pending', 'approved']:
                if booking['room_name'] == selected_room:
                    is_room_available = False
                    break

                if booking['user_room_number'] == user_room_number:
                    is_same_house_booking_conflict = True
                    break

        if not is_room_available:
            st.error(f"ห้อง {selected_room} ไม่ว่างในช่วงเวลาที่เลือก กรุณาเลือกช่วงเวลาอื่น")
            return

        if is_same_house_booking_conflict:
            st.error(f"ไม่สามารถจองห้องนี้ได้ เนื่องจากห้องเลขที่ {user_room_number} มีการจองห้องอื่นในช่วงเวลาเดียวกันอยู่แล้ว")
            return

        if selected_room == "E-Sport room":
            if not (1 <= num_users_or_machines <= room_info.get('max_machines', 0)):
                st.error(f"จำนวนเครื่องต้องไม่เกิน {room_info.get('max_machines', 0)} เครื่อง และต้องมากกว่า 0")
                return
        else:
            if not (room_info.get('min_users', 0) <= num_users_or_machines <= room_info.get('max_users', 0)):
                st.error(f"จำนวนผู้เข้าใช้งานต้องอยู่ระหว่าง {room_info.get('min_users', 0)} ถึง {room_info.get('max_users', 0)} คน")
                return

        new_booking = {
            "booking_id": str(uuid.uuid4()),
            "username": current_username,
            "room_name": selected_room,
            "booking_date": booking_date.strftime("%Y-%m-%d"),
            "start_time": start_time_str,
            "end_time": end_time_str,
            "num_users_or_machines": num_users_or_machines,
            "user_full_name": user_full_name,
            "user_room_number": user_room_number,
            "user_phone_number": user_phone_number,
            "status": "pending",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        bookings.append(new_booking)
        save_bookings(bookings)
        st.success("การจองห้องสำเร็จ! โปรดรอการอนุมัติจากผู้ดูแลระบบ")
        st.session_state['current_page'] = 'my_bookings'
        st.experimental_rerun()

    st.markdown("---")
    if st.button("กลับหน้าหลัก", key="back_from_booking"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- หน้าจัดการการจองของฉัน (สำหรับผู้ใช้ทั่วไป) (คงเดิม) ---
def my_bookings_page():
    st.title("การจองของฉัน")
    current_username = get_current_username()
    users = load_users()
    current_user_data = users.get(current_username, {})

    st.subheader("ข้อมูลโปรไฟล์ของคุณ")
    st.write(f"**ชื่อผู้ใช้:** {current_user_data.get('username')}")
    st.write(f"**ชื่อ-นามสกุล:** {current_user_data.get('full_name')}")
    st.write(f"**ห้องเลขที่:** {current_user_data.get('room_number')}")
    st.write(f"**เบอร์โทรศัพท์:** {current_user_data.get('phone_number')}")
    st.write(f"**สถานะผู้ใช้:** {current_user_data.get('user_status')}")
    st.write(f"**สถานะบัญชี:** {current_user_data.get('status').capitalize()}")

    st.subheader("รายการจองห้องกิจกรรมของฉัน")
    bookings = load_bookings()
    user_bookings = [b for b in bookings if b['username'] == current_username]

    if user_bookings:
        df = pd.DataFrame(user_bookings)
        df['datetime_sort'] = pd.to_datetime(df['booking_date'] + ' ' + df['start_time'])
        df = df.sort_values(by='datetime_sort', ascending=False)
        df = df.drop(columns=['datetime_sort'])

        df_display = df[[
            'room_name', 'booking_date', 'start_time', 'end_time',
            'num_users_or_machines', 'status', 'timestamp', 'booking_id'
        ]].rename(columns={
            'room_name': 'ห้องกิจกรรม',
            'booking_date': 'วันที่จอง',
            'start_time': 'เวลาเริ่มต้น',
            'end_time': 'เวลาสิ้นสุด',
            'num_users_or_machines': 'จำนวนคน/เครื่อง',
            'status': 'สถานะ',
            'timestamp': 'เวลาที่ทำการจอง'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("ยกเลิกการจอง")
        cancellable_bookings = [
            b for b in user_bookings
            if b['status'] == 'pending' and
               (datetime.datetime.strptime(f"{b['booking_date']} {b['start_time']}", "%Y-%m-%d %H:%M") > datetime.datetime.now())
        ]

        if cancellable_bookings:
            booking_ids_to_cancel = {
                f"{b['booking_id'][:8]}... - {b['room_name']} ({b['booking_date']} {b['start_time']})" : b['booking_id']
                for b in cancellable_bookings
            }
            selected_booking_display = st.selectbox(
                "เลือกรายการจองที่ต้องการยกเลิก (เฉพาะสถานะ 'รออนุมัติ' และยังไม่ถึงเวลาจอง)",
                list(booking_ids_to_cancel.keys())
            )
            selected_booking_id = booking_ids_to_cancel.get(selected_booking_display)

            if st.button("ยืนยันการยกเลิกการจอง"):
                bookings_to_update = load_bookings()
                found_and_canceled = False
                for i, booking in enumerate(bookings_to_update):
                    if booking['booking_id'] == selected_booking_id:
                        if booking['status'] == 'pending':
                            bookings_to_update[i]['status'] = 'cancelled_by_user'
                            save_bookings(bookings_to_update)
                            st.success("ยกเลิกการจองสำเร็จแล้ว")
                            found_and_canceled = True
                            st.experimental_rerun()
                        else:
                            st.warning(f"ไม่สามารถยกเลิกการจองนี้ได้ เนื่องจากสถานะเป็น '{booking['status']}'")
                        break
                if not found_and_canceled:
                    st.error("ไม่พบรายการจองที่เลือก หรือไม่สามารถยกเลิกได้")
        else:
            st.info("ไม่มีรายการจองที่สามารถยกเลิกได้ในขณะนี้")

    else:
        st.info("คุณยังไม่มีการจองห้องกิจกรรม")

    st.markdown("---")
    if st.button("กลับหน้าหลัก"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- หน้าจัดการการจอง (สำหรับผู้ดูแลระบบ) (คงเดิม) ---
def admin_manage_bookings_page():
    st.title("จัดการการจองทั้งหมด (สำหรับผู้ดูแลระบบ)")

    bookings = load_bookings()
    users = load_users()

    if not bookings:
        st.info("ยังไม่มีรายการจองในระบบ")
        if st.button("กลับหน้าหลัก"):
            st.session_state['current_page'] = 'main_page'
            st.experimental_rerun()
        return

    df = pd.DataFrame(bookings)
    df['Full Booking Info'] = df.apply(lambda row: f"{row['room_name']} on {row['booking_date']} from {row['start_time']} to {row['end_time']} by {row['username']} (Room: {row['user_room_number']})", axis=1)

    st.subheader("รายการจองทั้งหมด")

    col_filter, col_sort = st.columns(2)
    with col_filter:
        status_filter = st.selectbox(
            "กรองตามสถานะ",
            ["ทั้งหมด", "pending", "approved", "rejected", "cancelled_by_user"],
            key="admin_booking_status_filter"
        )
    with col_sort:
        sort_by_options = {
            "วันที่จอง (ล่าสุด)": ("booking_date", "start_time", False),
            "วันที่จอง (เก่าสุด)": ("booking_date", "start_time", True),
            "สถานะ": ("status", None, True)
        }
        sort_by_display = st.selectbox(
            "เรียงลำดับตาม",
            list(sort_by_options.keys()),
            key="admin_booking_sort"
        )
        sort_col1, sort_col2, sort_asc = sort_by_options[sort_by_display]

    filtered_df = df.copy()
    if status_filter != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]

    if sort_col1 == "booking_date":
        filtered_df['sort_key'] = pd.to_datetime(filtered_df['booking_date'] + ' ' + filtered_df['start_time'])
        filtered_df = filtered_df.sort_values(by='sort_key', ascending=sort_asc).drop(columns=['sort_key'])
    else:
        filtered_df = filtered_df.sort_values(by=sort_col1, ascending=sort_asc)


    st.dataframe(filtered_df[[
        'booking_id', 'username', 'room_name', 'booking_date', 'start_time', 'end_time',
        'num_users_or_machines', 'user_full_name', 'user_room_number', 'user_phone_number',
        'status', 'timestamp'
    ]].rename(columns={
        'booking_id': 'รหัสการจอง',
        'username': 'ชื่อผู้ใช้',
        'room_name': 'ห้องกิจกรรม',
        'booking_date': 'วันที่จอง',
        'start_time': 'เวลาเริ่ม',
        'end_time': 'เวลาสิ้นสุด',
        'num_users_or_machines': 'จำนวนคน/เครื่อง',
        'user_full_name': 'ชื่อ-นามสกุลผู้จอง',
        'user_room_number': 'ห้องเลขที่ผู้จอง',
        'user_phone_number': 'เบอร์โทรผู้จอง',
        'status': 'สถานะ',
        'timestamp': 'เวลาทำรายการ'
    }), use_container_width=True, hide_index=True)


    st.markdown("---")
    st.subheader("จัดการสถานะการจอง")
    booking_ids = [b['booking_id'] for b in filtered_df.to_dict('records')]
    if booking_ids:
        selected_booking_id = st.selectbox(
            "เลือกรหัสการจองที่ต้องการจัดการ",
            booking_ids,
            key="select_booking_to_manage"
        )
        new_status = st.selectbox(
            "เปลี่ยนสถานะเป็น",
            ["pending", "approved", "rejected", "cancelled_by_user"],
            key="new_booking_status"
        )
        if st.button("อัปเดตสถานะการจอง"):
            bookings_to_update = load_bookings()
            for i, booking in enumerate(bookings_to_update):
                if booking['booking_id'] == selected_booking_id:
                    bookings_to_update[i]['status'] = new_status
                    save_bookings(bookings_to_update)
                    st.success(f"อัปเดตสถานะการจอง {selected_booking_id} เป็น '{new_status}' สำเร็จ")
                    st.experimental_rerun()
            else:
                st.error("ไม่พบรายการจองที่เลือก")
    else:
        st.info("ไม่มีรายการจองให้จัดการ")

    st.markdown("---")
    st.subheader("ลบการจอง")
    if booking_ids:
        booking_id_to_delete = st.selectbox(
            "เลือกรหัสการจองที่ต้องการลบ",
            booking_ids,
            key="select_booking_to_delete"
        )
        if st.button("ยืนยันการลบการจอง"):
            bookings_to_update = load_bookings()
            original_len = len(bookings_to_update)
            bookings_to_update = [b for b in bookings_to_update if b['booking_id'] != booking_id_to_delete]
            if len(bookings_to_update) < original_len:
                save_bookings(bookings_to_update)
                st.success(f"ลบการจอง {booking_id_to_delete} สำเร็จ")
                st.experimental_rerun()
            else:
                st.error("ไม่พบรายการจองที่เลือก")
    else:
        st.info("ไม่มีรายการจองให้ลบ")

    st.markdown("---")
    st.subheader("ส่งออกข้อมูล")
    if bookings:
        df_export = pd.DataFrame(bookings)
        df_export_final = df_export[[
            'booking_id', 'username', 'room_name', 'booking_date', 'start_time', 'end_time',
            'num_users_or_machines', 'user_full_name', 'user_room_number', 'user_phone_number',
            'status', 'timestamp'
        ]].rename(columns={
            'booking_id': 'รหัสการจอง',
            'username': 'ชื่อผู้ใช้',
            'room_name': 'ห้องกิจกรรม',
            'booking_date': 'วันที่จอง',
            'start_time': 'เวลาเริ่ม',
            'end_time': 'เวลาสิ้นสุด',
            'num_users_or_machines': 'จำนวนคน/เครื่อง',
            'user_full_name': 'ชื่อ-นามสกุลผู้จอง',
            'user_room_number': 'ห้องเลขที่ผู้จอง',
            'user_phone_number': 'เบอร์โทรผู้จอง',
            'status': 'สถานะ',
            'timestamp': 'เวลาทำรายการ'
        })
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_export_final.to_excel(writer, sheet_name='Bookings', index=False)
        output.seek(0)

        st.download_button(
            label="ดาวน์โหลดข้อมูลการจองเป็น Excel",
            data=output,
            file_name="booking_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ไม่มีข้อมูลการจองสำหรับส่งออก")

    st.markdown("---")
    if st.button("กลับหน้าหลัก", key="back_from_admin_bookings"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- หน้าจัดการผู้ใช้ (สำหรับแอดมิน) (ปรับปรุง) ---
def manage_users_page():
    st.title("จัดการผู้ใช้ (สำหรับผู้ดูแลระบบ)")

    users = load_users()
    if not users:
        st.info("ยังไม่มีผู้ใช้ในระบบ")
        if st.button("กลับหน้าหลัก"):
            st.session_state['current_page'] = 'main_page'
            st.experimental_rerun()
        return

    # แปลง Dictionary ของ users เป็น List ของ Dictionary เพื่อสร้าง DataFrame ได้ง่ายขึ้น
    users_list = list(users.values())
    df_users = pd.DataFrame(users_list)

    st.subheader("รายการผู้ใช้ทั้งหมด")
    # เลือกคอลัมน์ที่ต้องการแสดงและตั้งชื่อใหม่
    df_display_users = df_users[[
        'username', 'full_name', 'room_number', 'phone_number',
        'user_status', 'status', 'role'
    ]].rename(columns={
        'username': 'ชื่อผู้ใช้',
        'full_name': 'ชื่อ-นามสกุล',
        'room_number': 'ห้องเลขที่',
        'phone_number': 'เบอร์โทรศัพท์',
        'user_status': 'สถานะผู้ใช้',
        'status': 'สถานะบัญชี',
        'role': 'บทบาท'
    })
    st.dataframe(df_display_users, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("จัดการสถานะและบทบาทของผู้ใช้")

    user_names = list(users.keys())
    if user_names:
        selected_user = st.selectbox(
            "เลือกชื่อผู้ใช้ที่ต้องการจัดการ",
            user_names,
            key="select_user_to_manage"
        )

        current_user_info = users.get(selected_user, {})
        col_status, col_role = st.columns(2)

        with col_status:
            new_status = st.selectbox(
                "เปลี่ยนสถานะบัญชี",
                ["pending", "approved", "rejected"],
                index=["pending", "approved", "rejected"].index(current_user_info.get('status', 'pending')),
                key=f"status_for_{selected_user}"
            )
        with col_role:
            new_role = st.selectbox(
                "เปลี่ยนบทบาท",
                ["user", "admin"],
                index=["user", "admin"].index(current_user_info.get('role', 'user')),
                key=f"role_for_{selected_user}"
            )

        if st.button("อัปเดตสถานะและบทบาทผู้ใช้"):
            users_to_update = load_users()
            if selected_user in users_to_update:
                users_to_update[selected_user]['status'] = new_status
                users_to_update[selected_user]['role'] = new_role
                save_users(users_to_update)
                st.success(f"อัปเดตสถานะและบทบาทของ '{selected_user}' เป็น สถานะ: '{new_status}', บทบาท: '{new_role}' สำเร็จ")
                st.experimental_rerun()
            else:
                st.error("ไม่พบผู้ใช้ที่เลือก")
    else:
        st.info("ไม่มีผู้ใช้ให้จัดการ")

    st.markdown("---")
    st.subheader("ลบผู้ใช้")
    if user_names:
        user_to_delete = st.selectbox(
            "เลือกชื่อผู้ใช้ที่ต้องการลบ",
            user_names,
            key="select_user_to_delete"
        )
        if st.button("ยืนยันการลบผู้ใช้"):
            if user_to_delete == get_current_username():
                st.error("ไม่สามารถลบบัญชีผู้ใช้ที่คุณกำลังล็อกอินอยู่ได้")
            else:
                users_to_update = load_users()
                if user_to_delete in users_to_update:
                    del users_to_update[user_to_delete]
                    save_users(users_to_update)
                    st.success(f"ลบผู้ใช้ '{user_to_delete}' สำเร็จ")
                    st.experimental_rerun()
                else:
                    st.error("ไม่พบผู้ใช้ที่เลือก")
    else:
        st.info("ไม่มีผู้ใช้ให้ลบ")

    st.markdown("---")
    st.subheader("ส่งออกข้อมูล")
    if users:
        df_export_users = pd.DataFrame(users_list)
        df_export_users_final = df_export_users[[
            'username', 'full_name', 'room_number', 'phone_number',
            'user_status', 'status', 'role'
        ]].rename(columns={
            'username': 'ชื่อผู้ใช้',
            'full_name': 'ชื่อ-นามสกุล',
            'room_number': 'ห้องเลขที่',
            'phone_number': 'เบอร์โทรศัพท์',
            'user_status': 'สถานะผู้ใช้',
            'status': 'สถานะบัญชี',
            'role': 'บทบาท'
        })
        output_users = BytesIO()
        with pd.ExcelWriter(output_users, engine='xlsxwriter') as writer:
            df_export_users_final.to_excel(writer, sheet_name='Users', index=False)
        output_users.seek(0)

        st.download_button(
            label="ดาวน์โหลดข้อมูลผู้ใช้เป็น Excel",
            data=output_users,
            file_name="user_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ไม่มีข้อมูลผู้ใช้สำหรับส่งออก")


    st.markdown("---")
    if st.button("กลับหน้าหลัก", key="back_from_manage_users"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- หน้าจัดการห้อง (สำหรับแอดมิน) (คงเดิม) ---
def manage_rooms_page():
    st.title("จัดการห้อง (สำหรับแอดมิน)")
    st.write("นี่คือหน้าจัดการห้อง - จะพัฒนาในส่วนถัดไป")
    rooms_df = pd.DataFrame.from_dict(ROOMS_DATA, orient='index')
    st.dataframe(rooms_df, use_container_width=True)
    st.info("โปรดทราบ: ในอนาคตหน้านี้จะอนุญาตให้แอดมินแก้ไข/ลบห้องได้")
    if st.button("กลับหน้าหลัก"):
        st.session_state['current_page'] = 'main_page'
        st.experimental_rerun()

# --- ระบบนำทางหน้าเพจ (คงเดิม) ---
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'main_page'

if st.session_state['current_page'] == 'main_page':
    main_page()
elif st.session_state['current_page'] == 'login':
    login_page()
elif st.session_state['current_page'] == 'register':
    register_page()
elif st.session_state['current_page'] == 'booking_form':
    booking_form_page()
elif st.session_state['current_page'] == 'my_bookings':
    my_bookings_page()
elif st.session_state['current_page'] == 'manage_users':
    manage_users_page()
elif st.session_state['current_page'] == 'manage_rooms':
    manage_rooms_page()
elif st.session_state['current_page'] == 'admin_manage_bookings':
    admin_manage_bookings_page()
