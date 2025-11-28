# Discord Application System - Complete Guide

## 🎯 Features

### ✅ Implemented Features

1. **Auto-Scoring System**
   - Scores based on age (25 points max)
   - Answer length scoring (25 points max)
   - Keyword detection (30 points max)
   - Grammar and effort (20 points max)
   - Score helps staff make informed decisions
   - All applications go to staff review (no auto-accept/reject)

2. **Applicants Dashboard**
   - Command: `!dashboard`
   - Shows total applications, accepted, rejected, pending
   - Displays average score and acceptance rate

3. **AI Review System**
   - Uses OpenAI API if key is provided
   - Falls back to heuristic summaries if no API key
   - Provides quality assessment for each application

4. **Cooldown System**
   - 7-day cooldown between applications
   - Beautiful embed showing time remaining
   - Prevents spam applications

5. **Card-Style Application Embeds**
   - Beautiful color-coded embeds
   - Shows: App ID, Name, Age, Reason, Score, AI Summary, Status
   - Different colors based on score (green/orange/red)

6. **Full Application History**
   - Stores all applications in SQLite database
   - Admin command: `!apphistory @user`
   - Shows last 10 applications with scores and status

7. **Channel Restriction**
   - Applications only work in designated channel
   - Configurable via `APPLICATION_ONLY_CHANNEL`
   - Denies applications from other channels

8. **Staff Review System**
   - Accept button (gives approved role, removes applicant role)
   - Reject button (optional reject role)
   - View History button
   - All actions logged and notified
   - Shows who reviewed and when for accepted/rejected applications

9. **Role Management**
   - APPLICANT_ROLE_ID - Given when applying
   - APPROVED_ROLE_ID - Given when accepted
   - REJECTED_ROLE_ID - Optional reject role

10. **Full Embed System**
    - All messages are embedded
    - DM notifications for applicants
    - Staff notifications
    - Cooldown warnings
    - Status updates

11. **Acceptance Announcements**
    - Automatic announcement when application is accepted
    - Custom welcome image generated
    - Posted to announcement channel (1440569097694744673)
    - Welcomes new member to the community

---

## 🔧 Setup Instructions

### Step 1: Configure IDs

Open `cogs/application_system.py` and fill in these configuration values at the top:

```python
# ==================== CONFIGURATION ====================
APPLICATION_ONLY_CHANNEL = 1234567890123456789  # Channel where applications are allowed
APPLICANT_ROLE_ID = 1234567890123456789  # Role given when someone applies
APPROVED_ROLE_ID = 1234567890123456789  # Role given when approved
REJECTED_ROLE_ID = 1234567890123456789  # Optional: Role given when rejected (set to None if not used)
STAFF_REVIEW_CHANNEL = 1234567890123456789  # Channel where staff reviews applications
OPENAI_API_KEY = None  # Optional: Set your OpenAI API key for AI reviews, or leave None

# Cooldown settings
COOLDOWN_DAYS = 7
```

### Step 2: Get Channel and Role IDs

**To get Channel IDs:**
1. Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)
2. Right-click on a channel → Copy ID

**To get Role IDs:**
1. Go to Server Settings → Roles
2. Right-click on a role → Copy ID

### Step 3: Create Required Roles

Create these roles in your Discord server:
- **Applicant** - Given to users when they submit an application
- **Approved** - Given to users when their application is accepted
- **Rejected** (Optional) - Given to users when their application is rejected

### Step 4: Create Required Channels

Create these channels:
- **#applications** - Where users submit applications
- **#staff-review** - Where staff reviews pending applications (staff-only)

### Step 5: Run the Bot

1. Run the bot
2. The bot will **automatically** create the apply button in your configured channel!
3. Check the console for confirmation: `✅ Created new apply message in applications`

**Optional Manual Setup:**
- If you want to recreate the message, go to your applications channel
3. Type: `!setupapply`
4. The bot will post an embed with an "Apply Now" button

---

## 📝 Commands

### User Commands

- **Apply Button** - Click the "📝 Apply Now" button in the applications channel
- **!dashboard** - View application statistics (anyone can use)

### Staff Commands

- **/find user:@user** - Quickly find and review a specific user's most recent application
  - Shows application with accept/reject buttons if pending
  - Shows reviewer info if already reviewed
  
- **/application** - Interactive dropdown to view and manage all applications
  - `/application` - View all applications
  - `/application status:Pending` - View only pending applications
  - `/application status:Accepted` - View accepted applications
  - `/application status:Rejected` - View rejected applications
  - `/application person:@user` - View specific user's full application history

### Admin Commands

- **!setupapply** - Setup the apply button in the current channel (Administrator only)
- **!apphistory @user** - View full application history for a user (Manage Server permission)
- **/channelemoji emoji_type:<type> new_emoji:<emoji>** - Change emojis used in application embeds (Administrator only)

### Staff Review Buttons

When an application is pending review, staff will see these buttons:
- **✅ Accept** - Accept the application
- **❌ Reject** - Reject the application
- **📋 View History** - View the user's application history

---

## 🎨 How It Works

### Application Flow

1. **User clicks "Apply Now" button**
   - System checks if they're in the correct channel
   - System checks cooldown (7 days)
   - If passed, shows application modal

2. **User fills out application form**
   - Name (required)
   - Age (required, 1-120)
   - Reason for joining (required, up to 1000 characters)

