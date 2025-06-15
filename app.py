import streamlit as st
import pandas as pd
import json
import datetime
import hashlib
import uuid
from io import BytesIO

# --- การกำหนดค่า CSS สำหรับ Mobile-First Design ---
def load_css():
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    .main-container {
        padding: 1rem;
        max-width: 100%;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .room-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e1e5e9;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .room-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .room-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
    }
    
    .room-icon {
        margin-right: 0.5rem;
        font-size: 1.5rem;
    }
    
    .room-info {
        color: #7f8c8d;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .room-description {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #495057;
        border-left: 4px solid #667eea;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .status-pending {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-approved {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-rejected {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Form styling */
    .form-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .app-title {
            font-size: 1.5rem;
        }
        
        .room-card {
            padding: 1rem;
        }
        
        .room-title {
            font-size: 1.1rem;
        }
        
        .form-container {
            padding: 1rem;
        }
    }
    
    /* Success/Error message styling */
    .stSuccess {
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    
    .stError {
        border-radius: 10px;
        border-left: 4px solid #dc3545;
    }
    
    .stWarning {
        border-radius: 10px;
        border-left: 4px solid #ffc107;
    }
    
    .stInfo {
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Navigation improvements */
    .nav-section {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- กำหนดค่าเริ่มต้นและข้อมูลห้อง (เพิ่มไอคอน) ---
ROOMS_DATA = {
    "Brain Stroming room": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1,
        "booking_advance_hours": 3,
        "min_users": 2,
        "max_users": 5,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 2 - 5 คน ต่อครั้ง",
        "icon": "🧠"
    },
    "E-Sport room": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1,
        "booking_advance_hours": 3,
        "max_machines": 3,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้ใช้งาน ไม่เกิน 3 เครื่อง ต่อครั้ง จากทั้งหมด 8 เครื่อง",
        "icon": "🎮"
    },
    "Pool Table": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1,
        "booking_advance_hours": 3,
        "min_users": 1,
        "max_users": 4,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 1 - 4 คน ต่อครั้ง",
        "icon": "🎱"
    },
    "Music & Dance room": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1,
        "booking_advance_hours": 3,
        "min_users": 1,
        "max_users": 5,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 1 - 5 คน ต่อครั้ง",
        "icon": "🎵"
    },
    "Meeting C": {
        "open_time": "06:00",
        "close_time": "21:00",
        "duration_per_booking": 1,
        "booking_advance_days": 5,
        "min_users": 5,
        "max_users": 12,
        "description": "จองได้ครั้งละ 1 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 5 วัน, จำกัดผู้เข้าใช้ 5 - 12 คน ต่อครั้ง",
        "icon": "👥"
    },
    "Movie & Karaoke": {
        "open_time": "07:00",
        "close_time": "21:00",
        "duration_per_booking": 2,
        "booking_advance_hours": 3,
        "min_users": 1,
        "max_users": 7,
        "description": "จองได้ครั้งละ 2 ชั่วโมง/ครั้ง, จองก่อนใช้งานจริง 3 ชั่วโมงขึ้นไป, จำกัดผู้เข้าใช้ 1 - 7 คน ต่อครั้ง",
        "icon": "🎬"
    }
}

# --- ฟังก์ชันช่วยจัดการข้อมูลผู้ใช้ (คงเดิม) ---
USERS_FILE = 'users.json'
BOOKINGS_FILE = 'bookings.json'

def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_bookings():
    try:
        with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, indent=4, ensure_ascii=False)

def check_login_status():
    return st.session_state.get('logged_in', False)

def get_current_user_role():
    return st.session_state.get('user_role', 'guest')

def get_current_username():
    return st.session_state.get('username', None)

def get_status_badge(status):
    """สร้าง HTML badge สำหรับสถานะ"""
    status_map = {
        'pending': ('รออนุมัติ', 'status-pending'),
        'approved': ('อนุมัติแล้ว', 'status-approved'),
        'rejected': ('ปฏิเสธ', 'status-rejected'),
        'cancelled_by_user': ('ยกเลิกแล้ว', 'status-rejected')
    }
    text, css_class = status_map.get(status, (status, 'status-pending'))
    return f'<span class="status-badge {css_class}">{text}</span>'

