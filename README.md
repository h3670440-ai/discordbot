# Vanity Bot - GitHub Deployment Files

## 📁 What's in This Folder

This folder contains **ONLY** the files you need to push to GitHub for Railway deployment.

### Files Included:
- ✅ `api_simple.py` - Main API server (Railway runs this)
- ✅ `discord_bot.py` - Discord bot (run locally or separate service)
- ✅ `Procfile` - Tells Railway to run the API
- ✅ `requirements.txt` - Python dependencies
- ✅ `railway.toml` - Railway configuration
- ✅ `.gitignore` - Prevents committing sensitive files
- ✅ `README.md` - This file

## 🚀 Deployment Steps

### 1. Create GitHub Repository
1. Go to https://github.com
2. Click "+" → "New repository"
3. Name it: `vanity-bot` (or whatever you want)
4. **DO NOT** initialize with README
5. Click "Create repository"

### 2. Push These Files to GitHub

Open terminal/PowerShell in the `botstuff` folder and run:

```bash
# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - Vanity bot deployment"

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/vanity-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Deploy to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `vanity-bot` repository
5. Railway will auto-detect the configuration

### 4. Set Environment Variables in Railway

In Railway dashboard:
1. Click your service
2. Go to "Variables" tab
3. Add these three variables:

```
DISCORD_TOKEN = your_discord_bot_token_here
OWNER_NAME = your_discord_username
PORT = 8080
```

### 5. Wait for Deployment

Railway will automatically deploy. Wait 60 seconds.

### 6. Test the API

Open in browser:
```
https://your-project.up.railway.app/
```

Should show:
```json
{
  "status": "online",
  "service": "Vanity API",
  "timestamp": "..."
}
```

✅ **If you see this, the API is working!**

### 7. Run the Discord Bot

The bot needs to run separately from the API.

**Option A: Run Locally (Recommended)**
```bash
# In the botstuff folder
python discord_bot.py
```

Keep this terminal open while using the bot.

**Option B: Deploy as Separate Railway Service**
1. Create a new Railway service
2. Connect to same GitHub repo
3. Change start command to: `python discord_bot.py`
4. Set same environment variables
5. Deploy

## 🎮 Using the System

### 1. Generate a Key (in Discord)
```
/generatescript @YourUsername 1 lifetime channel
```

Copy the key (e.g., `VANITY-ABC123DEF456`)

### 2. Redeem the Key (in Discord)
```
/scriptpanel
```
Click "Redeem Key" → Paste your key → Submit

### 3. Update Your Roblox Config

Edit your `vanityconfig.lua`:
```lua
['Key'] = "VANITY-ABC123DEF456",  -- Your actual key
```

### 4. Load Script in Roblox

Execute the script - it should verify and load!

## ⚠️ Important Notes

### Security
- **NEVER** commit `.env` file (it's in `.gitignore`)
- **NEVER** commit `vanity.db` database (it's in `.gitignore`)
- Use Railway environment variables for secrets
- Keep your Discord bot token private

### Database
- `vanity.db` is created automatically on Railway
- Database persists across deployments
- Both API and bot use the same database

### Bot vs API
- **API** runs on Railway (handles key verification from Roblox)
- **Bot** runs locally or on separate Railway service (manages keys in Discord)
- Both share the same database file

## 🐛 Troubleshooting

### API Not Responding
- Wait 60 seconds after deployment
- Check Railway logs for errors
- Verify environment variables are set
- Test: `curl https://your-project.up.railway.app/`

### Bot Not Working
- Make sure bot is running (`python discord_bot.py`)
- Check `DISCORD_TOKEN` is correct
- Verify you have "Owner" role in Discord
- Your Discord username must match `OWNER_NAME`

### Script Gets Kicked
- Make sure you **redeemed** the key in Discord first
- Check key is correct in `vanityconfig.lua`
- Test key: `curl "https://your-project.up.railway.app/check?key=YOUR_KEY&hwid=test"`

## 📞 Quick Reference

### Railway Environment Variables
```
DISCORD_TOKEN = your_bot_token
OWNER_NAME = your_discord_username
PORT = 8080
```

### Testing Commands
```bash
# Test API health
curl https://your-project.up.railway.app/

# Test database
curl https://your-project.up.railway.app/test

# Test key verification
curl "https://your-project.up.railway.app/check?key=YOUR_KEY&hwid=test"
```

### Discord Commands (Owner Only)
- `/scriptpanel` - Show control panel
- `/generatescript @user [duration]` - Generate a key
- `/blacklist @user` - Blacklist a user
- `/unblacklist @user` - Remove blacklist
- `/resethwid <key>` - Reset HWID for a key

## ✅ Deployment Checklist

Before pushing to GitHub:
- [ ] All 6 files are in the folder
- [ ] `.env` is NOT in the folder (it's ignored)
- [ ] `vanity.db` is NOT in the folder (it's ignored)

After deploying to Railway:
- [ ] Environment variables are set
- [ ] API responds at `/`
- [ ] Database test passes at `/test`
- [ ] Bot is running (locally or separate service)
- [ ] Can generate keys in Discord
- [ ] Can redeem keys in Discord
- [ ] Lua script can verify keys

## 🎉 You're Ready!

These files are all you need. Just push to GitHub and deploy to Railway!
