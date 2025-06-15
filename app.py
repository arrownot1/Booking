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
                
                # สร้างไฟล์ Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    bookings_export_df.to_excel(writer, sheet_name='การจอง', index=False)
                
                st.download_button(
                    label="ดาวน์โหลดข้อมูลการจอง",
                    data=output.getvalue(),
                    file_name=f"booking_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            if st.button("ส่งออกข้อมูลผู้ใช้"):
                users_export_df = pd.read_sql_query("""
                    SELECT id, username, full_name, room_number, phone, status, 
                           approval_status, created_at
                    FROM users 
                    WHERE is_admin = 0
                    ORDER BY created_at DESC
                """, conn)
                
                # สร้างไฟล์ Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    users_export_df.to_excel(writer, sheet_name='ผู้ใช้', index=False)
                
                st.download_button(
                    label="ดาวน์โหลดข้อมูลผู้ใช้",
                    data=output.getvalue(),
                    file_name=f"users_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
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
