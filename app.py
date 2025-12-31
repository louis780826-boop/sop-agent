import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# --- 1. 設定頁面 ---
st.set_page_config(page_title="智能 SOP 生成器 Pro", page_icon="📝", layout="wide")

# --- 2. 門禁系統 (新增功能) ---
def check_password():
    """檢查用戶密碼是否正確"""
    if "APP_PASSWORD" not in st.secrets:
        # 如果忘了設密碼，預設不鎖，但會提示
        return True
    
    password_input = st.sidebar.text_input("🔑 請輸入通行密碼 (付費解鎖)", type="password")
    
    if password_input == st.secrets["APP_PASSWORD"]:
        return True
    else:
        # 👇 這裡填入您的 Gumroad 連結
        gumroad_link = "https://louisian5723.gumroad.com/l/wjxao" 
        
        st.sidebar.markdown(f"---")
        st.sidebar.warning("🔒 未輸入密碼或密碼錯誤")
        st.sidebar.markdown(f"""
        ### 如何獲取密碼？
        本工具為 VIP 專用功能。
        
        👉 **[點擊這裡購買通行證 (US$ 9)]({gumroad_link})**
        
        *付款後，系統會自動將密碼寄至您的信箱。*
        """)
        return False

# --- 3. 讀取 API Key ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # 如果通過了密碼驗證，才讓輸入 Key (雙重驗證)
    st.sidebar.divider()
    api_key = st.sidebar.text_input("API Key (管理員用)", type="password")

# --- 4. 核心邏輯開始 ---
# 如果密碼錯誤，直接停止執行，顯示鎖定畫面
if not check_password():
    st.warning("🔒 本工具為付費軟體，請輸入正確密碼以解鎖功能。")
    st.markdown("### 如何獲取密碼？")
    st.markdown("如果您有興趣使用此工具，請聯繫 [您的 Email] 或 [購買連結] 獲取通行密碼。")
    st.stop()  # ⛔ 這裡是很重要的指令，程式會停在這裡，不會往下跑

# --- 以下是原本的功能 (只有密碼正確才會執行到這裡) ---

def generate_sop(raw_text):
    if not api_key:
        st.error("❌ 系統偵測到 API Key 缺失，請檢查設定。")
        return None
    
    try:
        genai.configure(api_key=api_key)
        # 使用您剛才測試成功的最新模型
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = """
        你是一位企業流程專家。請將用戶輸入的內容整理成結構化的 SOP。
        輸出格式要求：
        1. 使用 Markdown 格式。
        2. 包含「目標」、「前置準備」、「執行步驟」、「風險提示」。
        3. 不要使用 Mermaid 代碼，請用文字描述流程即可。
        """
        
        with st.spinner("🤖 AI 正在撰寫文檔中..."):
            response = model.generate_content(f"{system_prompt}\n\n用戶輸入：\n{raw_text}")
            return response.text
            
    except Exception as e:
        st.error(f"發生錯誤：{e}")
        return None

def create_docx(text):
    doc = Document()
    doc.add_heading('標準作業程序 (SOP)', 0)
    for line in text.split('\n'):
        if line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=1)
        elif line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=2)
        elif line.strip() != "":
            doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 主畫面 UI ---
st.title("📝 企業級 SOP 智能生成器 (VIP版)")
st.success("🔓 驗證成功！歡迎使用專業版功能。")

col1, col2 = st.columns(2)

with col1:
    user_input = st.text_area("輸入內容", height=400, placeholder="請貼上會議記錄或語音轉文字稿...")
    generate_btn = st.button("🚀 生成 SOP", type="primary", use_container_width=True)

with col2:
    if generate_btn and user_input:
        result = generate_sop(user_input)
        if result:
            st.session_state['result'] = result
            
    if 'result' in st.session_state:
        st.markdown("### 📄 預覽結果")
        st.markdown(st.session_state['result'])
        st.divider()
        docx_file = create_docx(st.session_state['result'])
        st.download_button(
            label="📥 下載 Word 檔案 (.docx)",
            data=docx_file,
            file_name="SOP_Output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )