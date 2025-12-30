import streamlit as st
import google.generativeai as genai
from docx import Document # 新增：處理 Word
from io import BytesIO    # 新增：處理檔案流
import os

# --- 設定頁面 ---
st.set_page_config(page_title="智能 SOP 生成器 Pro", page_icon="📝", layout="wide")

# --- 讀取 Key (優先讀取 secrets, 否則讀取輸入框) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.sidebar.title("🔧 設定")
    api_key = st.sidebar.text_input("請輸入 Gemini API Key", type="password")

# --- 核心函數：呼叫 Gemini ---
def generate_sop(raw_text):
    if not api_key:
        st.error("❌ 請先設定 API Key")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = """
        你是一位企業流程專家。請將用戶輸入的內容整理成結構化的 SOP。
        輸出格式要求：
        1. 使用 Markdown 格式。
        2. 包含「目標」、「前置準備」、「執行步驟」、「風險提示」。
        3. 不要使用 Mermaid 代碼，請用文字描述流程即可（為了方便轉 Word）。
        """
        
        with st.spinner("🤖 AI 正在撰寫文檔中..."):
            response = model.generate_content(f"{system_prompt}\n\n用戶輸入：\n{raw_text}")
            return response.text
            
    except Exception as e:
        st.error(f"發生錯誤：{e}")
        return None

# --- 新增函數：將文字轉為 Word ---
def create_docx(text):
    doc = Document()
    doc.add_heading('標準作業程序 (SOP)', 0)
    
    # 簡單將 AI 產出的文字寫入 Word
    for line in text.split('\n'):
        if line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=1)
        elif line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=2)
        elif line.strip() != "":
            doc.add_paragraph(line)
            
    # 存到記憶體中
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 主畫面 UI ---
st.title("📝 企業級 SOP 智能生成器 (Pro版)")
st.markdown("### 雜亂筆記 ➡️ 專業 Word 文檔")

col1, col2 = st.columns(2)

with col1:
    user_input = st.text_area("輸入內容", height=400, placeholder="請貼上會議記錄或語音轉文字稿...")
    generate_btn = st.button("🚀 生成 SOP", type="primary", use_container_width=True)

with col2:
    if generate_btn and user_input:
        result = generate_sop(user_input)
        if result:
            st.session_state['result'] = result # 存起來
            
    # 顯示結果與下載按鈕
    if 'result' in st.session_state:
        st.markdown("### 📄 預覽結果")
        st.markdown(st.session_state['result'])
        
        st.divider() # 分隔線
        
        # 製作 Word 檔
        docx_file = create_docx(st.session_state['result'])
        
        # 下載按鈕
        st.download_button(
            label="📥 下載 Word 檔案 (.docx)",
            data=docx_file,
            file_name="SOP_Output.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )