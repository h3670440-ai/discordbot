"""
Simplified API that focuses on just the Flask server
Run the Discord bot separately if needed
"""
from flask import Flask, request, jsonify
import sqlite3
import os
import datetime

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "online",
        "service": "Vanity API",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200

@app.route('/test')
def test():
    """Test endpoint to verify database connectivity"""
    try:
        conn = sqlite3.connect("vanity.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM keys")
        key_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blacklists")
        blacklist_count = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            "status": "ok",
            "database": "connected",
            "keys": key_count,
            "blacklists": blacklist_count
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 200

@app.route('/check', methods=['GET'])
def check():
    conn = None
    try:
        key_code = request.args.get('key')
        hwid = request.args.get('hwid')
        
        print(f"[CHECK] Request received - key='{key_code}', hwid='{hwid}'")
        
        if not key_code or not hwid:
            print("[CHECK] Missing parameters")
            return jsonify({"valid": False, "reason": "Missing key or HWID"}), 200
        
        key_code = key_code.strip()
        hwid = hwid.strip()
        
        print(f"[CHECK] Connecting to database...")
        conn = sqlite3.connect("vanity.db", timeout=10)
        cursor = conn.cursor()
        
        # Check if key exists
        print(f"[CHECK] Querying key: {key_code}")
        cursor.execute("SELECT is_redeemed, redeemed_by, hwid, expiration FROM keys WHERE key = ?", (key_code,))
        row = cursor.fetchone()
        
        if not row:
            print(f"[CHECK] Key not found: {key_code}")
            return jsonify({"valid": False, "reason": "Invalid key"}), 200
        
        is_redeemed, user_id, saved_hwid, expiration = row
        print(f"[CHECK] Key found - is_redeemed={is_redeemed}, user_id={user_id}, saved_hwid={saved_hwid}")
        
        # Check if key has been redeemed
        if is_redeemed == 0:
            print(f"[CHECK] Key not redeemed yet")
            return jsonify({"valid": False, "reason": "Key not redeemed. Please redeem your key first"}), 200
        
        # Check Expiration
        if expiration is not None and expiration != "":
            try:
                exp_dt = datetime.datetime.fromisoformat(expiration)
                if datetime.datetime.now() > exp_dt:
                    print(f"[CHECK] Key expired: {expiration}")
                    return jsonify({"valid": False, "reason": "Key expired"}), 200
            except Exception as e:
                print(f"[CHECK] Expiration parse error: {e}")
                pass
        
        # Check blacklist
        if user_id is not None:
            cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                print(f"[CHECK] User blacklisted: {user_id}")
                return jsonify({"valid": False, "reason": "Blacklisted user"}), 200
            
        # Check HWID
        if saved_hwid is None or saved_hwid == "":
            # Bind HWID on first use
            cursor.execute("UPDATE keys SET hwid = ? WHERE key = ?", (hwid, key_code))
            conn.commit()
            print(f"[CHECK] Bound key {key_code} to HWID {hwid}")
        elif saved_hwid != hwid:
            print(f"[CHECK] HWID mismatch - expected: {saved_hwid}, got: {hwid}")
            return jsonify({"valid": False, "reason": "HWID mismatch. Use /resethwid to reset"}), 200
        
        print(f"[CHECK] Validation successful for key: {key_code}")
        return jsonify({"valid": True, "reason": "success"}), 200
        
    except Exception as e:
        print(f"[CHECK] ERROR: {e}")
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
    print("[DB] Initializing Database...")
    try:
        conn = sqlite3.connect("vanity.db", timeout=10)
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
        
        cursor.execute("SELECT COUNT(*) FROM keys")
        key_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blacklists")
        blacklist_count = cursor.fetchone()[0]
        
        conn.close()
        print(f"[DB] Database ready - {key_count} keys, {blacklist_count} blacklisted users")
    except Exception as e:
        print(f"[DB] ERROR: Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 50)
    print("VANITY API SERVER (SIMPLE MODE)")
    print("=" * 50)
    print("NOTE: Run discord_bot.py separately for Discord functionality")
    print("=" * 50)
    
    init_db()
    
    port = int(os.getenv('PORT', 8080))
    print(f"[API] Server starting on port {port}")
    print(f"[API] Health check: http://0.0.0.0:{port}/")
    print(f"[API] Test endpoint: http://0.0.0.0:{port}/test")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, threaded=True, debug=False)
