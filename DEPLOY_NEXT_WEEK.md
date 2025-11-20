# Deploy Next Week: Upgrade to TestFlight (Professional Polish)

**Goal:** Polished app for 10-20 friends via TestFlight

**Prerequisites:**
- ✅ Completed DEPLOY_TODAY.md
- ✅ 5 friends tested with Expo Go
- ✅ Collected feedback and fixed critical bugs
- ✅ Apple Developer account ($99/year)

**Timeline:** 1 week total

---

## Week 2 Plan Overview

- **Monday-Tuesday:** Build and test locally
- **Wednesday:** Submit to TestFlight
- **Thursday-Friday:** TestFlight review + fixes
- **Weekend:** Roll out to 10-20 friends

---

## Step 1: Build for iOS (Monday)

### 1.1: Install EAS CLI

```bash
npm install -g eas-cli
```

### 1.2: Login to Expo Account

```bash
cd mobile
eas login
```

### 1.3: Configure EAS Build

Create `mobile/eas.json`:

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "production": {
      "distribution": "store",
      "ios": {
        "bundleIdentifier": "com.yourname.collegeassistant"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your.apple.id@email.com",
        "ascAppId": "PLACEHOLDER",
        "appleTeamId": "YOUR_TEAM_ID"
      }
    }
  }
}
```

### 1.4: Update app.json

**File: `mobile/app.json`**

Update these fields:

```json
{
  "expo": {
    "name": "College Assistant",
    "slug": "college-assistant",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#4F46E5"
    },
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.yourname.collegeassistant",
      "buildNumber": "1.0.0"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.yourname.collegeassistant"
    }
  }
}
```

### 1.5: Create App Icons

You need:
- `icon.png` (1024x1024)
- `splash.png` (1242x2436 or similar)
- `adaptive-icon.png` (1024x1024 for Android)

**Quick way:** Use https://www.appicon.co/ to generate all sizes from one image.

### 1.6: Build for TestFlight

```bash
cd mobile
eas build --platform ios --profile production
```

This will:
1. Ask you to create/login to Apple Developer account
2. Create certificates and provisioning profiles
3. Build your app in the cloud (~10-20 min)
4. Give you a download link

---

## Step 2: Submit to TestFlight (Wednesday)

### 2.1: Create App in App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" → "+" → "New App"
3. Fill in:
   - **Platform:** iOS
   - **Name:** College Assistant
   - **Primary Language:** English (US)
   - **Bundle ID:** com.yourname.collegeassistant
   - **SKU:** collegeassistant (or any unique identifier)
   - **User Access:** Full Access

### 2.2: Add App Information

1. Click on your new app
2. Go to "App Information"
3. Fill in:
   - **Category:** Education or Productivity
   - **Privacy Policy URL:** (Create a simple one, see below)
   - **Subtitle:** "AI-Powered Job Application Assistant"
   - **Description:** (See template below)

**Privacy Policy (Quick Template):**

Create a GitHub Gist or Google Doc:

```
Privacy Policy for College Assistant

We collect:
- Your email and name
- Resume data you upload
- Job preferences
- Application history

We use this data to:
- Find jobs matching your preferences
- Generate cover letters
- Track your applications

We share data with:
- OpenAI (for cover letter generation)
- Job sites (LinkedIn/Indeed) when scraping

You can:
- Delete your account anytime
- Export your data
- Contact us at: your.email@example.com

