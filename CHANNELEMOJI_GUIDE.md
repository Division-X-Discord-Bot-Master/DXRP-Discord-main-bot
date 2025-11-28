# 🎨 /channelemoji Command Guide

## Overview

The `/channelemoji` command allows administrators to customize the emojis used throughout the application system embeds.

## 🎯 Command Usage

```
/channelemoji emoji_type:<type> new_emoji:<emoji>
```

### Example
```
/channelemoji emoji_type:Accepted new_emoji:🎉
```

## 📋 Available Emoji Types

| Type | Current Default | Description |
|------|----------------|-------------|
| **Apply Button** | 📝 | Apply Now button |
| **Applicant** | 👤 | User/applicant field |
| **Age** | 🎂 | Age field |
| **Score** | 📊 | Score field |
| **Reason** | 📝 | Reason for joining field |
| **AI Summary** | 🤖 | AI summary field |
| **Status** | 📌 | Status field |
| **Applied Date** | 📅 | When applied field |
| **Reviewed By** | 👮 | Reviewer field |
| **Reviewed At** | 🕒 | Review timestamp field |
| **Pending** | ⏳ | Pending status emoji |
| **Accepted** | ✅ | Accepted status emoji |
| **Rejected** | ❌ | Rejected status emoji |
| **Cooldown** | ⏰ | Cooldown field |
| **Dashboard** | 📊 | Dashboard title |
| **History** | 📋 | History/requirements field |
| **Warning** | ⚠️ | Warning messages |
| **Error** | ❌ | Error messages |
| **Success** | ✅ | Success messages |
| **Info** | ℹ️ | Info messages |

## 🎨 Examples

### Example 1: Change Accepted Emoji
```
/channelemoji emoji_type:Accepted new_emoji:🎉
```
**Result:** All accepted applications will show 🎉 instead of ✅

### Example 2: Change Applicant Emoji
```
/channelemoji emoji_type:Applicant new_emoji:🧑
```
**Result:** Applicant field will show 🧑 instead of 👤

### Example 3: Change Pending Emoji
```
/channelemoji emoji_type:Pending new_emoji:🔄
```
**Result:** Pending applications will show 🔄 instead of ⏳

### Example 4: Change AI Summary Emoji
```
/channelemoji emoji_type:"AI Summary" new_emoji:🧠
```
**Result:** AI summary field will show 🧠 instead of 🤖

## ✨ Features

### 1. **Instant Update**
- Changes take effect immediately
- No bot restart required
- All new embeds use new emojis

### 2. **Apply Message Update**
- Automatically updates the apply button message
- New emojis appear in the application channel
- Seamless transition

### 3. **Confirmation**
- Shows old emoji vs new emoji
- Confirms the change was successful
- Private response (ephemeral)

### 4. **Persistent**
- Changes persist during bot session
- Note: Resets on bot restart (stored in memory)

## 📊 Visual Example

### Before
```
┌─────────────────────────────────────────┐
│      📋 Application Details             │
├─────────────────────────────────────────┤
│ 👤 Applicant: @JohnDoe                  │
│ 🎂 Age: 22                              │
│ 📊 Score: 85/100                        │
│ 📌 Status: ✅ ACCEPTED                  │
└─────────────────────────────────────────┘
```

### After `/channelemoji emoji_type:Accepted new_emoji:🎉`
```
┌─────────────────────────────────────────┐
│      📋 Application Details             │
├─────────────────────────────────────────┤
│ 👤 Applicant: @JohnDoe                  │
│ 🎂 Age: 22                              │
│ 📊 Score: 85/100                        │
│ 📌 Status: 🎉 ACCEPTED                  │
└─────────────────────────────────────────┘
```

## 🎯 Use Cases

### Use Case 1: Server Branding
Customize emojis to match your server's theme and branding.

### Use Case 2: Custom Server Emojis
Use your server's custom emojis instead of default ones.

### Use Case 3: Accessibility
Change emojis to more recognizable ones for your community.

### Use Case 4: Fun Themes
Create seasonal themes (🎃 for Halloween, 🎄 for Christmas, etc.)

## 💡 Pro Tips

### Tip 1: Use Custom Emojis
You can use your server's custom emojis:
```
/channelemoji emoji_type:Accepted new_emoji:<:custom_check:123456789>
```

### Tip 2: Unicode Emojis
Any Unicode emoji works:
```
/channelemoji emoji_type:Pending new_emoji:⌛
```

### Tip 3: Multiple Changes
Change multiple emojis to create a cohesive theme:
```
/channelemoji emoji_type:Accepted new_emoji:🎉
/channelemoji emoji_type:Rejected new_emoji:😢
/channelemoji emoji_type:Pending new_emoji:🔄
```

### Tip 4: Test First
Changes are immediate, so test with less important emojis first!

### Tip 5: Document Changes
Keep track of your custom emojis in case you need to reset them.

## ⚠️ Important Notes

### 1. **Memory Storage**
- Emoji changes are stored in memory (RAM)
- Changes reset when bot restarts
- To make permanent, edit the EMOJIS dictionary in code

### 2. **Permissions Required**
- Requires Administrator permission
- Only admins can change emojis

### 3. **Immediate Effect**
- Changes apply to all new embeds immediately
- Existing messages are not retroactively updated
- Apply button message IS updated automatically

### 4. **Custom Emoji Format**
For custom server emojis, use format: `<:emoji_name:emoji_id>`

## 🔄 Resetting to Defaults

To reset an emoji to default, use the original emoji:

```
/channelemoji emoji_type:Accepted new_emoji:✅
/channelemoji emoji_type:Rejected new_emoji:❌
/channelemoji emoji_type:Pending new_emoji:⏳
```

## 📋 Default Emoji List

For reference, here are all the defaults:

```python
"apply": "📝"
"applicant": "👤"
"age": "🎂"
"score": "📊"
"reason": "📝"
"ai": "🤖"
"status": "📌"
"applied": "📅"
"reviewed_by": "👮"
"reviewed_at": "🕒"
"pending": "⏳"
"accepted": "✅"
"rejected": "❌"
"cooldown": "⏰"
"dashboard": "📊"
"history": "📋"
"warning": "⚠️"
"error": "❌"
"success": "✅"
"info": "ℹ️"
```

## 🎨 Theme Ideas

### Professional Theme
```
Accepted: ✔️
Rejected: ✖️
Pending: ⏸️
```

### Fun Theme
```
Accepted: 🎉
Rejected: 😢
Pending: 🤔
```

### Gaming Theme
```
Accepted: 🏆
Rejected: 💀
Pending: 🎮
```

### Nature Theme
```
Accepted: 🌟
Rejected: 🍂
Pending: 🌱
```

## 🚀 Quick Start

1. **Choose emoji type** from the dropdown
2. **Enter new emoji** (Unicode or custom)
3. **Submit** and see confirmation
4. **Check** the apply button message for updates

## ✅ Summary

The `/channelemoji` command gives you full control over the visual appearance of your application system. Customize it to match your server's personality!

**Command Format:**
```
/channelemoji emoji_type:<type> new_emoji:<emoji>
```

**Permissions:** Administrator only

**Effect:** Immediate (for new embeds)

**Persistence:** Until bot restart (memory-based)

---

Make your application system uniquely yours! 🎨
