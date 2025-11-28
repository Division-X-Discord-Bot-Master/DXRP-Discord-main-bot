# 📊 Command Comparison Guide

## All Application Commands at a Glance

### 🔍 `/find user:@username`
**Purpose:** Quick lookup of specific user's most recent application

**Best For:**
- ✅ User just told you they applied
- ✅ Quick status checks
- ✅ Immediate reviews
- ✅ Verifying if someone applied

**Shows:**
- Most recent application only
- Full details with score and AI summary
- Accept/Reject buttons if pending
- Reviewer info if already reviewed

**Example:**
```
/find user:@JohnDoe
→ Shows JohnDoe's latest application
→ Can accept/reject immediately
```

---

### 📋 `/application`
**Purpose:** Browse and manage all applications

**Best For:**
- ✅ Reviewing multiple applications
- ✅ Seeing all pending applications
- ✅ Filtering by status
- ✅ Review sessions

**Shows:**
- Dropdown with up to 25 applications
- Summary statistics
- Filter options

**Example:**
```
/application status:Pending
→ Shows dropdown with all pending
→ Select one to review
```

---

### 👤 `/application person:@username`
**Purpose:** View complete application history for a user

**Best For:**
- ✅ Checking if user applied before
- ✅ Seeing all past applications
- ✅ Reviewing application patterns
- ✅ Checking previous scores

**Shows:**
- All applications from that user
- Up to 10 most recent
- Scores, statuses, dates

**Example:**
```
/application person:@JohnDoe
→ Shows all of JohnDoe's applications
→ See if they applied multiple times
```

---

### 📊 `!dashboard`
**Purpose:** View overall statistics

**Best For:**
- ✅ Checking total applications
- ✅ Seeing acceptance rates
- ✅ Monitoring average scores
- ✅ Quick overview

**Shows:**
- Total applications
- Accepted/Rejected/Pending counts
- Average score
- Acceptance rate

**Example:**
```
!dashboard
→ Shows statistics embed
→ See overall performance
```

---

### 🔧 `!setupapply`
**Purpose:** Manually create apply button

**Best For:**
- ✅ Recreating apply message
- ✅ Moving apply button
- ✅ Fixing broken button

**Shows:**
- Creates new apply button message
- Deletes old one if exists

**Example:**
```
!setupapply
→ Creates apply button in current channel
→ Updates database
```

---

### 📜 `!apphistory @username`
**Purpose:** View user's application history (prefix command version)

**Best For:**
- ✅ Same as `/application person:@user`
- ✅ For those who prefer prefix commands

**Shows:**
- Same as `/application person:@user`

**Example:**
```
!apphistory @JohnDoe
→ Shows all applications
```

---

## 🎯 Quick Decision Tree

### "I need to review a specific user"
→ Use `/find user:@username`

### "I need to review all pending applications"
→ Use `/application status:Pending`

### "I need to check if someone applied before"
→ Use `/application person:@username`

### "I need to see overall statistics"
→ Use `!dashboard`

### "I need to fix the apply button"
→ Use `!setupapply`

---

## 📊 Feature Comparison Table

| Feature | `/find` | `/application` | `/application person:@user` | `!dashboard` |
|---------|---------|----------------|----------------------------|--------------|
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡⚡ |
| **Shows Single User** | ✅ Most Recent | ❌ | ✅ All History | ❌ |
| **Shows Multiple Users** | ❌ | ✅ Dropdown | ❌ | ❌ |
| **Filter by Status** | ❌ | ✅ | ❌ | ❌ |
| **Accept/Reject Buttons** | ✅ If Pending | ✅ If Pending | ❌ View Only | ❌ |
| **Statistics** | ❌ | ✅ Summary | ❌ | ✅ Full Stats |
| **Best For** | Quick Lookup | Bulk Review | History Check | Overview |

---

## 🔄 Workflow Examples

### Workflow 1: User Just Applied
```
User: "I just applied!"
↓
Staff: /find user:@User
↓
Review application
↓
Click Accept or Reject
↓
Done! ✅
```
**Time:** ~30 seconds

---

### Workflow 2: Review Session
```
Staff: Time to review applications
↓
Staff: /application status:Pending
↓
See dropdown with 10 pending
↓
Select first one
↓
Review and decide
↓
Repeat for each
↓
Done! ✅
```
**Time:** ~5 minutes for 10 applications

---

### Workflow 3: Check User History
```
User: "I applied before, why was I rejected?"
↓
Staff: /application person:@User
↓
See all 3 past applications
↓
Check scores and reasons
↓
Explain to user
↓
Done! ✅
```
**Time:** ~1 minute

---

### Workflow 4: Daily Statistics
```
Staff: Let's check today's stats
↓
Staff: !dashboard
↓
See total, accepted, rejected, pending
↓
Check acceptance rate
↓
Done! ✅
```
**Time:** ~10 seconds

---

## 💡 Pro Tips

### Tip 1: Combine Commands
- Use `/find` for quick lookups
- Use `/application` for bulk reviews
- Use both in same session!

### Tip 2: Keyboard Shortcuts
- Type `/f` and Discord will suggest `/find`
- Type `/a` and Discord will suggest `/application`

### Tip 3: Ephemeral Responses
- All responses are private (ephemeral)
- Only you can see them
- No channel spam!

### Tip 4: Multiple Staff
- Multiple staff can review simultaneously
- Each sees their own responses
- No conflicts!

### Tip 5: Mobile Friendly
- All commands work on mobile
- Dropdowns work perfectly
- Buttons are touch-friendly

---

## 🎨 Visual Comparison

### `/find` - Direct Access
```
Command → Application Details → Accept/Reject
```
**Steps:** 2

### `/application` - Browse and Select
```
Command → Dropdown → Select → Application Details → Accept/Reject
```
**Steps:** 4

### Result
`/find` is **2x faster** for specific users! ⚡

---

## 📋 Command Cheat Sheet

```
Quick Lookup:        /find user:@username
Browse All:          /application
Filter Pending:      /application status:Pending
User History:        /application person:@username
Statistics:          !dashboard
Setup Button:        !setupapply
```

---

## 🎉 Summary

| Need | Command | Speed |
|------|---------|-------|
| Review specific user | `/find user:@user` | ⚡⚡⚡ |
| Review multiple apps | `/application status:Pending` | ⚡⚡ |
| Check user history | `/application person:@user` | ⚡⚡ |
| View statistics | `!dashboard` | ⚡⚡⚡ |

**All commands work together to provide a complete application management system!** 🚀
