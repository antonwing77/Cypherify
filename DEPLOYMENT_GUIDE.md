# Render Deployment Guide for Cypherify

## Prerequisites

1. ✅ GitHub account
2. ✅ Render account (free): https://render.com
3. ✅ OpenAI API key (optional, for AI features): https://platform.openai.com

---

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)

```bash
cd c:\Users\anton\OneDrive\Desktop\Cypherify
git init
git add .
git commit -m "Initial commit - Cypherify educational tool"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Name: `Cypherify`
3. Description: "Educational Cryptography Tool"
4. Make it **Public** (required for free Render tier)
5. Click "Create repository"

### 1.3 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/Cypherify.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Render

### 2.1 Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub

### 2.2 Create New Web Service

1. Click "New +" button (top right)
2. Select "Web Service"
3. Click "Connect a repository"
4. Select your `Cypherify` repository
5. Click "Connect"

### 2.3 Configure Service Settings

Fill in the following:

**Basic Settings:**
- **Name**: `cypherify` (or any name you prefer)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave blank

**Build Settings:**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```
  gunicorn app:server --bind 0.0.0.0:$PORT
  ```

**Instance Type:**
- Select **Free** (for testing)
- Or **Starter** ($7/month) for always-on service

### 2.4 Environment Variables (Optional)

Click "Advanced" → "Add Environment Variable":

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-...` (your OpenAI API key) |

**Note**: AI Teacher won't work without this, but all ciphers will function normally.

### 2.5 Deploy

1. Click "Create Web Service"
2. Wait 3-5 minutes for build
3. Watch the logs for any errors
4. Once deployed, click the URL (e.g., `https://cypherify.onrender.com`)

---

## Step 3: Test Your Deployment

1. **Visit your URL**: `https://your-app-name.onrender.com`
2. **Test a cipher**: Try Caesar cipher with "Hello World"
3. **Test AI Teacher**: Ask a question (if API key configured)
4. **Test Auto-Detect**: Try decrypting "Khoor Zruog"

---

## Troubleshooting

### Issue: Build Failed

**Check**:
- `requirements.txt` is in root directory
- All dependencies are listed
- Python version is correct

**Solution**:
```bash
# Test locally first
pip install -r requirements.txt
python app.py
```

### Issue: App Crashes on Start

**Check Logs**:
- Go to Render dashboard → Your service → Logs
- Look for error messages

**Common Fixes**:
- Make sure `server = app.server` is in `app.py`
- Verify `gunicorn` is in `requirements.txt`

### Issue: AI Teacher Not Working

**Check**:
- `OPENAI_API_KEY` is set in environment variables
- API key is valid and has credits
- Key starts with `sk-`

### Issue: Free Tier Sleeps

**Behavior**: Free tier sleeps after 15 minutes of inactivity

**Solutions**:
1. **Upgrade to Starter** ($7/month) for always-on
2. **Accept 30-second wake time** on first visit
3. **Use UptimeRobot** to ping every 14 minutes (keeps it awake)

---

## Updating Your Deployment

### Method 1: Git Push (Automatic)

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push

# Render auto-deploys on push!
```

### Method 2: Manual Deploy

1. Go to Render dashboard
2. Click your service
3. Click "Manual Deploy" → "Deploy latest commit"

---

## Performance Tips

### Speed Up Cold Starts

Add to `app.py`:
```python
import os
if os.environ.get('RENDER'):
    # Render-specific optimizations
    app.config.suppress_callback_exceptions = True
```

### Reduce Memory Usage

In `app.py`:
```python
# Limit AI conversation history
if len(conv_history) > 5:  # Was 10
    conv_history = conv_history[-5:]
```

### Add Caching

Install:
```bash
pip install flask-caching
```

Add to `requirements.txt`:
```
flask-caching==2.1.0
```

---

## Cost Breakdown

| Tier | Cost | Features |
|------|------|----------|
| **Free** | $0/month | Sleeps after 15 min, 750 hours/month |
| **Starter** | $7/month | Always-on, 1GB RAM, faster |
| **Standard** | $25/month | 2GB RAM, better performance |

**Recommendation**: Start with **Free**, upgrade to **Starter** if you need 24/7 availability.

---

## Custom Domain (Optional)

1. Buy domain from Namecheap, Google Domains, etc.
2. In Render dashboard → Settings → Custom Domain
3. Add your domain (e.g., `cypherify.com`)
4. Update DNS records as shown
5. SSL certificate auto-generated

---

## Monitoring

### Check Service Health

- **Dashboard**: https://dashboard.render.com
- **Logs**: Real-time in dashboard
- **Metrics**: CPU, Memory, Request count

### Set Up Alerts

1. Dashboard → Your service → Settings
2. Scroll to "Alerts"
3. Add email for deploy failures

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **GitHub Issues**: Create issue in your repository

---

## Success! 🎉

Your Cypherify app should now be live at:
```
https://your-app-name.onrender.com
```

Share it with friends, add it to your portfolio, and keep learning cryptography!