Last updated: [Today's date]
```

**Description Template:**

```
College Assistant helps students apply to jobs and internships faster using AI.

FEATURES:
• Automatic job search from LinkedIn and Indeed
• AI-powered job matching
• Auto-generated cover letters
• One-tap application submission
• Application tracking

HOW IT WORKS:
1. Upload your resume
2. Set your preferences
3. We find matching jobs daily
4. Review and submit applications in seconds

Save 18 minutes per application. Get more interviews.

Perfect for college students seeking internships, co-ops, and entry-level positions.
```

### 2.3: Upload Build to TestFlight

```bash
cd mobile
eas submit --platform ios
```

This will:
1. Upload your build to App Store Connect
2. Take 5-10 minutes
3. Show up in TestFlight section

### 2.4: Set Up TestFlight

1. Go to App Store Connect → TestFlight
2. Click on your build (should say "Ready to Submit")
3. Fill in "What to Test":
   ```
   First beta release. Please test:
   - Sign up and login
   - Resume upload
   - Setting job preferences
   - Viewing prepared applications
   - Submitting an application

   Known issues: None yet!
   ```

4. Click "Submit for Review"

**Apple will review in 1-3 days.**

---

## Step 3: Invite Friends (After Apple Approves)

### 3.1: Create Test Group

1. In TestFlight section of App Store Connect
2. Click "Internal Testing" or "External Testing"
3. Click "+" to create new group
4. Name it "Friends Beta"

**Internal vs External:**
- **Internal:** Up to 100 testers, no Apple review, instant access
- **External:** Up to 10,000 testers, requires Apple review (1-3 days)

**Recommendation:** Start with Internal for your 5 close friends, then expand to External.

### 3.2: Add Testers by Email

1. Click on your test group
2. Click "Add Testers"
3. Enter friends' emails (must be Apple ID emails)
4. They'll get email invite

### 3.3: Send Instructions to Friends

Create a message:

```
Hey! The app is ready to test on TestFlight 🎉

SETUP (2 minutes):

1. Check your email for "You're invited to test College Assistant"
2. Click "View in TestFlight" or "Accept"
3. Install TestFlight app (if you don't have it)
4. Install College Assistant from TestFlight

That's it! The app will auto-update when I push new versions.

GETTING STARTED:

1. Open app and sign up
2. Upload your resume (PDF)
3. Set job preferences (roles, locations, salary)
4. Check back tomorrow - you'll have jobs to review!

FEEDBACK:

Found a bug? Have a suggestion? Let me know!
- Text me
- Or use "Send Feedback" in TestFlight

Thanks for testing! 🚀
```

---

## Step 4: Polish Based on Feedback (Week 2-3)

### Things to Add/Fix:

#### **A. Better Onboarding**

Add tutorial screens on first launch:

**File: `mobile/src/screens/OnboardingScreen.tsx`** (create new)

```typescript
import React, { useState } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

export default function OnboardingScreen({ navigation }) {
  const [page, setPage] = useState(0);

  const pages = [
    {
      title: "Find Jobs Automatically",
      description: "We search LinkedIn and Indeed daily for jobs matching your skills",
      icon: "search"
    },
    {
      title: "AI Does the Work",
      description: "Cover letters generated, applications pre-filled",
      icon: "robot"
    },
    {
      title: "Just Tap Submit",
      description: "Review prepared applications and apply in seconds",
      icon: "rocket"
    }
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{pages[page].title}</Text>
      <Text style={styles.description}>{pages[page].description}</Text>

      {page < pages.length - 1 ? (
        <TouchableOpacity onPress={() => setPage(page + 1)}>
          <Text>Next</Text>
        </TouchableOpacity>
      ) : (
        <TouchableOpacity onPress={() => navigation.replace('Main')}>
          <Text>Get Started</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}
```

#### **B. Push Notifications**

Add Expo Notifications:

```bash
npx expo install expo-notifications
```

Send notification when applications are ready:

```typescript
// backend/app/services/application_preparer.py
# After creating prepared application
await send_push_notification(
    user_id=profile.user_id,
    title="New Application Ready!",
    body=f"Review your application for {job.title} at {job.company}"
)
```

#### **C. Usage Stats Screen**

Show users their usage in Settings:

```typescript
<View>
  <Text>Cover Letters Used: {profile.cover_letters_generated} / {profile.cover_letter_limit}</Text>
  <Text>Resets: {formatDate(profile.usage_reset_date)}</Text>
</View>
```

#### **D. Invite Code System**

Add invite codes to control who can sign up:

**File: `backend/app/models/user.py`**

```python
class InviteCode(Base):
    __tablename__ = "invite_codes"

    code = Column(String, primary_key=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    used_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
```

Update registration to require invite code:

```python
@router.post("/register")
async def register(
    email: str,
    password: str,
    invite_code: str,  # NEW: Required
    db: AsyncSession = Depends(get_db)
):
    # Check invite code
    code = await db.get(InviteCode, invite_code)
    if not code or code.current_uses >= code.max_uses:
        raise HTTPException(status_code=400, detail="Invalid invite code")

    # ... rest of registration ...

    # Mark invite code as used
    code.current_uses += 1
    code.used_by_user_id = new_user.id
    code.used_at = datetime.utcnow()
    await db.commit()
```

#### **E. Cost Sharing System**

Track costs per user:

```python
# backend/app/models/billing.py
class UserBilling(Base):
    __tablename__ = "user_billing"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    cover_letters_this_month = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)  # In USD

    # Calculate: $0.02 per cover letter (GPT-3.5)
```

Add billing endpoint:

```python
@router.get("/billing/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    billing = await db.get(UserBilling, current_user.id)
    return {
        "cover_letters": billing.cover_letters_this_month,
        "estimated_cost": billing.estimated_cost,
        "share": billing.estimated_cost / total_users
    }
```

---

## Step 5: Set Up Cost Sharing (Week 3)

### Options:

#### **Option A: Venmo/Cash App (Simplest)**

1. Calculate total monthly cost: $40
2. Divide by number of friends: $40 / 10 = $4/person
3. Send Venmo request at end of month

#### **Option B: Stripe Subscriptions (Professional)**

1. Set up Stripe account
2. Create subscription product ($2-5/month)
3. Add Stripe integration to app
4. Users pay directly via credit card

#### **Option C: Usage-Based Billing**

Track actual usage per user and charge accordingly:
- $0.02 per cover letter generated
- $0.50 per month base fee
- Send invoice at end of month

---

## Success Metrics (Week 2-4)

Track these to see if it's working:

### User Engagement:
- [ ] 80%+ of testers complete onboarding
- [ ] 50%+ upload resume within 24 hours
- [ ] 80%+ set job preferences
- [ ] 30%+ check app daily

### Feature Usage:
- [ ] Average 5+ job matches per user per day
- [ ] Average 2+ applications submitted per user per week
- [ ] Cover letter quality rating >4/5

### Technical:
- [ ] App crashes <1% of sessions
- [ ] API response time <500ms
- [ ] Background jobs run successfully >95% of the time

### Business:
- [ ] Total cost <$50/month
- [ ] Cost per active user <$5/month
- [ ] Friends willing to pay $2-5/month

---

## Cost Estimate (Week 2+)

| Item | Cost | Notes |
|------|------|-------|
| Railway (backend) | $25/month | For 10-20 users |
| OpenAI (GPT-3.5) | $10-20/month | 500-1000 cover letters |
| Apple Developer | $8.25/month | $99/year amortized |
| Domain (optional) | $1/month | collegeassistant.app |
| **Total** | **$44-54/month** | |
| **Per user (20 friends)** | **$2.20-2.70/month** | Very affordable! |

---

## Rollout Plan

### Week 1: Expo Go (5 friends)
- MVP testing
- Core functionality validation
- Collect feedback

### Week 2: TestFlight Internal (10 friends)
- Polish based on Week 1 feedback
- More robust testing
- Identify edge cases

### Week 3: TestFlight External (20-50 friends)
- Expand to wider group
- Implement cost sharing
- Add polish features

### Week 4+: Iterate
- Fix bugs
- Add requested features
- Consider App Store release (if popular)

---

## When to Move to App Store (Optional)

Consider full App Store release if:

- ✅ 50+ active users
- ✅ <1% crash rate
- ✅ Positive feedback from beta testers
- ✅ Revenue covers costs ($2-5/user/month)
- ✅ You want to open it up publicly

**App Store Pros:**
- Discoverable by anyone
- More professional
- No TestFlight expiration

**App Store Cons:**
- Strict review process (1-3 days per update)
- Can be rejected for various reasons
- Harder to keep it "friends only"

---

## Next Steps Checklist

This week:
- [ ] Get Apple Developer account (if not done)
- [ ] Fix any critical bugs from Week 1 testing
- [ ] Create app icons and splash screen
- [ ] Build with EAS (`eas build --platform ios`)
- [ ] Create App Store Connect listing
- [ ] Submit to TestFlight
- [ ] Wait for Apple approval (1-3 days)
- [ ] Invite 5-10 more friends
- [ ] Set up cost sharing

Next week:
- [ ] Collect feedback from TestFlight testers
- [ ] Implement top 3 requested features
- [ ] Add push notifications
- [ ] Improve onboarding flow
- [ ] Expand to 20-30 friends

---

**You're on track!** 🚀

By end of Week 2, you'll have a polished app that 10-20 friends can use professionally via TestFlight.

Let me know when you're ready for Week 3 (scaling to 50+) or if you hit any issues!
