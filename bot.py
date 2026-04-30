import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class VanityBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        # This syncs the slash commands to Discord
        await self.tree.sync()
        print(f"✅ Slash commands synced!")

bot = VanityBot()

# --- SECURITY CHECK HELPER ---
async def check_security(interaction: discord.Interaction):
    if interaction.user.name != "v9pv":
        await interaction.response.send_message("❌ user mismatch", ephemeral=True)
        return False
    
    has_role = discord.utils.get(interaction.user.roles, name="Owner")
    if not has_role:
        await interaction.response.send_message("❌ role mismatch", ephemeral=True)
        return False
        
    return True

@bot.event
async def on_ready():
    print(f'✅ Vanity Bot is online! Logged in as {bot.user}')

# --- MODERATION SLASH COMMANDS ---

@bot.tree.command(name="ban", description="Bans a member (Owner Only)")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not await check_security(interaction): return
    
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f'🔨 **{member}** has been banned. Reason: {reason}')
    except Exception as e:
        await interaction.response.send_message(f'❌ Failed to ban: {e}', ephemeral=True)

@bot.tree.command(name="kick", description="Kicks a member (Owner Only)")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not await check_security(interaction): return
    
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f'👢 **{member}** has been kicked. Reason: {reason}')
    except Exception as e:
        await interaction.response.send_message(f'❌ Failed to kick: {e}', ephemeral=True)

@bot.tree.command(name="mute", description="Mutes a member for a set duration (Owner Only)")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 60):
    if not await check_security(interaction): return
    
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=f"Muted by {interaction.user}")
        await interaction.response.send_message(f'🔇 **{member}** has been muted for {minutes} minutes.')
    except Exception as e:
        await interaction.response.send_message(f'❌ Failed to mute: {e}', ephemeral=True)

@bot.tree.command(name="unmute", description="Removes the mute from a member (Owner Only)")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not await check_security(interaction): return
    
    try:
        await member.timeout(None)
        await interaction.response.send_message(f'🔊 **{member}** has been unmuted.')
    except Exception as e:
        await interaction.response.send_message(f'❌ Failed to unmute: {e}', ephemeral=True)

# --- PUBLIC SLASH COMMANDS ---

@bot.tree.command(name="viewprofile", description="Shows the profile picture of a member")
async def viewprofile(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    
    embed = discord.Embed(
        title=f"👤 Profile: {member.display_name}",
        color=discord.Color.red()
    )
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ DISCORD_TOKEN not found in variables. Please add it to start the bot.")
