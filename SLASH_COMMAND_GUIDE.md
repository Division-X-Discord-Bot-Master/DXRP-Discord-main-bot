# 📋 /application Slash Command Guide

## Overview

The `/application` slash command provides an interactive way to view and manage all applications through a dropdown menu interface.

## 🎯 Command Usage

### Basic Usage
```
/application
```
Shows all applications with a dropdown menu to select and review.

### Filter by Status
```
/application status:Pending
/application status:Accepted
/application status:Rejected
/application status:All
```

### View Specific User
```
/application person:@username
```
Shows all applications from a specific user.

## 🎨 Features

### 1. **Dropdown Selection**
- Lists up to 25 applications in a dropdown menu
- Each option shows:
  - Username
  - Score (out of 100)
  - Status (Pending/Accepted/Rejected)
  - Application date
  - Color indicator (🟢 Green = 70+, 🟡 Yellow = 50-69, 🔴 Red = <50)

### 2. **Detailed View**
When you select an application, you see:
- 👤 Applicant (with mention)
- 🎂 Age
- 📊 Score
- 📌 Status
- 📅 Applied date
- 📝 Full reason for joining
- 🤖 AI Summary
- 👮 Reviewed by (if reviewed)

### 3. **Review Buttons**
For pending applications, you get:
- ✅ **Accept** - Approve the application
- ❌ **Reject** - Reject the application
- 📋 **View History** - See user's full application history

### 4. **Summary Statistics**
Shows quick stats:
- ⏳ Pending count
- ✅ Accepted count
- ❌ Rejected count

## 📊 Examples

### Example 1: Review Pending Applications
```
/application status:Pending
```
1. Shows dropdown with all pending applications
2. Select an applicant
3. Review their details
4. Click Accept or Reject

### Example 2: Check User History
```
/application person:@JohnDoe
```
Shows all applications submitted by JohnDoe.

### Example 3: View All Applications
```
/application status:All
```
Shows every application regardless of status.

## 🎯 Use Cases

### For Staff Review
1. Use `/application status:Pending` to see all pending applications
2. Select an application from the dropdown
3. Review the details and score
4. Make a decision (Accept/Reject)
5. User automatically gets role and DM notification

### For Checking History
1. Use `/application person:@user` to see if someone applied before
2. Check their previous scores and reasons
3. Make informed decisions

### For Statistics
1. Use `/application` to see overall stats
2. Check how many pending applications need review
3. Monitor acceptance/rejection rates

## 🔒 Permissions

- Command is available to staff members
- Only shows in the configured staff review channel: `1440569096809877561`
- Responses are ephemeral (only visible to you)

## 🎨 Visual Indicators

### Score Colors
- 🟢 **Green** (70-100): Strong application
- 🟡 **Yellow** (50-69): Moderate application
- 🔴 **Red** (0-49): Weak application

### Status Emojis
- ⏳ **Pending**: Awaiting review
- ✅ **Accepted**: Approved
- ❌ **Rejected**: Denied

## 💡 Tips

1. **Filter by Pending** - Most efficient way to review new applications
2. **Check History** - Before accepting, check if user applied before
3. **Use Scores** - Higher scores indicate better applications
4. **Read AI Summary** - Quick insight into application quality
5. **Dropdown Limit** - Only shows 25 most recent, use filters for more

## 🔄 Workflow

```
Staff Member
    ↓
/application status:Pending
    ↓
Dropdown appears with pending applications
    ↓
Select an applicant
    ↓
Review details (score, reason, AI summary)
    ↓
Click Accept or Reject
    ↓
User gets role + DM notification
    ↓
Application marked as reviewed
```

## 📝 Notes

- Dropdown has 5-minute timeout
- All responses are ephemeral (private)
- Accept/Reject buttons work instantly
- Database updates automatically
- User receives DM notification
- Roles are assigned/removed automatically

## 🎉 Benefits

1. **Interactive** - Easy dropdown selection
2. **Organized** - Filter by status
3. **Efficient** - Review multiple applications quickly
4. **Informative** - See all details at once
5. **Fast** - One-click accept/reject
6. **Tracked** - All actions logged in database

---

This command makes application management much easier for staff! 🚀