# --- หน้าหลัก (Landing Page) - ปรับปรุงใหม่ ---
def main_page():
    st.set_page_config(
        page_title="ระบบจองห้องกิจกรรม",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    load_css()
    
    # Header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">🏠 ระบบจองห้องกิจกรรม</div>
        <div class="app-subtitle">เลือกห้องกิจกรรมที่ต้องการเพื่อดูรายละเอียดและทำการจอง</div>
    </div>
    """, unsafe_allow_html=True)

    # Room cards
    for room_name, room_info in ROOMS_DATA.items():
        st.markdown(f"""
        <div class="room-card">
            <div class="room-title">
                <span class="room-icon">{room_info.get('icon', '🏢')}</span>
                {room_name}
            </div>
            <div class="room-info">
                <strong>⏰ เวลาเปิด:</strong> {room_info['open_time']} - {room_info['close_time']} น.
            </div>
            <div class="room-description">
                <strong>📋 เงื่อนไข:</strong> {room_info['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"📅 จองห้อง {room_name}", key=f"book_{room_name}"):
            if check_login_status():
                users = load_users()
                current_user_data = users.get(get_current_username())
                if current_user_data and current_user_data.get('status') == 'approved':
                    st.session_state['current_page'] = 'booking_form'
                    st.session_state['selected_room'] = room_name
                    st.rerun()
                elif current_user_data and current_user_data.get('status') == 'pending':
                    st.warning("⏳ บัญชีของคุณอยู่ระหว่างรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการตรวจสอบ")
                elif current_user_data and current_user_data.get('status') == 'rejected':
                    st.error("❌ บัญชีของคุณถูกปฏิเสธการลงทะเบียน กรุณาติดต่อผู้ดูแลระบบ")
                else:
                    st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนทำการจอง")
                    st.session_state['logged_in'] = False
                    st.session_state['current_page'] = 'login'
                    st.rerun()
            else:
                st.warning("⚠️ กรุณาเข้าสู่ระบบก่อนทำการจอง")
                st.session_state['current_page'] = 'login'
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar navigation
    setup_sidebar()

def setup_sidebar():
    """ตั้งค่า sidebar navigation"""
    st.sidebar.markdown("""
    <div class="nav-section">
        <h3>🧭 เมนูนำทาง</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not check_login_status():
        if st.sidebar.button("🔐 เข้าสู่ระบบ"):
            st.session_state['current_page'] = 'login'
            st.rerun()
        if st.sidebar.button("📝 สมัครสมาชิก"):
            st.session_state['current_page'] = 'register'
            st.rerun()
    else:
        current_username = get_current_username()
        users = load_users()
        user_data = users.get(current_username)

        if user_data:
            st.sidebar.markdown(f"""
            <div class="nav-section">
                <h4>👋 สวัสดี</h4>
                <p><strong>{user_data.get('full_name', current_username)}</strong></p>
                <p>{get_status_badge(user_data.get('status', 'pending'))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if user_data.get('status') == 'approved':
                if st.sidebar.button("📋 จัดการการจองของฉัน"):
                    st.session_state['current_page'] = 'my_bookings'
                    st.rerun()
                if get_current_user_role() == 'admin':
                    st.sidebar.markdown("---")
                    st.sidebar.markdown("**🔧 เมนูผู้ดูแลระบบ**")
                    if st.sidebar.button("👥 จัดการผู้ใช้"):
                        st.session_state['current_page'] = 'manage_users'
                        st.rerun()
                    if st.sidebar.button("🏢 จัดการห้อง"):
                        st.session_state['current_page'] = 'manage_rooms'
                        st.rerun()
                    if st.sidebar.button("📊 ดูการจองทั้งหมด"):
                        st.session_state['current_page'] = 'admin_manage_bookings'
                        st.rerun()

        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 ออกจากระบบ"):
            for key in ['logged_in', 'username', 'user_role']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state['current_page'] = 'main_page'
            st.success("✅ ออกจากระบบเรียบร้อยแล้ว")
            st.rerun()

# --- หน้าเข้าสู่ระบบ - ปรับปรุงใหม่ ---
def login_page():
    load_css()
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">🔐 เข้าสู่ระบบ</div>
        <div class="app-subtitle">กรุณาใส่ข้อมูลเพื่อเข้าสู่ระบบ</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        initial_username = st.session_state.get('remember_me_username', '')
        username_or_phone = st.text_input("👤 ชื่อผู้ใช้ หรือ เบอร์โทรศัพท์", value=initial_username)
        password = st.text_input("🔒 รหัสผ่าน", type="password")
        remember_me = st.checkbox("💾 จดจำชื่อผู้ใช้")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔐 เข้าสู่ระบบ", use_container_width=True):
                login_user(username_or_phone, password, remember_me)
        with col2:
            if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
                st.session_state['current_page'] = 'main_page'
                st.rerun()
        
        st.markdown("---")
        st.markdown("**ยังไม่มีบัญชีใช่ไหม?**")
        if st.button("📝 สมัครสมาชิก", use_container_width=True):
            st.session_state['current_page'] = 'register'
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def login_user(username_or_phone, password, remember_me):
    """ฟังก์ชันจัดการการเข้าสู่ระบบ"""
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
            st.success(f"🎉 ยินดีต้อนรับ, {found_user.get('full_name', found_user['username'])}!")
            st.session_state['current_page'] = 'main_page'
            st.rerun()
        elif found_user.get('status') == 'pending':
            st.warning("⏳ บัญชีของคุณอยู่ระหว่างรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการตรวจสอบ")
            st.session_state['logged_in'] = True
            st.session_state['current_page'] = 'main_page'
            st.rerun()
        elif found_user.get('status') == 'rejected':
            st.error("❌ บัญชีของคุณถูกปฏิเสธการลงทะเบียน กรุณาติดต่อผู้ดูแลระบบ")
            st.session_state['logged_in'] = False
            st.session_state['current_page'] = 'login'
            st.rerun()
    else:
        st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

# --- หน้าสมัครสมาชิก - ปรับปรุงใหม่ ---
def register_page():
    load_css()
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📝 สมัครสมาชิกใหม่</div>
        <div class="app-subtitle">กรุณากรอกข้อมูลเพื่อสมัครสมาชิก</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        new_username = st.text_input("👤 ชื่อผู้ใช้ (ใช้สำหรับเข้าสู่ระบบ)")
        
        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input("🔒 รหัสผ่าน", type="password")
        with col2:
            confirm_password = st.text_input("🔒 ยืนยันรหัสผ่าน", type="password")
        
        full_name = st.text_input("📛 ชื่อ-นามสกุล")
        
        col3, col4 = st.columns(2)
        with col3:
            room_number = st.text_input("🏠 ห้องเลขที่ (เช่น 54/999)")
        with col4:
            phone_number = st.text_input("📱 เบอร์โทรศัพท์ (เช่น 08XXXXXXXX)")
        
        user_status_options = ["ผู้เช่า", "เจ้าของ"]
        user_status = st.selectbox("👥 สถานะ", user_status_options)
        
        id_photo = st.file_uploader("📷 อัปโหลดไฟล์รูปภาพสำหรับยืนยันตัวตน (เช่น บัตรประชาชน)", 
                                   type=["png", "jpg", "jpeg"])

        col5, col6 = st.columns(2)
        with col5:
            if st.button("📝 สมัครสมาชิก", use_container_width=True):
                register_user(new_username, new_password, confirm_password, full_name, 
                            room_number, phone_number, user_status, id_photo)
        with col6:
            if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
                st.session_state['current_page'] = 'main_page'
                st.rerun()

        st.markdown("---")
        st.markdown("**มีบัญชีอยู่แล้วใช่ไหม?**")
        if st.button("🔐 เข้าสู่ระบบ", use_container_width=True):
            st.session_state['current_page'] = 'login'
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def register_user(new_username, new_password, confirm_password, full_name, 
                 room_number, phone_number, user_status, id_photo):
    """ฟังก์ชันจัดการการสมัครสมาชิก"""
    users = load_users()
    
    if not all([new_username, new_password, confirm_password, full_name, room_number, phone_number, id_photo]):
        st.error("❌ กรุณากรอกข้อมูลให้ครบถ้วนและอัปโหลดรูปภาพ")
        return
    
    if new_password != confirm_password:
        st.error("❌ รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
        return
    
    if new_username in users:
        st.error("❌ ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่อผู้ใช้อื่น")
        return
    
    if any(user_data.get('phone_number') == phone_number for user_data in users.values()):
        st.error("❌ เบอร์โทรศัพท์นี้มีการลงทะเบียนแล้ว กรุณาใช้เบอร์อื่นหรือติดต่อผู้ดูแลระบบ")
        return

    users[new_username] = {
        'username': new_username,
        'password': hash_password(new_password),
        'full_name': full_name,
        'room_number': room_number,
        'phone_number': phone_number,
        'user_status': user_status,
        'id_photo_uploaded': True,
        'status': 'pending',
        'role': 'user'
    }
    save_users(users)
    st.success("🎉 สมัครสมาชิกสำเร็จ! โปรดรอการอนุมัติจากผู้ดูแลระบบ")
    st.session_state['current_page'] = 'login'
    st.rerun()

# --- หน้าจองห้อง - ปรับปรุงใหม่ ---
def booking_form_page():
    load_css()
    
    selected_room = st.session_state.get('selected_room', 'ไม่ระบุ')
    room_info = ROOMS_DATA.get(selected_room, {})
    current_username = get_current_username()
    users = load_users()
    current_user_data = users.get(current_username, {})

    st.markdown(f"""
    <div class="app-header">
        <div class="app-title">{room_info.get('icon', '🏢')} จองห้อง: {selected_room}</div>
        <div class="app-subtitle">กรุณากรอกข้อมูลการจองให้ครบถ้วน</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # ข้อมูลห้อง
        st.markdown(f"""
        <div class="room-description">
            <strong>📋 รายละเอียดห้อง:</strong> {room_info.get('description', 'ไม่มีข้อมูล')}
        </div>
        """, unsafe_allow_html=True)

        # ข้อมูลผู้จอง
        st.subheader("👤 ข้อมูลผู้จอง")
        col1, col2 = st.columns(2)
        with col1:
            user_full_name = st.text_input("📛 ชื่อ-นามสกุล", 
                                         value=current_user_data.get('full_name', ''), 
                                         disabled=True)
            user_room_number = st.text_input("🏠 ห้องเลขที่", 
                                           value=current_user_data.get('room_number', ''), 
                                           disabled=True)
        with col2:
            user_phone_number = st.text_input("📱 เบอร์โทรศัพท์", 
                                            value=current_user_data.get('phone_number', ''), 
                                            disabled=True)

        st.markdown("---")
        
        # ข้อมูลการจอง
        st.subheader("📅 ข้อมูลการจอง")
        col3, col4 = st.columns(2)
        
        with col3:
            booking_date = st.date_input("📅 เลือกวันที่จอง", 
                                       min_value=datetime.date.today())
        
        with col4:
            # คำนวณช่วงเวลาที่ว่าง
            available_time_slots = calculate_available_slots(selected_room, booking_date, room_info)
            
            if not available_time_slots:
                st.warning("⚠️ ไม่มีช่วงเวลาว่างสำหรับวันที่เลือก")
                booking_time = st.selectbox("⏰ เลือกช่วงเวลา", 
                                          ["- ไม่มีช่วงเวลาว่าง -"], 
                                          disabled=True)
            else:
                booking_time = st.selectbox("⏰ เลือกช่วงเวลา", available_time_slots)

        # จำนวนผู้ใช้/เครื่อง
        if selected_room == "E-Sport room":
            num_users_or_machines = st.number_input(
                f"🎮 จำนวนเครื่องที่ต้องการใช้ (สูงสุด {room_info.get('max_machines', 0)} เครื่อง)",
                min_value=1,
                max_value=room_info.get('max_machines', 0),
                value=1,
                step=1
            )
        else:
            min_users = room_info.get('min_users', 1)
            max_users = room_info.get('max_users', 1)
            num_users_or_machines = st.number_input(
                f"👥 จำนวนผู้เข้าใช้งาน (ขั้นต่ำ {min_users} คน, สูงสุด {max_users} คน)",
                min_value=min_users,
                max_value=max_users,
                value=min_users,
                step=1
            )

        st.markdown("---")
        
        # ปุ่มดำเนินการ
        col5, col6 = st.columns(2)
        with col5:
            if st.button("✅ ยืนยันการจอง", use_container_width=True):
                process_booking(selected_room, booking_date, booking_time, 
                              num_users_or_machines, current_user_data, room_info)
        with col6:
            if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
                st.session_state['current_page'] = 'main_page'
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

def calculate_available_slots(selected_room, booking_date, room_info):
    """คำนวณช่วงเวลาที่ว่างสำหรับการจอง"""
    open_time_str = room_info.get('open_time')
    close_time_str = room_info.get('close_time')
    duration_hours = room_info.get('duration_per_booking')
    
    available_time_slots = []
    
    if open_time_str and close_time_str and duration_hours:
        open_time = datetime.datetime.strptime(open_time_str, "%H:%M").time()
        close_time = datetime.datetime.strptime(close_time_str, "%H:%M").time()
        
        current_time_slot_start = datetime.datetime.combine(booking_date, open_time)
        
        while current_time_slot_start.time() < close_time:
            current_time_slot_end = current_time_slot_start + datetime.timedelta(hours=duration_hours)
            
            if current_time_slot_end.date() > booking_date or current_time_slot_end.time() > close_time:
                break
            
            # ตรวจสอบว่าช่วงเวลานี้ว่างหรือไม่
            is_slot_available = True
            bookings = load_bookings()
            
            for booking in bookings:
                existing_booking_start_dt = datetime.datetime.strptime(
                    f"{booking['booking_date']} {booking['start_time']}", "%Y-%m-%d %H:%M")
                existing_booking_end_dt = datetime.datetime.strptime(
                    f"{booking['booking_date']} {booking['end_time']}", "%Y-%m-%d %H:%M")
                
                time_overlap = (current_time_slot_start < existing_booking_end_dt) and \
                              (current_time_slot_end > existing_booking_start_dt)
                
                if time_overlap and booking['status'] in ['pending', 'approved'] and \
                   booking['room_name'] == selected_room:
                    is_slot_available = False
                    break
            
            if is_slot_available:
                available_time_slots.append(
                    f"{current_time_slot_start.strftime('%H:%M')} - {current_time_slot_end.strftime('%H:%M')}")
            
            current_time_slot_start = current_time_slot_start + datetime.timedelta(hours=duration_hours)
    
    return available_time_slots

def process_booking(selected_room, booking_date, booking_time, num_users_or_machines, 
                   current_user_data, room_info):
    """ประมวลผลการจอง"""
    if not booking_date or not booking_time or booking_time == "- ไม่มีช่วงเวลาว่าง -":
        st.error("❌ กรุณากรอกข้อมูลการจองให้ครบถ้วนและเลือกช่วงเวลาที่ว่าง")
        return

    start_time_str = booking_time.split(' - ')[0]
    end_time_str = booking_time.split(' - ')[1]
    booking_datetime_start = datetime.datetime.combine(
        booking_date, datetime.datetime.strptime(start_time_str, "%H:%M").time())
    
    # ตรวจสอบเวลาล่วงหน้า
    current_datetime = datetime.datetime.now()
    if booking_datetime_start < current_datetime:
        st.error("❌ ไม่สามารถจองในเวลาที่ผ่านมาแล้วได้")
        return
    
    # ตรวจสอบการจองล่วงหน้า
    if not check_advance_booking(booking_datetime_start, current_datetime, room_info, selected_room):
        return
    
    # ตรวจสอบความขัดแย้งของการจอง
    if not check_booking_conflicts(booking_datetime_start, booking_time, selected_room, 
                                 current_user_data.get('room_number')):
        return
    
    # ตรวจสอบจำนวนผู้ใช้/เครื่อง
    if not validate_user_count(selected_room, num_users_or_machines, room_info):
        return
    
    # สร้างการจองใหม่
    create_new_booking(selected_room, booking_date, start_time_str, end_time_str,
                      num_users_or_machines, current_user_data)

def check_advance_booking(booking_datetime_start, current_datetime, room_info, selected_room):
    """ตรวจสอบการจองล่วงหน้า"""
    if "booking_advance_days" in room_info:
        required_advance_date = current_datetime + datetime.timedelta(days=room_info["booking_advance_days"])
        if booking_datetime_start < required_advance_date:
            st.error(f"❌ ห้อง {selected_room} ต้องจองล่วงหน้าอย่างน้อย {room_info['booking_advance_days']} วัน")
            return False
    elif "booking_advance_hours" in room_info:
        required_advance_time = current_datetime + datetime.timedelta(hours=room_info["booking_advance_hours"])
        if booking_datetime_start < required_advance_time:
            st.error(f"❌ ต้องจองล่วงหน้าอย่างน้อย {room_info['booking_advance_hours']} ชั่วโมง")
            return False
    return True

def check_booking_conflicts(booking_datetime_start, booking_time, selected_room, user_room_number):
    """ตรวจสอบความขัดแย้งของการจอง"""
    start_time_str = booking_time.split(' - ')[0]
    end_time_str = booking_time.split(' - ')[1]
    booking_datetime_end = datetime.datetime.combine(
        booking_datetime_start.date(), 
        datetime.datetime.strptime(end_time_str, "%H:%M").time())
    
    bookings = load_bookings()
    
    for booking in bookings:
        existing_booking_start_dt = datetime.datetime.strptime(
            f"{booking['booking_date']} {booking['start_time']}", "%Y-%m-%d %H:%M")
        existing_booking_end_dt = datetime.datetime.strptime(
            f"{booking['booking_date']} {booking['end_time']}", "%Y-%m-%d %H:%M")
        
        time_overlap = (booking_datetime_start < existing_booking_end_dt) and \
                      (booking_datetime_end > existing_booking_start_dt)
        
        if time_overlap and booking['status'] in ['pending', 'approved']:
            if booking['room_name'] == selected_room:
                st.error(f"❌ ห้อง {selected_room} ไม่ว่างในช่วงเวลาที่เลือก")
                return False
            
            if booking['user_room_number'] == user_room_number:
                st.error(f"❌ ห้องเลขที่ {user_room_number} มีการจองห้องอื่นในช่วงเวลาเดียวกันอยู่แล้ว")
                return False
    
    return True

def validate_user_count(selected_room, num_users_or_machines, room_info):
    """ตรวจสอบจำนวนผู้ใช้/เครื่อง"""
    if selected_room == "E-Sport room":
        if not (1 <= num_users_or_machines <= room_info.get('max_machines', 0)):
            st.error(f"❌ จำนวนเครื่องต้องไม่เกิน {room_info.get('max_machines', 0)} เครื่อง")
            return False
    else:
        min_users = room_info.get('min_users', 0)
        max_users = room_info.get('max_users', 0)
        if not (min_users <= num_users_or_machines <= max_users):
            st.error(f"❌ จำนวนผู้เข้าใช้งานต้องอยู่ระหว่าง {min_users} ถึง {max_users} คน")
            return False
    return True

def create_new_booking(selected_room, booking_date, start_time_str, end_time_str,
                      num_users_or_machines, current_user_data):
    """สร้างการจองใหม่"""
    new_booking = {
        "booking_id": str(uuid.uuid4()),
        "username": get_current_username(),
        "room_name": selected_room,
        "booking_date": booking_date.strftime("%Y-%m-%d"),
        "start_time": start_time_str,
        "end_time": end_time_str,
        "num_users_or_machines": num_users_or_machines,
        "user_full_name": current_user_data.get('full_name', ''),
        "user_room_number": current_user_data.get('room_number', ''),
        "user_phone_number": current_user_data.get('phone_number', ''),
        "status": "pending",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    bookings = load_bookings()
    bookings.append(new_booking)
    save_bookings(bookings)
    
    st.success("🎉 การจองห้องสำเร็จ! โปรดรอการอนุมัติจากผู้ดูแลระบบ")
    st.session_state['current_page'] = 'my_bookings'
    st.rerun()

# --- หน้าจัดการการจองของฉัน - ปรับปรุงใหม่ ---
def my_bookings_page():
    load_css()
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📋 การจองของฉัน</div>
        <div class="app-subtitle">จัดการและติดตามสถานะการจองของคุณ</div>
    </div>
    """, unsafe_allow_html=True)

    current_username = get_current_username()
    users = load_users()
    current_user_data = users.get(current_username, {})

    # ข้อมูลโปรไฟล์
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("👤 ข้อมูลโปรไฟล์")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**👤 ชื่อผู้ใช้:** {current_user_data.get('username')}")
            st.write(f"**📛 ชื่อ-นามสกุล:** {current_user_data.get('full_name')}")
            st.write(f"**🏠 ห้องเลขที่:** {current_user_data.get('room_number')}")
        with col2:
            st.write(f"**📱 เบอร์โทรศัพท์:** {current_user_data.get('phone_number')}")
            st.write(f"**👥 สถานะผู้ใช้:** {current_user_data.get('user_status')}")
            st.markdown(f"**📊 สถานะบัญชี:** {get_status_badge(current_user_data.get('status'))}", 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # รายการจอง
    st.subheader("📅 รายการจองห้องกิจกรรม")
    bookings = load_bookings()
    user_bookings = [b for b in bookings if b['username'] == current_username]

    if user_bookings:
        display_user_bookings(user_bookings)
        display_cancellation_section(user_bookings)
    else:
        st.info("ℹ️ คุณยังไม่มีการจองห้องกิจกรรม")

    # ปุ่มกลับ
    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state['current_page'] = 'main_page'
        st.rerun()

def display_user_bookings(user_bookings):
    """แสดงรายการจองของผู้ใช้"""
    df = pd.DataFrame(user_bookings)
    df['datetime_sort'] = pd.to_datetime(df['booking_date'] + ' ' + df['start_time'])
    df = df.sort_values(by='datetime_sort', ascending=False)
    
    # เพิ่มคอลัมน์สถานะที่มี HTML
    df['สถานะ_HTML'] = df['status'].apply(get_status_badge)
    
    df_display = df[[
        'room_name', 'booking_date', 'start_time', 'end_time',
        'num_users_or_machines', 'สถานะ_HTML', 'timestamp'
    ]].rename(columns={
        'room_name': '🏢 ห้องกิจกรรม',
        'booking_date': '📅 วันที่จอง',
        'start_time': '⏰ เวลาเริ่มต้น',
        'end_time': '⏰ เวลาสิ้นสุด',
        'num_users_or_machines': '👥 จำนวนคน/เครื่อง',
        'สถานะ_HTML': '📊 สถานะ',
        'timestamp': '🕐 เวลาที่ทำการจอง'
    })
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

def display_cancellation_section(user_bookings):
    """แสดงส่วนยกเลิกการจอง"""
    st.markdown("---")
    st.subheader("❌ ยกเลิกการจอง")
    
    cancellable_bookings = [
        b for b in user_bookings
        if b['status'] == 'pending' and
           (datetime.datetime.strptime(f"{b['booking_date']} {b['start_time']}", "%Y-%m-%d %H:%M") > 
            datetime.datetime.now())
    ]

    if cancellable_bookings:
        booking_options = {
            f"🏢 {b['room_name']} - 📅 {b['booking_date']} ⏰ {b['start_time']}" : b['booking_id']
            for b in cancellable_bookings
        }
        
        selected_booking_display = st.selectbox(
            "เลือกรายการจองที่ต้องการยกเลิก (เฉพาะสถานะ 'รออนุมัติ' และยังไม่ถึงเวลาจอง)",
            list(booking_options.keys())
        )
        
        if st.button("❌ ยืนยันการยกเลิกการจอง", use_container_width=True):
            selected_booking_id = booking_options.get(selected_booking_display)
            cancel_booking(selected_booking_id)
    else:
        st.info("ℹ️ ไม่มีรายการจองที่สามารถยกเลิกได้ในขณะนี้")

def cancel_booking(booking_id):
    """ยกเลิกการจอง"""
    bookings = load_bookings()
    
    for i, booking in enumerate(bookings):
        if booking['booking_id'] == booking_id and booking['status'] == 'pending':
            bookings[i]['status'] = 'cancelled_by_user'
            save_bookings(bookings)
            st.success("✅ ยกเลิกการจองสำเร็จแล้ว")
            st.rerun()
            return
    
    st.error("❌ ไม่สามารถยกเลิกการจองนี้ได้")

# --- หน้าจัดการการจอง (สำหรับผู้ดูแลระบบ) - ปรับปรุงใหม่ ---
def admin_manage_bookings_page():
    load_css()
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📊 จัดการการจองทั้งหมด</div>
        <div class="app-subtitle">สำหรับผู้ดูแลระบบ</div>
    </div>
    """, unsafe_allow_html=True)

    bookings = load_bookings()

    if not bookings:
        st.info("ℹ️ ยังไม่มีรายการจองในระบบ")
        if st.button("🏠 กลับหน้าหลัก"):
            st.session_state['current_page'] = 'main_page'
            st.rerun()
        return

    # ส่วนกรองและเรียงข้อมูล
    display_booking_filters_and_data(bookings)
    
    # ส่วนจัดการสถานะ
    display_booking_management_section(bookings)
    
    # ส่วนส่งออกข้อมูล
    display_export_section(bookings)

    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state['current_page'] = 'main_page'
        st.rerun()

def display_booking_filters_and_data(bookings):
    """แสดงส่วนกรองและข้อมูลการจอง"""
    df = pd.DataFrame(bookings)
    
    st.subheader("🔍 กรองและเรียงข้อมูล")
    col_filter, col_sort = st.columns(2)
    
    with col_filter:
        status_filter = st.selectbox(
            "กรองตามสถานะ",
            ["ทั้งหมด", "pending", "approved", "rejected", "cancelled_by_user"],
            key="admin_booking_status_filter"
        )
    
    with col_sort:
        sort_options = {
            "วันที่จอง (ล่าสุด)": ("booking_date", "start_time", False),
            "วันที่จอง (เก่าสุด)": ("booking_date", "start_time", True),
            "สถานะ": ("status", None, True)
        }
        sort_by_display = st.selectbox(
            "เรียงลำดับตาม",
            list(sort_options.keys()),
            key="admin_booking_sort"
        )

    # กรองข้อมูล
    filtered_df = df.copy()
    if status_filter != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]

    # เรียงข้อมูล
    sort_col1, sort_col2, sort_asc = sort_options[sort_by_display]
    if sort_col1 == "booking_date":
        filtered_df['sort_key'] = pd.to_datetime(filtered_df['booking_date'] + ' ' + filtered_df['start_time'])
        filtered_df = filtered_df.sort_values(by='sort_key', ascending=sort_asc).drop(columns=['sort_key'])
    else:
        filtered_df = filtered_df.sort_values(by=sort_col1, ascending=sort_asc)

    # แสดงข้อมูล
    st.subheader("📋 รายการจองทั้งหมด")
    
    # เพิ่มคอลัมน์สถานะที่มี HTML
    filtered_df['สถานะ_HTML'] = filtered_df['status'].apply(get_status_badge)
    
    display_columns = [
        'booking_id', 'username', 'room_name', 'booking_date', 'start_time', 'end_time',
        'num_users_or_machines', 'user_full_name', 'user_room_number', 'user_phone_number',
        'สถานะ_HTML', 'timestamp'
    ]
    
    column_names = {
        'booking_id': '🆔 รหัสการจอง',
        'username': '👤 ชื่อผู้ใช้',
        'room_name': '🏢 ห้องกิจกรรม',
        'booking_date': '📅 วันที่จอง',
        'start_time': '⏰ เวลาเริ่ม',
        'end_time': '⏰ เวลาสิ้นสุด',
        'num_users_or_machines': '👥 จำนวนคน/เครื่อง',
        'user_full_name': '📛 ชื่อ-นามสกุลผู้จอง',
        'user_room_number': '🏠 ห้องเลขที่ผู้จอง',
        'user_phone_number': '📱 เบอร์โทรผู้จอง',
        'สถานะ_HTML': '📊 สถานะ',
        'timestamp': '🕐 เวลาทำรายการ'
    }
    
    df_display = filtered_df[display_columns].rename(columns=column_names)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

def display_booking_management_section(bookings):
    """แสดงส่วนจัดการการจอง"""
    st.markdown("---")
    st.subheader("⚙️ จัดการสถานะการจอง")
    
    booking_ids = [b['booking_id'] for b in bookings]
    
    if booking_ids:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_booking_id = st.selectbox(
                "เลือกรหัสการจองที่ต้องการจัดการ",
                booking_ids,
                key="select_booking_to_manage"
            )
        
        with col2:
            new_status = st.selectbox(
                "เปลี่ยนสถานะเป็น",
                ["pending", "approved", "rejected", "cancelled_by_user"],
                key="new_booking_status"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("✅ อัปเดตสถานะการจอง", use_container_width=True):
                update_booking_status(selected_booking_id, new_status)
        
        with col4:
            if st.button("🗑️ ลบการจอง", use_container_width=True):
                delete_booking(selected_booking_id)
    else:
        st.info("ℹ️ ไม่มีรายการจองให้จัดการ")

def update_booking_status(booking_id, new_status):
    """อัปเดตสถานะการจอง"""
    bookings = load_bookings()
    
    for i, booking in enumerate(bookings):
        if booking['booking_id'] == booking_id:
            bookings[i]['status'] = new_status
            save_bookings(bookings)
            st.success(f"✅ อัปเดตสถานะการจอง {booking_id[:8]}... เป็น '{new_status}' สำเร็จ")
            st.rerun()
            return
    
    st.error("❌ ไม่พบรายการจองที่เลือก")

def delete_booking(booking_id):
    """ลบการจอง"""
    bookings = load_bookings()
    original_len = len(bookings)
    bookings = [b for b in bookings if b['booking_id'] != booking_id]
    
    if len(bookings) < original_len:
        save_bookings(bookings)
        st.success(f"✅ ลบการจอง {booking_id[:8]}... สำเร็จ")
        st.rerun()
    else:
        st.error("❌ ไม่พบรายการจองที่เลือก")

def display_export_section(bookings):
    """แสดงส่วนส่งออกข้อมูล"""
    st.markdown("---")
    st.subheader("📤 ส่งออกข้อมูล")
    
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
            label="📥 ดาวน์โหลดข้อมูลการจองเป็น Excel",
            data=output,
            file_name=f"booking_data_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("ℹ️ ไม่มีข้อมูลการจองสำหรับส่งออก")

# --- หน้าจัดการผู้ใช้ (สำหรับแอดมิน) - ปรับปรุงใหม่ ---
def manage_users_page():
    load_css()
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">👥 จัดการผู้ใช้</div>
        <div class="app-subtitle">สำหรับผู้ดูแลระบบ</div>
    </div>
    """, unsafe_allow_html=True)

    users = load_users()
    
    if not users:
        st.info("ℹ️ ยังไม่มีผู้ใช้ในระบบ")
        if st.button("🏠 กลับหน้าหลัก"):
            st.session_state['current_page'] = 'main_page'
            st.rerun()
        return

    # แสดงรายการผู้ใช้
    display_users_list(users)
    
    # จัดการผู้ใช้
    display_user_management_section(users)
    
    # ส่งออกข้อมูลผู้ใช้
    display_users_export_section(users)

    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state['current_page'] = 'main_page'
        st.rerun()

def display_users_list(users):
    """แสดงรายการผู้ใช้"""
    st.subheader("📋 รายการผู้ใช้ทั้งหมด")
    
    users_list = list(users.values())
    df_users = pd.DataFrame(users_list)
    
    # เพิ่มคอลัมน์สถานะที่มี HTML
    df_users['สถานะ_HTML'] = df_users['status'].apply(get_status_badge)
    
    # เพิ่มไอคอนสำหรับบทบาท
    df_users['บทบาท_HTML'] = df_users['role'].apply(lambda x: '👑 แอดมิน' if x == 'admin' else '👤 ผู้ใช้')
    
    df_display_users = df_users[[
        'username', 'full_name', 'room_number', 'phone_number',
        'user_status', 'สถานะ_HTML', 'บทบาท_HTML'
    ]].rename(columns={
        'username': '👤 ชื่อผู้ใช้',
        'full_name': '📛 ชื่อ-นามสกุล',
        'room_number': '🏠 ห้องเลขที่',
        'phone_number': '📱 เบอร์โทรศัพท์',
        'user_status': '👥 สถานะผู้ใช้',
        'สถานะ_HTML': '📊 สถานะบัญชี',
        'บทบาท_HTML': '🎭 บทบาท'
    })
    
    st.dataframe(df_display_users, use_container_width=True, hide_index=True)

def display_user_management_section(users):
    """แสดงส่วนจัดการผู้ใช้"""
    st.markdown("---")
    st.subheader("⚙️ จัดการสถานะและบทบาทของผู้ใช้")

    user_names = list(users.keys())
    
    if user_names:
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            
            selected_user = st.selectbox(
                "👤 เลือกชื่อผู้ใช้ที่ต้องการจัดการ",
                user_names,
                key="select_user_to_manage"
            )

            current_user_info = users.get(selected_user, {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_status = st.selectbox(
                    "📊 เปลี่ยนสถานะบัญชี",
                    ["pending", "approved", "rejected"],
                    index=["pending", "approved", "rejected"].index(current_user_info.get('status', 'pending')),
                    key=f"status_for_{selected_user}"
                )
            
            with col2:
                new_role = st.selectbox(
                    "🎭 เปลี่ยนบทบาท",
                    ["user", "admin"],
                    index=["user", "admin"].index(current_user_info.get('role', 'user')),
                    key=f"role_for_{selected_user}"
                )

            col3, col4 = st.columns(2)
            
            with col3:
                if st.button("✅ อัปเดตสถานะและบทบาท", use_container_width=True):
                    update_user_status_and_role(selected_user, new_status, new_role)
            
            with col4:
                if st.button("🗑️ ลบผู้ใช้", use_container_width=True):
                    delete_user(selected_user)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("ℹ️ ไม่มีผู้ใช้ให้จัดการ")

def update_user_status_and_role(username, new_status, new_role):
    """อัปเดตสถานะและบทบาทของผู้ใช้"""
    users = load_users()
    
    if username in users:
        users[username]['status'] = new_status
        users[username]['role'] = new_role
        save_users(users)
        st.success(f"✅ อัปเดตข้อมูลของ '{username}' สำเร็จ - สถานะ: '{new_status}', บทบาท: '{new_role}'")
        st.rerun()
    else:
        st.error("❌ ไม่พบผู้ใช้ที่เลือก")

def delete_user(username):
    """ลบผู้ใช้"""
    if username == get_current_username():
        st.error("❌ ไม่สามารถลบบัญชีผู้ใช้ที่คุณกำลังล็อกอินอยู่ได้")
        return
    
    users = load_users()
    
    if username in users:
        del users[username]
        save_users(users)
        st.success(f"✅ ลบผู้ใช้ '{username}' สำเร็จ")
        st.rerun()
    else:
        st.error("❌ ไม่พบผู้ใช้ที่เลือก")

def display_users_export_section(users):
    """แสดงส่วนส่งออกข้อมูลผู้ใช้"""
    st.markdown("---")
    st.subheader("📤 ส่งออกข้อมูลผู้ใช้")
    
    if users:
        users_list = list(users.values())
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
            label="📥 ดาวน์โหลดข้อมูลผู้ใช้เป็น Excel",
            data=output_users,
            file_name=f"user_data_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("ℹ️ ไม่มีข้อมูลผู้ใช้สำหรับส่งออก")

# --- หน้าจัดการห้อง (สำหรับแอดมิน) - ปรับปรุงใหม่ ---
def manage_rooms_page():
    load_css()
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">🏢 จัดการห้อง</div>
        <div class="app-subtitle">สำหรับผู้ดูแลระบบ</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📋 รายการห้องกิจกรรมทั้งหมด")
    
    # แสดงข้อมูลห้องในรูปแบบ cards
    for room_name, room_info in ROOMS_DATA.items():
        st.markdown(f"""
        <div class="room-card">
            <div class="room-title">
                <span class="room-icon">{room_info.get('icon', '🏢')}</span>
                {room_name}
            </div>
            <div class="room-info">
                <strong>⏰ เวลาเปิด-ปิด:</strong> {room_info['open_time']} - {room_info['close_time']} น.
            </div>
            <div class="room-info">
                <strong>⏱️ ระยะเวลาการจอง:</strong> {room_info['duration_per_booking']} ชั่วโมง/ครั้ง
            </div>
            <div class="room-info">
                <strong>📅 จองล่วงหน้า:</strong> 
                {room_info.get('booking_advance_days', room_info.get('booking_advance_hours', 0))} 
                {'วัน' if 'booking_advance_days' in room_info else 'ชั่วโมง'}
            </div>
            <div class="room-info">
                <strong>👥 จำนวนผู้ใช้:</strong> 
                {f"{room_info.get('min_users', 1)}-{room_info.get('max_users', 1)} คน" if 'min_users' in room_info else f"สูงสุด {room_info.get('max_machines', 0)} เครื่อง"}
            </div>
            <div class="room-description">
                <strong>📋 รายละเอียด:</strong> {room_info['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # แสดงข้อมูลในรูปแบบตาราง
    st.subheader("📊 ข้อมูลห้องในรูปแบบตาราง")
    
    # สร้าง DataFrame จากข้อมูลห้อง
    rooms_data = []
    for room_name, room_info in ROOMS_DATA.items():
        room_data = {
            'ห้องกิจกรรม': f"{room_info.get('icon', '🏢')} {room_name}",
            'เวลาเปิด': room_info['open_time'],
            'เวลาปิด': room_info['close_time'],
            'ระยะเวลาการจอง (ชม.)': room_info['duration_per_booking'],
            'จองล่วงหน้า': f"{room_info.get('booking_advance_days', room_info.get('booking_advance_hours', 0))} {'วัน' if 'booking_advance_days' in room_info else 'ชม.'}",
            'จำนวนผู้ใช้/เครื่อง': f"{room_info.get('min_users', 1)}-{room_info.get('max_users', room_info.get('max_machines', 1))}"
        }
        rooms_data.append(room_data)
    
    rooms_df = pd.DataFrame(rooms_data)
    st.dataframe(rooms_df, use_container_width=True, hide_index=True)
    
    # ส่วนส่งออกข้อมูล
    st.markdown("---")
    st.subheader("📤 ส่งออกข้อมูลห้อง")
    
    output_rooms = BytesIO()
    with pd.ExcelWriter(output_rooms, engine='xlsxwriter') as writer:
        rooms_df.to_excel(writer, sheet_name='Rooms', index=False)
    output_rooms.seek(0)

    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลห้องเป็น Excel",
        data=output_rooms,
        file_name=f"rooms_data_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # ข้อความแจ้งเตือน
    st.info("ℹ️ **หมายเหตุ:** ในอนาคตหน้านี้จะอนุญาตให้แอดมินแก้ไข/เพิ่ม/ลบห้องได้")
    
    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state['current_page'] = 'main_page'
        st.rerun()

# --- ระบบนำทางหน้าเพจหลัก ---
def main():
    """ฟังก์ชันหลักสำหรับจัดการการนำทางระหว่างหน้า"""
    
    # ตั้งค่าเริ่มต้น
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'main_page'
    
    # กำหนดหน้าปัจจุบัน
    current_page = st.session_state['current_page']
    
    # นำทางไปยังหน้าที่เหมาะสม
    if current_page == 'main_page':
        main_page()
    elif current_page == 'login':
        login_page()
    elif current_page == 'register':
        register_page()
    elif current_page == 'booking_form':
        booking_form_page()
    elif current_page == 'my_bookings':
        my_bookings_page()
    elif current_page == 'manage_users':
        manage_users_page()
    elif current_page == 'manage_rooms':
        manage_rooms_page()
    elif current_page == 'admin_manage_bookings':
        admin_manage_bookings_page()
    else:
        # หากไม่พบหน้าที่ระบุ ให้กลับไปหน้าหลัก
        st.session_state['current_page'] = 'main_page'
        st.rerun()

# --- เพิ่มฟังก์ชันสำหรับ Mobile Optimization ---
def add_mobile_meta_tags():
    """เพิ่ม meta tags สำหรับ mobile optimization"""
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="theme-color" content="#667eea">
    """, unsafe_allow_html=True)

def add_pwa_manifest():
    """เพิ่ม PWA manifest สำหรับการติดตั้งเป็น app"""
    st.markdown("""
    <script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js');
        });
    }
    </script>
    """, unsafe_allow_html=True)

# --- เพิ่มฟังก์ชันสำหรับการแจ้งเตือน ---
def show_notification(message, type="info"):
    """แสดงการแจ้งเตือนแบบ toast"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    icon = icons.get(type, "ℹ️")
    
    st.markdown(f"""
    <div class="notification notification-{type}">
        <span class="notification-icon">{icon}</span>
        <span class="notification-message">{message}</span>
    </div>
    """, unsafe_allow_html=True)

# --- เพิ่ม CSS สำหรับ notifications ---
def add_notification_css():
    """เพิ่ม CSS สำหรับการแจ้งเตือน"""
    st.markdown("""
    <style>
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        z-index: 1000;
        display: flex;
        align-items: center;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    }
    
    .notification-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    
    .notification-message {
        flex: 1;
        font-weight: 500;
    }
    
    .notification-success {
        border-left: 4px solid #28a745;
    }
    
    .notification-error {
        border-left: 4px solid #dc3545;
    }
    
    .notification-warning {
        border-left: 4px solid #ffc107;
    }
    
    .notification-info {
        border-left: 4px solid #17a2b8;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @media (max-width: 768px) {
        .notification {
            right: 10px;
            left: 10px;
            min-width: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- เรียกใช้แอปพลิเคชัน ---
if __name__ == "__main__":
    # เพิ่ม mobile optimization
    add_mobile_meta_tags()
    add_notification_css()
    
    # เรียกใช้ฟังก์ชันหลัก
    main()


