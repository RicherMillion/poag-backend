"""
PocketAgent Backend Server
==========================
- Magic link email auth (Resend)
- PostgreSQL database (Render)
- Clash of Agents API proxy
- POAG storage per user
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import psycopg2
import psycopg2.extras
import secrets
import time
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, origins=["*"])

CLASH_BASE = "https://clashofagents.org"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
APP_URL = os.environ.get("APP_URL", "https://poag-backend-1.onrender.com")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# ─── Database ─────────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    if not DATABASE_URL:
        return
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS magic_links (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS poags (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                type TEXT NOT NULL,
                personality TEXT NOT NULL,
                tracks JSONB DEFAULT '{}',
                clash_fighter_name TEXT,
                clash_api_key TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized")
    except Exception as e:
        print(f"DB init error: {e}")

# ─── Auth helpers ─────────────────────────────────────────────────────────────

def get_user_from_token(token):
    if not token or not DATABASE_URL:
        return None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.* FROM users u
            JOIN sessions s ON s.user_id = u.id
            WHERE s.token = %s
        """, (token,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except:
        return None

def send_magic_link(email, token):
    magic_url = f"{APP_URL}/auth/verify?token={token}"
    if not RESEND_API_KEY:
        print(f"[DEV] Magic link: {magic_url}")
        return True
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": "PocketAgent <noreply@mypoag.app>",
                "to": [email],
                "subject": "Your PocketAgent login link",
                "html": f"""
                <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px">
                  <h1 style="font-size:24px;margin-bottom:8px">PocketAgent</h1>
                  <p style="color:#666;margin-bottom:24px">Click the button below to sign in. This link expires in 15 minutes.</p>
                  <a href="{magic_url}" style="background:#7c6fff;color:#fff;padding:14px 28px;border-radius:10px;text-decoration:none;font-weight:600;display:inline-block">Sign In to PocketAgent</a>
                  <p style="color:#999;font-size:12px;margin-top:24px">If you didn't request this, ignore this email.</p>
                </div>
                """
            },
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ─── Health ───────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "PocketAgent Backend", "db": bool(DATABASE_URL)})

# ─── Auth: request magic link ─────────────────────────────────────────────────

