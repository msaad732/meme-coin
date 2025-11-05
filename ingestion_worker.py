import discord
from discord.ext import commands
import os
import time
import json
from pathlib import Path
import asyncio
from typing import Optional
import psycopg
from psycopg.rows import dict_row

# 1. Configuration (Load Keys Securely)
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g., postgres://user:pass@host:port/db
# << REPLACE with client's actual channel IDs
# Note: These must be integers, not strings.
TARGET_CHANNEL_IDS = [1221851803214413925]  

# Set Intents: REQUIRED for the bot to read message content
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Initialize the Bot Client
bot = commands.Bot(command_prefix='!', intents=intents)


def ensure_db_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id BIGSERIAL PRIMARY KEY,
                ts BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                channel_name TEXT,
                author_id BIGINT NOT NULL,
                author TEXT NOT NULL,
                content TEXT NOT NULL
            );
            """
        )
        conn.commit()


# Global connection cache (lazy connection)
_db_conn = None


def get_db_connection():
    """Get database connection (lazy initialization). Returns None if connection fails."""
    global _db_conn
    
    if not DATABASE_URL:
        return None
    
    # Return cached connection if available
    if _db_conn is not None:
        try:
            # Test if connection is still alive
            with _db_conn.cursor() as cur:
                cur.execute("SELECT 1")
            return _db_conn
        except:
            # Connection is dead, reset it
            _db_conn = None
    
    # Try to create new connection
    try:
        # Try connecting with IPv4 preference and connection timeout
        conn = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            connect_timeout=10
        )
        ensure_db_schema(conn)
        _db_conn = conn
        print("✅ Database connection established")
        return conn
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("⚠️ Falling back to JSONL file storage")
        _db_conn = None
        return None


def _insert_message_sync(record: dict) -> None:
    """Insert message to database. Falls back silently if DB unavailable."""
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (ts, channel_id, channel_name, author_id, author, content)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    record["ts"],
                    record["channel_id"],
                    record.get("channel_name"),
                    record["author_id"],
                    record["author"],
                    record["content"],
                ),
            )
            conn.commit()
    except Exception as e:
        print(f"⚠️ Database write failed: {e}")
        # Reset connection on error so it retries next time
        global _db_conn
        _db_conn = None


@bot.event
async def on_ready():
    """Confirms the bot has logged into Discord."""
    print(f'✅ Discord Bot Logged in as {bot.user}')
    print(f'Listening for messages in channels: {TARGET_CHANNEL_IDS}')
    
    # Try to connect to database on startup (non-blocking, won't crash if fails)
    if DATABASE_URL:
        print("Attempting database connection...")
        await asyncio.to_thread(get_db_connection)
    else:
        print("⚠️ No DATABASE_URL set, using JSONL file storage only")
    print()


@bot.event
async def on_message(message):
    """Event handler for every new message received."""
    
    # 1. Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # 2. Check if the message is in one of the target channels
    if message.channel.id in TARGET_CHANNEL_IDS:
        content = message.content.strip()
        
        # --- SIMPLE MESSAGE STORAGE/OUTPUT ---
        
        print("-" * 50)
        print(f"[{time.strftime('%H:%M:%S', time.localtime())} UTC] New Message Detected:")
        print(f"Channel ID: {message.channel.id}")
        print(f"Author: {message.author.display_name}")
        print("\n--- CONTENT START ---")
        print(content)
        print("--- CONTENT END ---\n")

        # Build record
        record = {
            "ts": int(time.time()),
            "channel_id": message.channel.id,
            "channel_name": getattr(message.channel, "name", None),
            "author_id": message.author.id,
            "author": message.author.display_name,
            "content": content,
        }

        # Try Postgres first if DATABASE_URL is set, fallback to JSONL
        if DATABASE_URL:
            # Try DB write (will fallback silently if DB unavailable)
            await asyncio.to_thread(_insert_message_sync, record)
        
        # Always write to JSONL as backup (or if no DATABASE_URL)
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        with (data_dir / "messages.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # --- END SIMPLE MESSAGE STORAGE/OUTPUT ---

    await bot.process_commands(message)


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("FATAL ERROR: DISCORD_TOKEN not found in environment variables.")
    else:
        # Run the bot and keep it connected
        # IMPORTANT: Make sure you have your DISCORD_TOKEN set up in a .env file
        # And your bot has the necessary permissions (Message Content Intent enabled)
        bot.run(DISCORD_TOKEN)
