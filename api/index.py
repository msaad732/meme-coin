"""Vercel serverless function - returns latest message from Supabase."""
import json
import os
import psycopg
from psycopg.rows import dict_row


def handler(req):
    """Vercel Python handler - returns latest message."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "DATABASE_URL not configured"}),
        }
    
    try:
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ts, channel_id, channel_name, author_id, author, content FROM messages ORDER BY ts DESC LIMIT 1"
            )
            row = cur.fetchone()
        conn.close()
        
        if row:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(dict(row), default=str),
            }
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "No messages found"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }

