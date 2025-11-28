# 🔍 /find Command Guide

## Overview

The `/find` command allows staff to quickly search for a specific user's most recent application and review it immediately.

## 🎯 Command Usage

```
/find user:@username
```

### Example
```
/find user:@JohnDoe
```

## ✨ Features

### 1. **Quick Search**
- Instantly finds a user's most recent application
- No need to browse through dropdown lists
- Direct access to review

### 2. **Smart Display**
- Shows full application details
- If **pending**: Shows Accept, Reject, View History buttons
- If **accepted/rejected**: Shows reviewer info and View History button

### 3. **No Applications Handling**
- If user hasn't applied, shows clear error message
- Helps verify if someone has applied before

## 📊 Use Cases

### Use Case 1: Quick Review
```
User: "Hey, I just applied!"
Staff: /find user:@User
→ Instantly see their application and review it
```

### Use Case 2: Check Application Status
```
User: "Did you review my application?"
Staff: /find user:@User
→ See if it's pending, accepted, or rejected
→ See who reviewed it and when
```

### Use Case 3: Verify Application
```
User: "I can't apply again"
Staff: /find user:@User
→ Check if they already have an application
→ See when they applied (for cooldown check)
```

### Use Case 4: Re-review
```
Staff: "Let me check that user's application again"
Staff: /find user:@User
→ Review their details
→ Check score and AI summary
```

## 🎨 Visual Examples

### Example 1: Finding a Pending Application

**Command:**
```
/find user:@JohnDoe
```

**Result:**
```
┌─────────────────────────────────────────┐
│      📋 Application Details             │
│      Application ID: 123                │
├─────────────────────────────────────────┤
│ 👤 Applicant: @JohnDoe                  │
│ 🎂 Age: 22                              │
│ 📊 Score: 85/100                        │
│ 📌 Status: ⏳ PENDING                   │
│ 📅 Applied: 2 hours ago                 │
│                                         │
│ 📝 Reason for Joining:                  │
│ I've been looking for an active         │
│ community to join...                    │
│                                         │
│ 🤖 AI Summary:                          │
│ Strong application with detailed        │
│ reasoning. Recommended for approval.    │
└─────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────────┐
│ ✅ Accept│ │ ❌ Reject│ │ 📋 View History│
└──────────┘ └──────────┘ └──────────────┘
```

**Action:** Staff can immediately accept or reject!

---

### Example 2: Finding an Accepted Application

**Command:**
```
/find user:@JaneSmith
```

**Result:**
```
┌─────────────────────────────────────────┐
│      📋 Application Details             │
│      Application ID: 98                 │
├─────────────────────────────────────────┤
│ 👤 Applicant: @JaneSmith                │
│ 🎂 Age: 20                              │
│ 📊 Score: 92/100                        │
│ 📌 Status: ✅ ACCEPTED                  │
│ 📅 Applied: 3 days ago                  │
│ 👮 Reviewed By: @StaffMember            │
│ 🕒 Reviewed At: 2 days ago              │
│                                         │
│ 📝 Reason for Joining:                  │
│ I'm passionate about this community...  │
│                                         │
│ 🤖 AI Summary:                          │
│ Excellent application. Highly engaged.  │
└─────────────────────────────────────────┘

┌──────────────────────┐
│ 📋 View User History │
└──────────────────────┘
```

**Info:** Shows who accepted and when. No accept/reject buttons (already reviewed).

---

### Example 3: User Has No Applications

**Command:**
```
/find user:@NewUser
```

**Result:**
```
┌─────────────────────────────────────────┐
│      ❌ No Applications Found           │
├─────────────────────────────────────────┤
│ @NewUser has not submitted any          │
│ applications.                           │
└─────────────────────────────────────────┘
```

**Info:** User hasn't applied yet.

---

## 🔄 Workflow Comparison

### Old Way (Using /application)
```
1. Type: /application status:Pending
2. See dropdown with all pending applications
3. Scroll through list to find user
4. Select user
5. Review application
```

### New Way (Using /find)
```
1. Type: /find user:@User
2. Instantly see their application
3. Review and decide
```

**Result:** Much faster for specific user lookups! ⚡

---

## 💡 Pro Tips

### Tip 1: Quick Response
When a user says "I just applied", use `/find` to instantly review their application.

### Tip 2: Status Check
Use `/find` to quickly check if someone's application was already reviewed.

### Tip 3: Cooldown Verification
If user says they can't apply, use `/find` to see when they last applied.

### Tip 4: Multiple Applications
`/find` shows the **most recent** application. Use "View History" button to see older ones.

### Tip 5: Combine Commands
- Use `/find` for specific users
- Use `/application` for browsing all pending applications

---

## 📋 Command Comparison

| Command | Best For | Shows |
|---------|----------|-------|
| `/find user:@User` | Specific user lookup | Most recent application |
| `/application` | Browse all applications | Dropdown list |
| `/application status:Pending` | Review queue | All pending apps |
| `/application person:@User` | Full user history | All applications |

---

## 🎯 When to Use Each Command

### Use `/find` when:
- ✅ User just told you they applied
- ✅ You need to check a specific user quickly
- ✅ User asks about their application status
- ✅ You want to verify if someone applied

### Use `/application` when:
- ✅ You want to review multiple applications
- ✅ You need to see all pending applications
- ✅ You want to filter by status
- ✅ You're doing a review session

### Use `/application person:@User` when:
- ✅ You need to see ALL of a user's applications
- ✅ You want to check their application history
- ✅ You need to see patterns in their applications

---

## 🚀 Benefits

1. **Speed** - Instant access to specific user's application
2. **Efficiency** - No scrolling through dropdowns
3. **Convenience** - Direct command for common task
4. **User-Friendly** - Easy to remember and use
5. **Flexible** - Works with pending and reviewed applications

---

## 📝 Technical Details

### What It Does
1. Searches database for user's applications
2. Gets most recent application (sorted by date)
3. Displays full application details
4. Shows appropriate buttons based on status

### Permissions
- Available to staff members
- Responses are ephemeral (only visible to you)

### Edge Cases
- If user has no applications: Shows error message
- If user has multiple applications: Shows most recent
- If application is pending: Shows accept/reject buttons
- If application is reviewed: Shows reviewer info

---

## 🎉 Example Scenarios

### Scenario 1: User Pings Staff
```
User: "@Staff I just applied! Can you review it?"
Staff: /find user:@User
→ Reviews application
→ Clicks Accept
→ User gets role immediately
```

### Scenario 2: Checking Status
```
User: "Did anyone review my application yet?"
Staff: /find user:@User
→ Sees it's still pending
Staff: "Still pending, we'll review it soon!"
```

### Scenario 3: Already Reviewed
```
User: "Can you check my application?"
Staff: /find user:@User
→ Sees it was accepted 2 days ago by @OtherStaff
Staff: "You were already accepted 2 days ago!"
```

### Scenario 4: Cooldown Check
```
User: "Why can't I apply again?"
Staff: /find user:@User
→ Sees they applied 3 days ago
Staff: "You need to wait 4 more days (7-day cooldown)"
```

---

## ✨ Summary

The `/find` command is perfect for:
- 🔍 Quick user lookups
- ⚡ Fast reviews
- 📊 Status checks
- 🎯 Targeted actions

Use it whenever you need to check a specific user's application quickly!

---

**Quick Reference:**
```
/find user:@username
```
That's it! Simple and powerful. 🚀
