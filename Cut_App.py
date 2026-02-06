import streamlit as st

# --- 1. ตั้งค่ารหัสผ่าน ---
PASSWORD = "CK3006"  # <--- เปลี่ยนรหัสผ่านที่คุณต้องการที่นี่


def check_password():
    """ฟังก์ชันตรวจสอบรหัสผ่าน"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 ระบบคำนวณตัดอลูมิเนียม")
        pwd = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน", type="password")
        if st.button("ตกลง"):
            if pwd == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ รหัสผ่านไม่ถูกต้อง")
        return False
    return True


# --- 2. ฟังก์ชันคำนวณ ---
def calculate_cuts(stock_length, kerf, pieces_list):
    all_pieces = []
    for p in pieces_list:
        p_len = float(p.get('len', 0))
        p_qty = int(p.get('qty', 0))
        if p_len > 0 and p_qty > 0:
            all_pieces.extend([p_len] * p_qty)
    all_pieces.sort(reverse=True)
    used_stocks = []
    for piece in all_pieces:
        placed = False
        if piece > stock_length: continue
        for stock in used_stocks:
            if piece + kerf <= stock['remaining'] or (piece <= stock['remaining'] and len(stock['pieces']) == 0):
                stock['pieces'].append(piece)
                stock['remaining'] -= (piece + kerf)
                placed = True
                break
        if not placed:
            used_stocks.append({'remaining': stock_length - piece - kerf, 'pieces': [piece]})
    return used_stocks


# --- 3. ส่วนหลักของโปรแกรม ---
st.set_page_config(page_title="AluCut Pro", layout="wide")

if check_password():  # ตรวจสอบรหัสผ่านก่อนแสดงเนื้อหา
    if 'projects' not in st.session_state:
        st.session_state.projects = [{'name': 'ชนิดที่ 1', 'items': [{'len': 100.0, 'qty': 1}]}]

    with st.sidebar:
        st.header("⚙️ Settings")
        stock_len = st.number_input("ความยาวเส้นมาตรฐาน (ซม.)", value=640.0)
        kerf_val = st.number_input("ความหนาใบตัด (ซม.)", value=0.5)
        if st.button("🧹 ล้างข้อมูล"):
            st.session_state.projects = [{'name': 'ชนิดที่ 1', 'items': [{'len': 100.0, 'qty': 1}]}]
            st.rerun()
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.authenticated = False
            st.rerun()

    st.title("🪟 โปรแกรมคำนวณตัดอลูมิเนียม")

    for p_idx in range(len(st.session_state.projects)):
        with st.container(border=True):
            current_project = st.session_state.projects[p_idx]
            current_project['name'] = st.text_input(f"ชื่อชนิดอลูมิเนียม #{p_idx + 1}",
                                                    value=current_project.get('name', ''), key=f"p_input_{p_idx}")

            st.write("📏 **รายการขนาด (แนวนอน):**")
            item_cols = st.columns(4)
            for i in range(len(current_project['items'])):
                current_item = current_project['items'][i]
                with item_cols[i % 4]:
                    with st.container(border=True):
                        current_item['len'] = st.number_input(f"ยาว (ซม.)", value=float(current_item.get('len', 0)),
                                                              key=f"len_{p_idx}_{i}")
                        current_item['qty'] = st.number_input(f"จำนวน", value=int(current_item.get('qty', 0)),
                                                              min_value=1, key=f"qty_{p_idx}_{i}")

            c1, c2, _ = st.columns([0.15, 0.15, 0.7])
            with c1:
                if st.button(f"➕ เพิ่มขนาด", key=f"add_i_btn_{p_idx}"):
                    st.session_state.projects[p_idx]['items'].append({'len': 100.0, 'qty': 1})
                    st.rerun()

            if st.button(f"🚀 คำนวณ {current_project['name']}", key=f"calc_btn_{p_idx}", type="primary"):
                results = calculate_cuts(stock_len, kerf_val, current_project['items'])
                st.success(f"📊 ใช้ทั้งหมด {len(results)} เส้น")
                res_display = st.columns(3)
                for r_idx, res in enumerate(results):
                    with res_display[r_idx % 3]:
                        with st.expander(f"เส้นที่ {r_idx + 1}", expanded=True):
                            st.write(f"ตัด: `{res['pieces']}`")
                            st.write(f"เหลือ: {max(0, res['remaining']):.2f} ซม.")

    st.divider()
    if st.button("🏢 เพิ่มชนิดอลูมิเนียมใหม่ (แนวตั้ง)"):
        st.session_state.projects.append(
            {'name': f'ชนิดที่ {len(st.session_state.projects) + 1}', 'items': [{'len': 100.0, 'qty': 1}]})
        st.rerun()
