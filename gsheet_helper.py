import json
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st


# Optional Google Sheets libs (required in requirements.txt)
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

# -------------------------
# Google Sheets helpers
# -------------------------
def get_gsheet_client_from_secrets():
    if gspread is None or Credentials is None:
        raise RuntimeError("gspread/google-auth not installed. Add to requirements.txt")
    sa_info = st.secrets.get("gcp_service_account")
    if not sa_info:
        raise RuntimeError("Missing Streamlit secret: gcp_service_account")
    creds = Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

def load_owned_from_sheet(sheet_id: str) -> List[str]:
    try:
        client = get_gsheet_client_from_secrets()
        sh = client.open_by_key(sheet_id)
        ws = sh.sheet1
        values = ws.col_values(1)
        return [v.strip() for v in values if v.strip()]
    except Exception as e:
        st.error(f"Failed to load owned tags from Google Sheet: {e}")
        return []

def save_owned_to_sheet(sheet_id: str, owned_list: List[str]):
    try:
        client = get_gsheet_client_from_secrets()
        sh = client.open_by_key(sheet_id)
        ws = sh.sheet1
        ws.clear()
        if owned_list:
            ws.update('A1', [[v] for v in owned_list])
        st.success("Saved owned tags to Google Sheet")
    except Exception as e:
        st.error(f"Failed to save owned tags to Google Sheet: {e}")

# -------------------------
# Local persistence fallback
# -------------------------
LOCAL_OWNED_FILE = Path("owned_tags.json")

def load_owned_local() -> List[str]:
    if LOCAL_OWNED_FILE.exists():
        try:
            return json.loads(LOCAL_OWNED_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_owned_local(owned_list: List[str]):
    try:
        LOCAL_OWNED_FILE.write_text(json.dumps(owned_list, ensure_ascii=False, indent=2), encoding="utf-8")
        st.sidebar.success(f"Saved {len(owned_list)} owned tags locally")
    except Exception as e:
        st.sidebar.error(f"Failed to save locally: {e}")

# -------------------------
# Load tags JSON (local file)
# -------------------------
DEFAULT_TAGS_FILE = "[03]stardust_v3_tags.json"
def load_tags(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        st.error(f"Tags file not found: {path}")
        return []
    with p.open(encoding="utf-8") as f:
        return json.load(f)
