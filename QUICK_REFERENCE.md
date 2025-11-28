# 📋 Quick Reference Card

## 🔧 Configuration Needed

```python
# In cogs/application_system.py (lines 11-17)

APPLICATION_ONLY_CHANNEL = 1440569097694744671  # ✅ Already set
APPLICANT_ROLE_ID = YOUR_ROLE_ID_HERE           # ⚠️ Need to set
APPROVED_ROLE_ID = YOUR_ROLE_ID_HERE            # ⚠️ Need to set
REJECTED_ROLE_ID = None                         # Optional
STAFF_REVIEW_CHANNEL = YOUR_CHANNEL_ID_HERE     # ⚠️ Need to set
```

---

## 📝 Commands Cheat Sheet

| Command | Description | Who Can Use |
|---------|-------------|-------------|
| **Apply Button** | Submit application | Everyone |
| `!dashboard` | View statistics | Everyone |
| `/find user:@user` | Find user's application | Staff |
| `/application` | View all applications | Staff |
| `/application status:Pending` | View pending only | Staff |
| `/application person:@user` | View user history | Staff |
| `!setupapply` | Setup apply button | Admin |
| `!apphistory @user` | View user history | Admin |
| `/channelemoji` | Change embed emojis | Admin |

---

## 🎯 Quick Start

1. **Get Role IDs**: Server Settings → Roles → Right-click → Copy ID
2. **Get Channel ID**: Right-click channel → Copy ID
3. **Edit Config**: Open `cogs/application_system.py` → Lines 11-17
4. **Run Bot**: `python main.py`
5. **Done!** Bot auto-creates apply button

---

## 🔄 User Journey

```
User → Click Apply → Fill Form → Submit
  ↓
Score Calculated (0-100)
  ↓
Sent to Staff Review
  ↓
Staff → /application status:Pending → Select User → Accept/Reject
  ↓
User gets Role + DM
```

---

## 📊 Scoring Quick Reference

| Category | Max Points |
|----------|------------|
| Age | 25 |
| Answer Length | 25 |
| Keywords | 30 |
| Grammar | 20 |
| **Total** | **100** |

**Visual Indicators:**
- 🟢 70-100 = Strong
- 🟡 50-69 = Moderate
- 🔴 0-49 = Weak

---

## 🗄️ Database Tables

- `applications` - All application data
- `application_cooldowns` - 7-day cooldown tracking
- `application_messages` - Apply button message ID

---

## 🎨 Features at a Glance

✅ Auto-scoring (0-100 points)
✅ Staff review system
✅ 7-day cooldown
✅ Full history tracking
✅ Beautiful embeds
✅ Channel restrictions
✅ Role management
✅ AI summaries (optional)
✅ Dashboard statistics
✅ Auto-setup on restart
✅ Interactive slash command

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Apply button not working | Check channel ID is correct |
| Roles not assigned | Verify role IDs and bot permissions |
| Message not appearing | Bot will auto-create on startup |
| Cooldown not working | Check database connection |
| Slash command not showing | Restart bot and sync commands |

---

## 📞 Support Files

- `APPLICATION_SYSTEM_README.md` - Full documentation
- `QUICK_SETUP.md` - 5-minute setup
- `SLASH_COMMAND_GUIDE.md` - Command details
- `COMMAND_EXAMPLE.md` - Visual examples
- `FINAL_SUMMARY.md` - Complete summary

---

## 🎉 That's It!

Configure 3 role IDs + 1 channel ID = Ready to go! 🚀
