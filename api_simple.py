"""
Combined API and Discord Bot - Runs both together on Railway
Discord bot runs in main thread, Flask API in background thread
"""
from flask import Flask, request, jsonify
import sqlite3
import os
import datetime
from threading import Thread
import discord
from discord import app_commands
from discord.ext import commands
import random
import string
from datetime import timedelta

app = Flask(__name__)

# Initialize Discord bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class VanityBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.db = None
    
    async def setup_hook(self):
        self.db = sqlite3.connect("vanity.db")
        cursor = self.db.cursor()
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
        self.db.commit()
        await self.tree.sync()
        print(f"✅ Discord bot ready and synced!")

bot = VanityBot()

# Flask routes
@app.route('/')
def health():
    return jsonify({
        "status": "online",
        "service": "Vanity API + Discord Bot",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200

@app.route('/test')
def test():
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
        return jsonify({"status": "error", "message": str(e)}), 200

@app.route('/check', methods=['GET'])
def check():
    conn = None
    try:
        key_code = request.args.get('key')
        hwid = request.args.get('hwid')
        
        print(f"[CHECK] key='{key_code}', hwid='{hwid}'")
        
        if not key_code or not hwid:
            return jsonify({"valid": False, "reason": "Missing key or HWID"}), 200
        
        key_code = key_code.strip()
        hwid = hwid.strip()
        
        conn = sqlite3.connect("vanity.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT is_redeemed, redeemed_by, hwid, expiration FROM keys WHERE key = ?", (key_code,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"valid": False, "reason": "Invalid key"}), 200
        
        is_redeemed, user_id, saved_hwid, expiration = row
        
        if is_redeemed == 0:
            return jsonify({"valid": False, "reason": "Key not redeemed. Please redeem your key first"}), 200
        
        if expiration:
            try:
                exp_dt = datetime.datetime.fromisoformat(expiration)
                if datetime.datetime.now() > exp_dt:
                    return jsonify({"valid": False, "reason": "Key expired"}), 200
            except:
                pass
        
        if user_id:
            cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return jsonify({"valid": False, "reason": "Blacklisted user"}), 200
        
        if not saved_hwid:
            cursor.execute("UPDATE keys SET hwid = ? WHERE key = ?", (hwid, key_code))
            conn.commit()
            print(f"[CHECK] Bound key to HWID")
        elif saved_hwid != hwid:
            return jsonify({"valid": False, "reason": "HWID mismatch"}), 200
        
        return jsonify({"valid": True, "reason": "success"}), 200
        
    except Exception as e:
        print(f"[CHECK] ERROR: {e}")
        return jsonify({"valid": False, "reason": "Server error"}), 200
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

# Discord bot commands
async def check_security(interaction: discord.Interaction):
    owner_name = os.getenv('OWNER_NAME', 'y9pv')
    cursor = bot.db.cursor()
    cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (interaction.user.id,))
    if cursor.fetchone():
        await interaction.response.send_message("❌ You are blacklisted.", ephemeral=True)
        return False
    if interaction.user.name != owner_name:
        await interaction.response.send_message(f"❌ user mismatch (expected {owner_name})", ephemeral=True)
        return False
    has_role = discord.utils.get(interaction.user.roles, name="Owner")
    if not has_role:
        await interaction.response.send_message("❌ role mismatch", ephemeral=True)
        return False
    return True

def generate_key_string():
    return "VANITY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@bot.event
async def on_ready():
    print(f'✅ Bot online as {bot.user}')

class RedeemModal(discord.ui.Modal, title="Redeem Your Key"):
    key_input = discord.ui.TextInput(label="Enter License Key", placeholder="VANITY-XXXX-XXXX-XXXX", min_length=10, max_length=50, required=True)
    
    async def on_submit(self, interaction: discord.Interaction):
        key_code = self.key_input.value
        cursor = bot.db.cursor()
        cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (interaction.user.id,))
        if cursor.fetchone():
            return await interaction.response.send_message("❌ You are blacklisted.", ephemeral=True)
        cursor.execute("SELECT key, is_redeemed, expiration, redeemed_by FROM keys WHERE key = ?", (key_code,))
        row = cursor.fetchone()
        if not row:
            return await interaction.response.send_message("❌ Invalid key.", ephemeral=True)
        if row[1] == 1 and row[3] != interaction.user.id:
            return await interaction.response.send_message("❌ Key already redeemed by another user.", ephemeral=True)
        if row[1] == 1 and row[3] == interaction.user.id:
            return await interaction.response.send_message("✅ You already redeemed this key.", ephemeral=True)
        cursor.execute("UPDATE keys SET is_redeemed = 1, redeemed_by = ? WHERE key = ?", (interaction.user.id, key_code))
        bot.db.commit()
        await interaction.response.send_message("✅ Successfully redeemed key!", ephemeral=True)

class VanityPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Redeem Key", style=discord.ButtonStyle.danger, custom_id="vanity:redeem")
    async def redeem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemModal())
    
    @discord.ui.button(label="Get Key", style=discord.ButtonStyle.secondary, custom_id="vanity:get_key")
    async def get_key_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor = bot.db.cursor()
        cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (interaction.user.id,))
        if cursor.fetchone():
            return await interaction.response.send_message("❌ You are blacklisted.", ephemeral=True)
        cursor.execute("SELECT key FROM keys WHERE redeemed_by = ?", (interaction.user.id,))
        if not cursor.fetchone():
            return await interaction.response.send_message("❌ You need to redeem a key first.", ephemeral=True)
        await interaction.response.send_message(f"```lua\nPrint(\"vanitynotoutyetlmao\")\n```", ephemeral=True)
    
    @discord.ui.button(label="Reset HWID", style=discord.ButtonStyle.secondary, custom_id="vanity:reset_hwid")
    async def reset_hwid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cursor = bot.db.cursor()
        cursor.execute("SELECT user_id FROM blacklists WHERE user_id = ?", (interaction.user.id,))
        if cursor.fetchone():
            return await interaction.response.send_message("❌ You are blacklisted.", ephemeral=True)
        cursor.execute("SELECT key FROM keys WHERE redeemed_by = ?", (interaction.user.id,))
        if not cursor.fetchone():
            return await interaction.response.send_message("❌ You need to redeem a key first.", ephemeral=True)
        await interaction.response.send_message("✅ Your key HWID has been reset.", ephemeral=True)

@bot.tree.command(name="scriptpanel", description="Vanity Script management panel (Owner Only)")
async def scriptpanel(interaction: discord.Interaction):
    if not await check_security(interaction): return
    embed = discord.Embed(
        title="Vanity Script | Control Panel",
        description="Welcome to the Vanity management interface.\n\n**Available Actions:**\n> Redeem Key: Activate your subscription.\n> Get Key: Information on how to obtain access.\n> Reset HWID: Resets ur key hwid.\n\n*Status: System Operational*",
        color=discord.Color.from_rgb(255, 0, 0),
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="Vanity Exploit • Premium Security", icon_url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, view=VanityPanelView())

@bot.tree.command(name="generatescript", description="Generates a Vanity key (Owner Only)")
@app_commands.describe(member="The member to generate a key for", value="Number of units", unit="The unit of time", destination="Where to send the key")
async def generatescript(interaction: discord.Interaction, member: discord.Member, value: int = 1, unit: str = "lifetime", destination: str = "channel"):
    if not await check_security(interaction): return
    new_key = generate_key_string()
    expiration = None
    if unit.lower() != "lifetime":
        now = datetime.datetime.now()
        if unit == "minutes": expiration = now + timedelta(minutes=value)
        elif unit == "hours": expiration = now + timedelta(hours=value)
        elif unit == "weeks": expiration = now + timedelta(weeks=value)
        elif unit == "months": expiration = now + timedelta(days=value*30)
    cursor = bot.db.cursor()
    cursor.execute("INSERT INTO keys (key, duration, expiration, is_redeemed, hwid) VALUES (?, ?, ?, ?, ?)", (new_key, f"{value} {unit}", expiration, 0, None))
    bot.db.commit()
    msg = f"Generated a Vanity key for {member.mention}\nKey: `{new_key}`\nDuration: **{value} {unit}**"
    if destination == "dm":
        try:
            await member.send(msg)
            await interaction.response.send_message(f"✅ Key sent to {member.mention}'s DMs.", ephemeral=True)
        except:
            await interaction.response.send_message(f"❌ Failed to DM. Key: `{new_key}`", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.mention} generated a vanity key for {member.mention}\n`{new_key}`")

@bot.tree.command(name="blacklist", description="Blacklists a user (Owner Only)")
async def blacklist(interaction: discord.Interaction, member: discord.Member):
    if not await check_security(interaction): return
    cursor = bot.db.cursor()
    cursor.execute("INSERT OR IGNORE INTO blacklists (user_id) VALUES (?)", (member.id,))
    cursor.execute("DELETE FROM keys WHERE redeemed_by = ?", (member.id,))
    bot.db.commit()
    await interaction.response.send_message(f"🚫 **{member}** has been blacklisted.")

@bot.tree.command(name="unblacklist", description="Unblacklist a user (Owner Only)")
async def unblacklist(interaction: discord.Interaction, user: discord.Member):
    if not await check_security(interaction): return
    cursor = bot.db.cursor()
    cursor.execute("DELETE FROM blacklists WHERE user_id = ?", (user.id,))
    bot.db.commit()
    await interaction.response.send_message(f"✅ {user.mention} has been unblacklisted.", ephemeral=True)

@bot.tree.command(name="resethwid", description="Reset the HWID bound to a key (Owner Only)")
async def resethwid(interaction: discord.Interaction, key: str):
    if not await check_security(interaction): return
    cursor = bot.db.cursor()
    cursor.execute("SELECT is_redeemed FROM keys WHERE key = ?", (key,))
    if not cursor.fetchone():
        return await interaction.response.send_message("❌ Key not found.", ephemeral=True)
    cursor.execute("UPDATE keys SET hwid = NULL WHERE key = ?", (key,))
    bot.db.commit()
    await interaction.response.send_message(f"✅ HWID for key `{key}` has been reset.", ephemeral=True)

def run_flask():
    """Run Flask API in background thread"""
    port = int(os.getenv('PORT', 8080))
    print(f"[API] Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("=" * 50)
    print("VANITY API + DISCORD BOT")
    print("=" * 50)
    
    # Start Flask in background thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run Discord bot in main thread
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN:
        print("[BOT] Starting Discord bot...")
        bot.run(TOKEN)
    else:
        print("❌ DISCORD_TOKEN not found!")
