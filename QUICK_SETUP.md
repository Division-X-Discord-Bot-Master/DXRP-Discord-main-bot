# Quick Setup Guide - Application System

## ⚡ 5-Minute Setup

### Step 1: Get Your IDs

**Enable Developer Mode:**
- Discord Settings → Advanced → Developer Mode ✅

**Get Channel IDs:**
1. Right-click your applications channel → Copy ID
2. Right-click your staff review channel → Copy ID

**Get Role IDs:**
1. Server Settings → Roles
2. Right-click each role → Copy ID
   - Applicant role
   - Approved role
   - Rejected role (optional)

### Step 2: Edit Configuration

Open `cogs/application_system.py` and replace these lines (around line 11-16):

```python
APPLICATION_ONLY_CHANNEL = 1234567890123456789  # Replace with your applications channel ID
APPLICANT_ROLE_ID = 1234567890123456789  # Replace with your applicant role ID
APPROVED_ROLE_ID = 1234567890123456789  # Replace with your approved role ID
REJECTED_ROLE_ID = 1234567890123456789  # Replace with your rejected role ID (or None)
STAFF_REVIEW_CHANNEL = 1234567890123456789  # Replace with your staff review channel ID
OPENAI_API_KEY = None  # Optional: Add your OpenAI API key or leave as None
```

### Step 3: Run the Bot

```bash
python main.py
```

### Step 4: Setup Apply Button

1. Go to your applications channel
2. Type: `!setupapply`
3. Done! ✅

---

## 🎯 Test It

1. Click the "Apply Now" button
2. Fill out the form
3. Check your DMs for the result
4. Check staff review channel if score is 40-69

---

## 📋 Commands Cheat Sheet

- `!setupapply` - Setup the apply button (Admin only)
- `!dashboard` - View statistics (Anyone)
- `!apphistory @user` - View user's application history (Staff)

---

## 🎨 How Scoring Works

All applications go to staff review, but the score helps staff make decisions:

- **70+ points** = Strong application (Green) ✅
- **50-69 points** = Moderate application (Orange) ⏳
- **Below 50** = Weak application (Red) ❌

**Score is based on:**
- Age (25 pts)
- Answer length (25 pts)
- Keywords (30 pts)
- Grammar (20 pts)

---

## 🔧 Optional: Enable AI Reviews

1. Get API key from https://platform.openai.com/api-keys
2. Install: `pip install openai`
3. Set in config: `OPENAI_API_KEY = "sk-your-key-here"`

---

## ✅ Checklist

- [ ] Created Applicant role
- [ ] Created Approved role
- [ ] Created Rejected role (optional)
- [ ] Created #applications channel
- [ ] Created #staff-review channel
- [ ] Copied all IDs
- [ ] Updated configuration in `cogs/application_system.py`
- [ ] Bot is running
- [ ] Ran `!setupapply` in applications channel
- [ ] Tested by clicking Apply button

---

## 🎉 You're Done!

Your application system is ready to use!
