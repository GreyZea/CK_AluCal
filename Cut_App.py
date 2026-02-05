import streamlit as st

def calculate_cuts(stock_length, kerf, pieces):
    all_pieces = []
    for length, count in pieces:
        all_pieces.extend([length] * count)
    all_pieces.sort(reverse=True)
    used_stocks = []
    for piece in all_pieces:
        placed = False
        if piece + kerf > stock_length: continue
        for stock in used_stocks:
            if piece + kerf <= stock['remaining']:
                stock['pieces'].append(piece); stock['remaining'] -= (piece + kerf)
                placed = True; break
        if not placed:
            used_stocks.append({'remaining': stock_length - piece - kerf, 'pieces': [piece]})
    return used_stocks

st.set_page_config(page_title="AluCut", layout="wide")
st.title("🪟 โปรแกรมคำนวณตัดอลูมิเนียม")

# ค่าพื้นฐาน
stock_len = st.sidebar.number_input("ความยาวเส้นอลูมิเนียม (ซม.)", value=640.0)
kerf_val = st.sidebar.number_input("ความหนาใบตัด (ซม.)", value=0.5)

if 'rows' not in st.session_state:
    st.session_state.rows = [{'len': 100.0, 'qty': 1}]

def add_row(): st.session_state.rows.append({'len': 100.0, 'qty': 1})

st.write("### 📝 รายการชิ้นงาน")
for i, row in enumerate(st.session_state.rows):
    c1, c2 = st.columns(2)
    with c1: st.session_state.rows[i]['len'] = st.number_input(f"ยาว (ซม.)", value=row['len'], key=f"l_{i}")
    with c2: st.session_state.rows[i]['qty'] = st.number_input(f"จำนวน", value=row['qty'], min_value=1, key=f"q_{i}")

st.button("➕ เพิ่มแถว", on_click=add_row)

if st.button("🚀 คำนวณตอนนี้"):
    data = [[r['len'], r['qty']] for r in st.session_state.rows]
    results = calculate_cuts(stock_len, kerf_val, data)
    st.header(f"📊 สรุป: ใช้ทั้งหมด {len(results)} เส้น")
    cols = st.columns(3)
    for i, res in enumerate(results):
        with cols[i%3]:
            with st.expander(f"เส้นที่ {i+1}"):
                st.write(f"ตัด: `{res['pieces']}`")
                st.write(f"เหลือเศษ: {res['remaining']:.2f} ซม.")
