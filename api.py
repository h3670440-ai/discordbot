from flask import Flask, request, jsonify
import sqlite3
import os
import threading
import subprocess
import time
import datetime

app = Flask(__name__)

@app.route('/')
def health():
    return "OK", 200

@app.route('/check', methods=['GET'])
def check():
    conn = None
    try:
        key_code = request.args.get('key')
        hwid = request.args.get('hwid')
        
        print(f"API: Request for key='{key_code}', hwid='{hwid}'")
        
        if not key_code or not hwid:
            return jsonify({"valid": False, "reason": "Missing key or HWID"}), 200
        
        key_code = key_code.strip()
        hwid = hwid.strip()
        
        conn = sqlite3.connect("vanity.db", timeout=10)
        cursor = conn.cursor()
        
        # Check if key exists
        cursor.execute("SELECT is_redeemed, redeemed_by, hwid, expiration FROM keys WHERE key = ?", (key_code,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"valid": False, "reason": "Invalid key"}), 200
        
        is_redeemed, user_id, saved_hwid, expiration = row
        
        # Check if key has been redeemed
        if is_redeemed == 0:
            return jsonify({"valid": False, "reason": "Key not redeemed. Please redeem your key first"}), 200
        
        # Check Expiration
        if expiration is not None and expiration != "":
            try:
                exp_dt = datetime.datetime.fromisoformat(expiration)
                if datetime.datetime.now() > exp_dt:
                    return jsonify({"valid": False, "reason": "Key expired"}), 200
            except Exception as e:
                print(f"API: Expiration parse error: {e}")
                pass # If parsing fails, assume lifetime
        
        # Check blacklist
        if user_id is not None:
            cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return jsonify({"valid": False, "reason": "Blacklisted user"}), 200
            
        # Check HWID
        if saved_hwid is None or saved_hwid == "":
            # Bind HWID on first use
            cursor.execute("UPDATE keys SET hwid = ? WHERE key = ?", (hwid, key_code))
            conn.commit()
            print(f"API: Bound key {key_code} to HWID {hwid}")
        elif saved_hwid != hwid:
            return jsonify({"valid": False, "reason": "HWID mismatch. Use /resethwid to reset"}), 200
            
        return jsonify({"valid": True, "reason": "success"}), 200
        
    except Exception as e:
        print(f"API Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"valid": False, "reason": "Server error. Please try again"}), 200
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def init_db():
    print("API: Initializing Database...")
    conn = sqlite3.connect("vanity.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY,
        duration TEXT,
        expiration TIMESTAMP,
        is_redeemed INTEGER DEFAULT 0,
        redeemed_by INTEGER,
        hwid TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS blacklists (
        user_id INTEGER PRIMARY KEY
    )''')
    conn.commit()
    conn.close()
    print("API: Database ready.")

def run_bot():
    print("API: Starting Discord Bot...")
    try:
        # Use sys.executable to ensure we use the same python interpreter
        import sys
        subprocess.run([sys.executable, "bot.py"])
    except Exception as e:
        print(f"API: Bot failed to start: {e}")

if __name__ == '__main__':
    init_db()
    
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.getenv('PORT', 8080))
    print(f"API: Listening on port {port}")
    
    # Use threaded=True to handle concurrent requests better
    app.run(host='0.0.0.0', port=port, threaded=True)
