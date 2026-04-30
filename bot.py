import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuration
OWNER_ID = 1481473862775472190
PREFIX = "!"

# Setup Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Custom check for Owner ID
def is_vanity_owner():
    async def predicate(ctx):
        if ctx.author.id != OWNER_ID:
            await ctx.send("❌ You are not authorized to use this command.")
            return False
        return True
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'✅ Vanity Bot is online! Logged in as {bot.user}')
    print(f'👑 Authorized Owner ID: {OWNER_ID}')

# --- MODERATION COMMANDS (OWNER ONLY) ---

@bot.command()
@is_vanity_owner()
async def ban(ctx, member: discord.Member, *, reason=None):
    """Bans a member from the server."""
    try:
        await member.ban(reason=reason)
        await ctx.send(f'🔨 **{member}** has been banned. Reason: {reason or "No reason provided."}')
    except Exception as e:
        await ctx.send(f'❌ Failed to ban: {e}')

@bot.command()
@is_vanity_owner()
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kicks a member from the server."""
    try:
        await member.kick(reason=reason)
        await ctx.send(f'👢 **{member}** has been kicked. Reason: {reason or "No reason provided."}')
    except Exception as e:
        await ctx.send(f'❌ Failed to kick: {e}')

@bot.command()
@is_vanity_owner()
async def mute(ctx, member: discord.Member, minutes: int = 60):
    """Mutes a member using timeouts (default 60 mins)."""
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=f"Muted by {ctx.author}")
        await ctx.send(f'🔇 **{member}** has been muted for {minutes} minutes.')
    except Exception as e:
        await ctx.send(f'❌ Failed to mute: {e}')

@bot.command()
@is_vanity_owner()
async def unmute(ctx, member: discord.Member):
    """Removes the timeout from a member."""
    try:
        await member.timeout(None)
        await ctx.send(f'🔊 **{member}** has been unmuted.')
    except Exception as e:
        await ctx.send(f'❌ Failed to unmute: {e}')

# --- PUBLIC COMMANDS (EVERYONE) ---

@bot.command()
async def viewprofile(ctx, member: discord.Member = None):
    """Displays the profile picture of a member."""
    member = member or ctx.author
    
    embed = discord.Embed(
        title=f"👤 Profile: {member.display_name}",
        color=discord.Color.red()
    )
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command()
async def helpme(ctx):
    """Custom help command."""
    embed = discord.Embed(title="🛡️ Vanity Bot Commands", color=discord.Color.red())
    
    # Moderation (Owner only)
    if ctx.author.id == OWNER_ID:
        embed.add_field(name="👑 Owner Commands", value="`!ban`, `!kick`, `!mute`, `!unmute`", inline=False)
    
    # Public
    embed.add_field(name="🌍 Public Commands", value="`!viewprofile`, `!helpme`", inline=False)
    
    await ctx.send(embed=embed)

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ DISCORD_TOKEN not found in .env file. Please add it to start the bot.")
