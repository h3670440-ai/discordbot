from flask import Flask, request
import sqlite3
import os
import threading
import subprocess
import time

app = Flask(__name__)

@app.route('/verify')
def verify():
    key_code = request.args.get('key')
    print(f"DEBUG: Received verification request for key: '{key_code}'")
    
    if not key_code:
        return "invalid"
    
    key_code = key_code.strip()
    
    try:
        # Connect to the same database the bot uses
        conn = sqlite3.connect("vanity.db")
        cursor = conn.cursor()
        
        # Check key existence and redemption status
        cursor.execute("SELECT is_redeemed, redeemed_by FROM keys WHERE key = ?", (key_code,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return "not found"
        
        if row[0] == 0:
            conn.close()
            return "not redeemed"
        
        user_id = row[1]
        
        # Check if the user who redeemed it is blacklisted
        cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            return "blacklisted"
        
        conn.close()
        return "success"
    except Exception as e:
        print(f"API Error: {e}")
        return "error"

def run_bot():
    print("API: Starting Discord Bot...")
    subprocess.run(["python", "bot.py"])

if __name__ == '__main__':
    # Start the bot in a background thread
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Railway provides the PORT environment variable
    port = int(os.getenv('PORT', 8080))
    print(f"API: Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)
