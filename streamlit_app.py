import json
import time
from pathlib import Path
import os
from typing import List, Dict

import streamlit as st
import psycopg
from psycopg.rows import dict_row


DATA_FILE = Path("data") / "messages.jsonl"
DATABASE_URL = os.getenv("DATABASE_URL")


def _load_from_jsonl(limit: int = 100) -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    messages = []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines
                continue
    messages.sort(key=lambda m: m.get("ts", 0), reverse=True)
    return messages[:limit]


def _load_from_postgres(limit: int = 100) -> List[Dict]:
    if not DATABASE_URL:
        return []
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ts, channel_id, channel_name, author_id, author, content
                FROM messages
                ORDER BY ts DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return list(rows)
    finally:
        conn.close()


def load_messages(limit: int = 100) -> List[Dict]:
    if DATABASE_URL:
        try:
            return _load_from_postgres(limit)
        except Exception as e:
            st.warning(f"DB read failed, falling back to local file: {e}")
            return _load_from_jsonl(limit)
    return _load_from_jsonl(limit)


st.set_page_config(page_title="Meme Tracker", layout="wide")
st.title("MemeTrackerBot – Recent Messages")

col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("Controls")
    limit = st.slider("Max messages", min_value=10, max_value=500, value=100, step=10)
    if st.button("Refresh"):
        st.rerun()

with col1:
    st.subheader("Latest Activity")
    msgs = load_messages(limit=limit)
    if not msgs:
        st.info("No messages stored yet. The bot will write here when it sees a target message.")
    else:
        latest = msgs[0]
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(latest.get("ts", 0)))
        st.markdown(f"**Most recent:** {ts_str} — {latest.get('author')} in #{latest.get('channel_name') or latest.get('channel_id')}")
        st.code(latest.get("content", ""))

st.divider()
st.subheader("All Recent Messages")

msgs = load_messages(limit=limit)
if msgs:
    # Render as a simple table
    st.dataframe(
        [
            {
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(m.get("ts", 0))) + " UTC",
                "channel": m.get("channel_name") or m.get("channel_id"),
                "author": m.get("author"),
                "content": m.get("content"),
            }
            for m in msgs
        ],
        use_container_width=True,
        hide_index=True,
    )