@app.route("/auth/login", methods=["POST"])
def auth_login():
    if not DATABASE_URL:
        return jsonify({"error": "Database not configured"}), 500
    try:
        body = request.get_json()
        email = body.get("email", "").strip().lower()
        if not email or "@" not in email:
            return jsonify({"error": "Valid email required"}), 400

        conn = get_db()
        cur = conn.cursor()

        # Create user if doesn't exist
        cur.execute("INSERT INTO users (email) VALUES (%s) ON CONFLICT (email) DO NOTHING", (email,))

        # Create magic link token
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(minutes=15)
        cur.execute("INSERT INTO magic_links (email, token, expires_at) VALUES (%s, %s, %s)", (email, token, expires))
        conn.commit()
        cur.close()
        conn.close()

        sent = send_magic_link(email, token)
        return jsonify({"success": True, "sent": sent, "message": "Check your email for a login link"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Auth: verify magic link ──────────────────────────────────────────────────

@app.route("/auth/verify", methods=["GET"])
def auth_verify():
    token = request.args.get("token")
    if not token:
        return "<h2>Invalid link</h2>", 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM magic_links
            WHERE token = %s AND used = FALSE AND expires_at > NOW()
        """, (token,))
        link = cur.fetchone()
        if not link:
            return "<h2>Link expired or already used</h2>", 400

        # Mark used
        cur.execute("UPDATE magic_links SET used = TRUE WHERE id = %s", (link["id"],))

        # Get user
        cur.execute("SELECT * FROM users WHERE email = %s", (link["email"],))
        user = cur.fetchone()

        # Create session
        session_token = secrets.token_urlsafe(32)
        cur.execute("INSERT INTO sessions (user_id, token) VALUES (%s, %s)", (user["id"], session_token))
        conn.commit()
        cur.close()
        conn.close()

        # Redirect back to app with session token
        return f"""
        <html><head><script>
        localStorage.setItem('poag_session', '{session_token}');
        localStorage.setItem('poag_email', '{user["email"]}');
        window.location.href = '{APP_URL.replace("poag-backend-1.onrender.com", "poag-backend-1.onrender.com")}?session={session_token}&email={user["email"]}';
        </script></head><body>Signing you in...</body></html>
        """
    except Exception as e:
        return f"<h2>Error: {e}</h2>", 500

# ─── Get current user ─────────────────────────────────────────────────────────

@app.route("/auth/me", methods=["GET"])
def auth_me():
    token = request.headers.get("x-session-token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"id": user["id"], "email": user["email"]})

# ─── POAGs ────────────────────────────────────────────────────────────────────

@app.route("/poags", methods=["GET"])
def get_poags():
    token = request.headers.get("x-session-token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM poags WHERE user_id = %s ORDER BY created_at DESC", (user["id"],))
        poags = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(p) for p in poags])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/poags", methods=["POST"])
def create_poag():
    token = request.headers.get("x-session-token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    try:
        body = request.get_json()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO poags (user_id, type, personality, tracks, clash_fighter_name, clash_api_key)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
        """, (
            user["id"],
            body.get("type"),
            body.get("personality"),
            json.dumps(body.get("tracks", {})),
            body.get("clash_fighter_name"),
            body.get("clash_api_key")
        ))
        poag = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(dict(poag)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/poags/<int:poag_id>", methods=["DELETE"])
def delete_poag(poag_id):
    token = request.headers.get("x-session-token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM poags WHERE id = %s AND user_id = %s", (poag_id, user["id"]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Clash proxy ──────────────────────────────────────────────────────────────

@app.route("/clash/register", methods=["POST"])
def clash_register():
    try:
        body = request.get_json()
        if not body or not body.get("name"):
            return jsonify({"error": "Fighter name is required"}), 400
        resp = requests.post(f"{CLASH_BASE}/api/register", json=body, headers={"Content-Type": "application/json"}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Clash of Agents server timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clash/me", methods=["GET"])
def clash_me():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        resp = requests.get(f"{CLASH_BASE}/api/me", headers={"x-api-key": api_key}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clash/leaderboard", methods=["GET"])
def clash_leaderboard():
    try:
        resp = requests.get(f"{CLASH_BASE}/api/leaderboard", timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clash/challenge", methods=["POST"])
def clash_challenge():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(f"{CLASH_BASE}/api/challenge", json=body, headers={"x-api-key": api_key, "Content-Type": "application/json"}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clash/fight/<fight_id>/action", methods=["POST"])
def clash_fight_action(fight_id):
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(f"{CLASH_BASE}/api/fight/{fight_id}/action", json=body, headers={"x-api-key": api_key, "Content-Type": "application/json"}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clash/train", methods=["POST"])
def clash_train():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(f"{CLASH_BASE}/api/train", json=body, headers={"x-api-key": api_key, "Content-Type": "application/json"}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clash/chat", methods=["POST"])
def clash_chat():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(f"{CLASH_BASE}/api/chat/general", json=body, headers={"x-api-key": api_key, "Content-Type": "application/json"}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Arena42 proxy ───────────────────────────────────────────────────────────

ARENA42_BASE = "https://api.arena42.ai"

@app.route("/arena42/register", methods=["POST"])
def arena42_register():
    try:
        body = request.get_json()
        if not body or not body.get("name"):
            return jsonify({"error": "Agent name is required"}), 400
        resp = requests.post(
            f"{ARENA42_BASE}/api/v1/agents/register",
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Arena42 server timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/arena42/competitions", methods=["GET"])
def arena42_competitions():
    try:
        resp = requests.get(
            f"{ARENA42_BASE}/api/competitions?joinable=true&compact=true",
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/arena42/join", methods=["POST"])
def arena42_join():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        competition_id = body.get("competition_id")
        resp = requests.post(
            f"{ARENA42_BASE}/api/competitions/{competition_id}/participants",
            json=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/arena42/action", methods=["POST"])
def arena42_action():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        competition_id = body.get("competition_id")
        resp = requests.post(
            f"{ARENA42_BASE}/api/competitions/{competition_id}/actions",
            json=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Run ──────────────────────────────────────────────────────────────────────

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
