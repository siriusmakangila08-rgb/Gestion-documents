from pathlib import Path
import base64
import mimetypes
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
st.set_page_config(
    page_title="Documents NETUBEX SARL",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)
st.markdown("""
<style>
#MainMenu, header, footer, [data-testid="stSidebar"] { visibility: hidden; display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] > .main { overflow: hidden; }
iframe[title="streamlit.components.v1.html"] { width: 100%; border: 0; display: block; }
</style>
""", unsafe_allow_html=True)


def file_to_data_url(path: Path) -> str:
    """Encode un fichier local en data: URL base64."""
    if not path.exists():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


# Logo NETUBEX
logo_path = ROOT / "assets" / "logo-netubex.svg"
logo_data_url = file_to_data_url(logo_path) if logo_path.exists() else ""

# Bibliothèques PDF embarquées localement (évite les pannes CDN)
jspdf_path = ROOT / "assets" / "jspdf.umd.min.js"
html2canvas_path = ROOT / "assets" / "html2canvas.min.js"
jspdf_data_url = file_to_data_url(jspdf_path)
html2canvas_data_url = file_to_data_url(html2canvas_path)

html_path = ROOT / "documents_ui.html"
css_path = ROOT / "documents.css"
js_path = ROOT / "documents.js"

if not html_path.exists():
    st.error(f"Fichier introuvable : {html_path}")
    st.stop()

html = html_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
js = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

# Injection du CSS, JS et du logo
html = html.replace("/*__CSS__*/", css).replace("/*__JS__*/", js)
html = html.replace("__DEFAULT_LOGO_DATA_URL__", logo_data_url)

# Remplacement des scripts CDN par les versions locales embarquées (data: URL)
if jspdf_data_url:
    html = html.replace(
        'src="https://unpkg.com/jspdf@3.0.3/dist/jspdf.umd.min.js"',
        f'src="{jspdf_data_url}"'
    )
if html2canvas_data_url:
    html = html.replace(
        'src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"',
        f'src="{html2canvas_data_url}"'
    )

# Hauteur généreuse pour ne pas couper le contenu
components.html(html, height=1080, scrolling=True)