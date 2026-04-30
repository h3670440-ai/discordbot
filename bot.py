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
    owner_name = os.getenv('OWNER_NAME', 'y9pv')
    if interaction.user.name != owner_name:
        await interaction.response.send_message(f"❌ user mismatch (expected {owner_name})", ephemeral=True)
        return False
    
    has_role = discord.utils.get(interaction.user.roles, name="Owner")
    if not has_role:
        await interaction.response.send_message("❌ role mismatch", ephemeral=True)
        return False
        
    return True

@bot.event
async def on_ready():
    print(f'✅ Vanity Bot is online! Logged in as {bot.user}')

# --- UI COMPONENTS FOR SCRIPT PANEL ---

class RedeemModal(discord.ui.Modal, title="Redeem Your Key"):
    key_input = discord.ui.TextInput(
        label="Enter License Key",
        placeholder="VANITY-XXXX-XXXX-XXXX",
        min_length=10,
        max_length=50,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Placeholder for backend verification
        key = self.key_input.value
        await interaction.response.send_message(
            f"⌛ Verifying key: `{key}`...\n❌ Error: Backend not connected. Contact an administrator.",
            ephemeral=True
        )

class VanityPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent view

    @discord.ui.button(label="Redeem Key", style=discord.ButtonStyle.danger, custom_id="vanity:redeem")
    async def redeem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemModal())

    @discord.ui.button(label="Get Key", style=discord.ButtonStyle.secondary, custom_id="vanity:get_key")
    async def get_key_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            f"{interaction.user.mention} Visit this channel: <#1488627841191903283>\n"
            "https://discord.com/channels/1487822538225487892/1488627841191903283"
        )
        await interaction.response.send_message(content, ephemeral=True)

    @discord.ui.button(label="Reset HWID", style=discord.ButtonStyle.secondary, custom_id="vanity:reset_hwid")
    async def reset_hwid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Placeholder for HWID reset logic
        await interaction.response.send_message(
            "Your HWID reset request has been sent to the staff team for approval.",
            ephemeral=True
        )

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

@bot.tree.command(name="scriptpanel", description="Sends the Vanity Script management panel (Owner Only)")
async def scriptpanel(interaction: discord.Interaction):
    if not await check_security(interaction): return

    embed = discord.Embed(
        title="Vanity Script | Control Panel",
        description=(
            "Welcome to the Vanity management interface. Use the buttons below to manage your license and hardware identification.\n\n"
            "**Available Actions:**\n"
            "> Redeem Key: Activate your subscription.\n"
            "> Get Key: Information on how to obtain access.\n"
            "> Reset HWID: Update your hardware ID for a new PC.\n\n"
            "*Status: System Operational*"
        ),
        color=discord.Color.from_rgb(255, 0, 0), # Pure Red
        timestamp=datetime.datetime.now()
    )
    
    # You can add a banner image here if you have one
    # embed.set_image(url="https://your-image-url.com/banner.png")
    embed.set_footer(text="Vanity Exploit • Premium Security", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

    await interaction.response.send_message(embed=embed, view=VanityPanelView())

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("⚠️ DISCORD_TOKEN not found in variables. Please add it to start the bot.")
