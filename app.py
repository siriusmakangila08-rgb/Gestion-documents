from pathlib import Path
import base64
import mimetypes
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Documents NETUBEX SARL", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
#MainMenu, header, footer, [data-testid="stSidebar"] { visibility: hidden; display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] > .main { overflow: hidden; }
iframe[title="streamlit.components.v1.html"] { width: 100%; border: 0; }
</style>
""", unsafe_allow_html=True)

logo_path = ROOT / "assets" / "logo-netubex.svg"
logo_data_url = ""
if logo_path.exists():
    mime_type = mimetypes.guess_type(logo_path.name)[0] or "image/svg+xml"
    logo_data_url = "data:" + mime_type + ";base64," + base64.b64encode(logo_path.read_bytes()).decode("ascii")

html = (ROOT / "documents_ui.html").read_text(encoding="utf-8")
css = (ROOT / "documents.css").read_text(encoding="utf-8")
js = (ROOT / "documents.js").read_text(encoding="utf-8")
html = html.replace("/*__CSS__*/", css).replace("/*__JS__*/", js)
html = html.replace("__DEFAULT_LOGO_DATA_URL__", logo_data_url)

st.iframe(html, height=970)

