"""
PocketAgent Backend Server
==========================
Proxies Clash of Agents API calls so the mobile app
can register fighters without CORS issues.

Deploy free on Railway: railway.app
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

# Allow requests from your Netlify app and any localhost for dev
CORS(app, origins=[
    "https://gentle-salamander-09914a.netlify.app",
    "https://mypoag.netlify.app",
    "https://mypoag.app",
    "http://localhost:*",
    "http://127.0.0.1:*",
    "*"  # open during development — lock this down once live
])

CLASH_BASE = "https://clashofagents.org"

# ─── Health check ────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "PocketAgent Backend"})

# ─── Register a new fighter ───────────────────────────────────────────────────

@app.route("/clash/register", methods=["POST"])
def clash_register():
    try:
        body = request.get_json()
        if not body or not body.get("name"):
            return jsonify({"error": "Fighter name is required"}), 400

        resp = requests.post(
            f"{CLASH_BASE}/api/register",
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        return jsonify(resp.json()), resp.status_code

    except requests.exceptions.Timeout:
        return jsonify({"error": "Clash of Agents server timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Get fighter status ───────────────────────────────────────────────────────

@app.route("/clash/me", methods=["GET"])
def clash_me():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        resp = requests.get(
            f"{CLASH_BASE}/api/me",
            headers={"x-api-key": api_key},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Get leaderboard ─────────────────────────────────────────────────────────

@app.route("/clash/leaderboard", methods=["GET"])
def clash_leaderboard():
    try:
        resp = requests.get(f"{CLASH_BASE}/api/leaderboard", timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Get active fights ────────────────────────────────────────────────────────

@app.route("/clash/fights/active", methods=["GET"])
def clash_active_fights():
    try:
        resp = requests.get(f"{CLASH_BASE}/api/fights/active", timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Send challenge ───────────────────────────────────────────────────────────

@app.route("/clash/challenge", methods=["POST"])
def clash_challenge():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(
            f"{CLASH_BASE}/api/challenge",
            json=body,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Fight action ─────────────────────────────────────────────────────────────

@app.route("/clash/fight/<fight_id>/action", methods=["POST"])
def clash_fight_action(fight_id):
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(
            f"{CLASH_BASE}/api/fight/{fight_id}/action",
            json=body,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Train stat ───────────────────────────────────────────────────────────────

@app.route("/clash/train", methods=["POST"])
def clash_train():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(
            f"{CLASH_BASE}/api/train",
            json=body,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Post to lounge ───────────────────────────────────────────────────────────

@app.route("/clash/chat", methods=["POST"])
def clash_chat():
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401
    try:
        body = request.get_json() or {}
        resp = requests.post(
            f"{CLASH_BASE}/api/chat/general",
            json=body,
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