3. **System scores the application**
   - Age scoring (16-25 = best score)
   - Length scoring (200+ chars = best score)
   - Keyword detection (community, friends, help, etc.)
   - Grammar check (proper sentences, capitalization)

4. **All applications sent to staff review**
   - Applicant role added
   - DM sent to user (pending status)
   - Sent to staff review channel with score and AI summary
   - Staff can accept/reject manually using buttons
   - Score helps staff make informed decisions

5. **Cooldown applied**
   - User cannot apply again for 7 days
   - Beautiful embed shows time remaining if they try

---

## 🤖 AI Review (Optional)

### With OpenAI API

If you provide an OpenAI API key, the system will use GPT-3.5-turbo to generate intelligent summaries of applications.

**To enable:**
1. Get an API key from https://platform.openai.com/api-keys
2. Set it in the configuration:
```python
OPENAI_API_KEY = "sk-your-api-key-here"
```
3. Install the OpenAI library:
```bash
pip install openai
```

### Without API Key (Default)

The system uses heuristic-based summaries:
- Score ≥ 70: "Strong application with detailed reasoning... Recommended for approval."
- Score ≥ 50: "Moderate application. Shows interest... Review carefully."
- Score < 50: "Basic application. Lacks detail... Consider requesting more information."

---

## 📊 Scoring System Breakdown

### Age Scoring (Max 25 points)
- Ages 16-25: 25 points
- Ages 13-30: 20 points
- Ages 30+: 15 points
- Other ages: 5 points

### Answer Length (Max 25 points)
- 200+ characters: 25 points
- 100-199 characters: 20 points
- 50-99 characters: 15 points
- Less than 50: 10 points

### Keywords (Max 30 points)
Positive keywords detected (5 points each, max 30):
- community, friends, learn, help, contribute
- active, participate, enjoy, passion, interested
- love, excited, experience, grow, support
- collaborate, share

### Grammar & Effort (Max 20 points)
- 3+ sentences: 10 points
- Starts with capital letter: 5 points
- No excessive caps: 5 points

**Total: 100 points possible**

---

## 🗄️ Database Structure

### Applications Table
```sql
- app_id (PRIMARY KEY)
- user_id
- username
- age
- reason
- score
- ai_summary
- status (pending/accepted/rejected)
- applied_at
- reviewed_by
- reviewed_at
```

### Cooldowns Table
```sql
- user_id (PRIMARY KEY)
- last_application
```

---

## 🎨 Embed Colors

- **Green** - High score applications (score ≥ 70)
- **Orange** - Medium score applications (score 50-69)
- **Red** - Low score applications (score < 50)
- **Blue** - Information messages

Note: All applications go to staff review regardless of score. Colors are just visual indicators to help staff prioritize.

---

## 🔒 Permissions Required

### Bot Permissions
- Manage Roles
- Send Messages
- Embed Links
- Read Message History
- Use External Emojis

### User Permissions
- **!dashboard**: None (everyone)
- **!setupapply**: Administrator
- **!apphistory**: Manage Server

---

## 🐛 Troubleshooting

### "Applications can only be submitted in #channel"
- Make sure you're in the correct channel
- Verify `APPLICATION_ONLY_CHANNEL` is set correctly

### "Application Cooldown" message
- User must wait 7 days between applications
- Check database to clear cooldown if needed

### Roles not being assigned
- Verify role IDs are correct
- Make sure bot's role is higher than the roles it's trying to assign
- Check bot has "Manage Roles" permission

### Apply button not working
- Make sure the bot is running
- Verify persistent views are loaded
- Try running `!setupapply` again

### AI summaries not working
- Check if OpenAI API key is valid
- Verify `openai` library is installed
- System will fall back to heuristics if AI fails

---

## 📈 Customization

### Change Cooldown Period
```python
COOLDOWN_DAYS = 14  # Change to 14 days
```

### Add More Keywords
Edit the `positive_keywords` list in the `calculate_score` method:
```python
positive_keywords = [
    'community', 'friends', 'learn',
    'your', 'custom', 'keywords'
]
```

### Disable Rejected Role
```python
REJECTED_ROLE_ID = None  # Don't assign a role to rejected users
```

---

## 📞 Support

If you encounter any issues:
1. Check the configuration values are correct
2. Verify bot permissions
3. Check console for error messages
4. Ensure all required roles and channels exist

---

## ✨ Example Usage

### User Experience
1. User goes to #applications channel
2. Sees beautiful embed with "Apply Now" button
3. Clicks button → Modal appears
4. Fills out: Name, Age, Reason
5. Submits → Gets instant feedback
6. Receives DM with result
7. If accepted: Gets approved role automatically

### Staff Experience
1. Application appears in #staff-review
2. Beautiful card shows all details + score + AI summary
3. Three buttons: Accept, Reject, View History
4. Click Accept → User gets role, DM sent automatically
5. All actions logged and tracked

---

## 🎉 That's It!

Your application system is now fully functional with:
- ✅ Auto-scoring and decisions
- ✅ Staff review system
- ✅ Cooldown protection
- ✅ Full history tracking
- ✅ Beautiful embeds everywhere
- ✅ Channel restrictions
- ✅ Role management
- ✅ AI summaries (optional)
- ✅ Dashboard statistics

Enjoy your automated application system! 🚀
