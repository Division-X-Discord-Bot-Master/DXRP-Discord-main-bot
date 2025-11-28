# 📊 Application System Flow Diagram

## 🔄 Complete Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CLICKS "APPLY NOW"                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Check Channel  │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
         ┌──────────┐              ┌──────────┐
         │ Correct  │              │  Wrong   │
         │ Channel  │              │ Channel  │
         └────┬─────┘              └────┬─────┘
              │                         │
              │                         ▼
              │                  ┌─────────────┐
              │                  │ Show Error  │
              │                  │   Embed     │
              │                  └─────────────┘
              │
              ▼
       ┌──────────────┐
       │Check Cooldown│
       └──────┬───────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐      ┌──────────────┐
│ Ready   │      │  On Cooldown │
│         │      │              │
└────┬────┘      └──────┬───────┘
     │                  │
     │                  ▼
     │           ┌─────────────┐
     │           │ Show Time   │
     │           │  Remaining  │
     │           └─────────────┘
     │
     ▼
┌──────────────┐
│ Show Modal   │
│ (Form)       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ User Fills:  │
│ - Name       │
│ - Age        │
│ - Reason     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Validate Age │
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌─────┐ ┌──────┐
│Valid│ │Invalid│
└──┬──┘ └───┬──┘
   │        │
   │        ▼
   │   ┌────────┐
   │   │ Error  │
   │   └────────┘
   │
   ▼
┌──────────────────┐
│ Calculate Score  │
│ - Age (25 pts)   │
│ - Length (25 pts)│
│ - Keywords (30)  │
│ - Grammar (20)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Get AI Summary  │
│ (or heuristic)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Save to Database │
│ Set Cooldown     │
└────────┬─────────┘
         │
         ▼
    ┌────┴────┐
    │ Score?  │
    └────┬────┘
         │
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
┌──────┐ ┌──────┐ ┌──────┐
│ ≥70  │ │40-69 │ │ <40  │
└──┬───┘ └──┬───┘ └──┬───┘
   │        │        │
   ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│AUTO  │ │STAFF │ │AUTO  │
│ACCEPT│ │REVIEW│ │REJECT│
└──┬───┘ └──┬───┘ └──┬───┘
   │        │        │
   │        │        │
   ▼        │        ▼
┌──────────┐│   ┌──────────┐
│+ Approved││   │+ Rejected│
│  Role    ││   │  Role    │
│- Applicant│   │- Applicant│
│  Role    ││   │  Role    │
└────┬─────┘│   └────┬─────┘
     │      │        │
     ▼      │        ▼
┌──────────┐│   ┌──────────┐
│ Send DM  ││   │ Send DM  │
│ (Accept) ││   │ (Reject) │
└────┬─────┘│   └────┬─────┘
     │      │        │
     ▼      │        ▼
┌──────────┐│   ┌──────────┐
│Log Staff ││   │Log Staff │
│ Channel  ││   │ Channel  │
└──────────┘│   └──────────┘
            │
            ▼
     ┌──────────────┐
     │+ Applicant   │
     │  Role        │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Send DM      │
     │ (Pending)    │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Post to Staff│
     │ Review       │
     │ Channel      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Show Buttons:│
     │ ✅ Accept    │
     │ ❌ Reject    │
     │ 📋 History   │
     └──────┬───────┘
            │
      ┌─────┴─────┐
      │           │
      ▼           ▼
┌──────────┐ ┌──────────┐
│ Accept   │ │ Reject   │
│ Clicked  │ │ Clicked  │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐ ┌──────────┐
│+ Approved│ │+ Rejected│
│  Role    │ │  Role    │
│- Applicant│ │- Applicant│
│  Role    │ │  Role    │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐ ┌──────────┐
│Update DB │ │Update DB │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐ ┌──────────┐
│ Send DM  │ │ Send DM  │
└────┬─────┘ └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐ ┌──────────┐
│Confirm to│ │Confirm to│
│  Staff   │ │  Staff   │
└──────────┘ └──────────┘
```

---

## 🎯 Decision Points

### 1. Channel Check
```
if channel_id == APPLICATION_ONLY_CHANNEL:
    ✅ Continue
else:
    ❌ Show error embed
```

### 2. Cooldown Check
```
if time_since_last_app >= 7 days:
    ✅ Continue
else:
    ⏰ Show cooldown embed
```

### 3. Age Validation
```
if 1 <= age <= 120:
    ✅ Continue
else:
    ❌ Show error embed
```

### 4. Score-Based Decision
```
if score >= 70:
    ✅ Auto-accept
elif score < 40:
    ❌ Auto-reject
else:
    ⏳ Staff review
```

---

## 📋 Data Flow

### Application Submission
```
User Input → Validation → Scoring → AI Summary → Database → Decision
```

### Auto-Accept Flow
```
Score ≥ 70 → Add Approved Role → Remove Applicant Role → Send DM → Log
```

### Auto-Reject Flow
```
Score < 40 → Add Rejected Role → Remove Applicant Role → Send DM → Log
```

### Staff Review Flow
```
Score 40-69 → Add Applicant Role → Send DM → Post to Staff → Wait for Decision
```

### Staff Decision Flow
```
Button Click → Update Roles → Update Database → Send DM → Confirm to Staff
```

---

## 🗄️ Database Operations

### On Application Submit
```sql
INSERT INTO applications (user_id, username, age, reason, score, ai_summary, status)
INSERT INTO application_cooldowns (user_id, last_application)
```

### On Staff Review
```sql
UPDATE applications SET status = ?, reviewed_by = ?, reviewed_at = ?
```

### On Dashboard Command
```sql
SELECT COUNT(*), SUM(CASE...), AVG(score) FROM applications
```

### On History Command
```sql
SELECT * FROM applications WHERE user_id = ? ORDER BY applied_at DESC
```

---

## 🎨 Embed Flow

### User Receives
1. **Submission Confirmation** (ephemeral)
2. **DM Notification** (accepted/rejected/pending)

### Staff Receives
1. **Review Card** (in staff channel)
2. **Decision Confirmation** (after button click)

### Dashboard Shows
1. **Statistics Embed** (total, accepted, rejected, pending, avg score)

### History Shows
1. **User History Embed** (all past applications)

---

## ⚡ Quick Reference

| Score Range | Action | Role Changes | DM Sent | Staff Notified |
|-------------|--------|--------------|---------|----------------|
| 70-100 | Auto-Accept | +Approved, -Applicant | ✅ Yes | ✅ Yes (log) |
| 40-69 | Staff Review | +Applicant | ✅ Yes | ✅ Yes (review) |
| 0-39 | Auto-Reject | +Rejected, -Applicant | ✅ Yes | ✅ Yes (log) |

---

## 🔄 State Transitions

```
[No Application] → [Applied] → [Pending/Accepted/Rejected]
                      ↓
                [Cooldown Active]
                      ↓
                [7 Days Pass]
                      ↓
                [Can Apply Again]
```

---

This flow ensures every application is processed efficiently with appropriate notifications and role management! 🚀
