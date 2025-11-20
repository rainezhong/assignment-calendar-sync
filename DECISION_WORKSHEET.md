# Decision Worksheet: Friend Group Deployment

Fill this out to get a clear deployment plan. Takes 5 minutes!

## Quick Questions

### 1. Group Size & Timeline

**How many friends will use this?**
- [ ] Just me (1)
- [ ] Close friends (2-5)
- [ ] Friend group (5-15)
- [ ] Larger group (15-50)
- [ ] Community (50+)

**When do you want it working?**
- [ ] This weekend (ASAP)
- [ ] Within 2 weeks
- [ ] Within a month
- [ ] No rush, want it done right

**Your answer:** _______________

---

### 2. Technical Comfort Level

**Your technical comfort:**
- [ ] Can run terminal commands, understand basic DevOps
- [ ] Can follow guides but prefer simple solutions
- [ ] Want it to "just work" with minimal setup

**Your friends' technical comfort:**
- [ ] Technical (can troubleshoot on their own)
- [ ] Semi-technical (can follow instructions)
- [ ] Non-technical (need it to be completely plug-and-play)

**Your answer:** _______________

---

### 3. Budget & Cost Sharing

**How much can you spend per month?**
- [ ] $0 (free only)
- [ ] $10-20 (minimal)
- [ ] $30-50 (reasonable)
- [ ] $50-100 (willing to invest)
- [ ] $100+ (go big)

**Cost sharing approach:**
- [ ] I'll pay for everything
- [ ] Split equally among all users
- [ ] Each person pays for their own usage
- [ ] Haven't thought about it yet

**Your answer:** _______________

---

### 4. Privacy & Data Access

**Can you (the admin) see their data?**
- [ ] Yes, I need it for debugging (tell them upfront)
- [ ] Only aggregated stats, no personal info
- [ ] No, full privacy (more complex to implement)
- [ ] Haven't thought about it

**Your answer:** _______________

---

### 5. Distribution Preference

**How polished does it need to be?**
- [ ] Quick MVP, can look rough (Expo Go)
- [ ] Should look professional (TestFlight)
- [ ] Fully polished (App Store)

**Your answer:** _______________

---

## Decision Matrix

Based on your answers, here's what I recommend:

### Scenario 1: "Get It Working This Weekend"
**Your answers:**
- 2-5 friends
- This weekend
- $10-20/month budget
- I'll pay for now
- Quick MVP is fine

**Recommended Stack:**
- ✅ Railway (backend) - $20/month
- ✅ Expo Go (mobile) - Free
- ✅ Email/password auth - Already built
- ✅ GPT-3.5 (cover letters) - $5/month
- ✅ APScheduler (background jobs) - Built-in

**Total Cost:** ~$25/month
**Setup Time:** 2-3 hours
**Friend Setup Time:** 5 minutes (download Expo Go, scan QR)

---

### Scenario 2: "Professional but Affordable"
**Your answers:**
- 5-15 friends
- Within 2 weeks
- $30-50/month budget
- Split costs equally
- Should look professional

**Recommended Stack:**
- ✅ Railway (backend) - $25/month
- ✅ TestFlight (mobile) - $8/month (Apple Developer)
- ✅ Email/password auth - Already built
- ✅ GPT-3.5 (cover letters) - $10/month
- ✅ Railway Cron (background jobs) - Included

**Total Cost:** ~$43/month ÷ 15 friends = **$2.87/person/month**
**Setup Time:** 1 week (including TestFlight review)
**Friend Setup Time:** 10 minutes (TestFlight install + sign up)

---

### Scenario 3: "Go Big, Make It Right"
**Your answers:**
- 15-50 friends
- Within a month
- $50-100/month budget
- Usage-based pricing for friends
- Fully polished

**Recommended Stack:**
- ✅ DigitalOcean (backend) - $30/month
- ✅ TestFlight → App Store - $8/month
- ✅ Google/Apple sign-in - Better UX
- ✅ GPT-4 (cover letters) - $40/month (or user-provided keys)
- ✅ External cron service - $10/month
- ✅ Monitoring (Sentry) - $10/month

**Total Cost:** ~$98/month ÷ 50 friends = **$1.96/person/month**
**Setup Time:** 2-4 weeks (includes OAuth, App Store review)
**Friend Setup Time:** 5 minutes (App Store download + Google sign-in)

---

## Your Recommended Path

Based on most common scenarios, here's the **default recommendation:**

### **Start with Scenario 1, Evolve to Scenario 2**

**Week 1: MVP (Scenario 1)**
1. Deploy to Railway ($20/month)
2. Test with Expo Go (free)
3. Get 3-5 close friends testing
4. Use GPT-3.5 to keep costs low
5. Collect feedback

**Week 2-3: Polish (Scenario 2)**
1. Get Apple Developer account ($99/year)
2. Build for TestFlight
3. Add invite code system
4. Implement usage limits
5. Invite 10-15 friends

**Week 4+: Scale (Scenario 2+)**
1. Set up cost sharing ($2-3/person/month)
2. Add push notifications
3. Improve onboarding
4. Consider Google sign-in if needed

**Total Investment:**
- Time: ~10-15 hours over 3 weeks
- Money: ~$25/month (Week 1), ~$40/month (Week 2+)
- Apple Developer: $99 one-time (Week 2)

---

## Action Items (Check When Done)

### Immediate (This Week)
- [ ] Decide on deployment model (Scenario 1, 2, or 3)
- [ ] Sign up for Railway account
- [ ] Set up OpenAI API account (GPT-3.5)
- [ ] Deploy backend to Railway
- [ ] Test backend is working (API docs)
- [ ] Update mobile app with Railway URL
- [ ] Test with Expo Go yourself

### Short-term (Week 2)
- [ ] Invite 2-3 close friends to test
- [ ] Collect feedback on UX
- [ ] Fix critical bugs
- [ ] Decide if TestFlight is worth it
- [ ] If yes: Buy Apple Developer account
- [ ] Create privacy policy document

### Medium-term (Week 3-4)
- [ ] Implement data isolation checks (CRITICAL)
- [ ] Add usage limits (cover letters/month)
- [ ] Create onboarding tutorial
- [ ] Set up cost-sharing (Venmo, Splitwise, etc.)
- [ ] Invite broader friend group
- [ ] Create Discord/group chat for support

---

## Red Flags to Watch For

Stop and reassess if you see:

- ⚠️ OpenAI costs >$50/month (too many cover letters, switch to GPT-3.5 or limits)
- ⚠️ Railway costs >$40/month (need to optimize or switch to DigitalOcean)
- ⚠️ Friends can see each other's data (CRITICAL BUG, fix immediately)
- ⚠️ Background jobs not running (apps not being prepared)
- ⚠️ More than 50 users (consider monetizing or limiting)
- ⚠️ You're spending >5 hours/week on support (need better docs/FAQ)

---

## Critical Code Changes Needed

Before deploying to friends, YOU MUST implement:

### 1. Data Isolation (CRITICAL)

**File: `backend/app/api/v1/career.py`**

Every endpoint needs to check user ownership:

```python
# BEFORE (UNSAFE - anyone can see anything)
@router.get("/applications")
async def get_applications(db: AsyncSession):
    result = await db.execute(select(JobApplication))
    return result.scalars().all()

# AFTER (SAFE - users only see their own data)
@router.get("/applications")
async def get_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(JobApplication).where(JobApplication.user_id == current_user.id)
    )
    return result.scalars().all()
```

**Do this for ALL endpoints:**
- ✅ `/career/profile`
- ✅ `/career/jobs/matches`
- ✅ `/career/applications`
- ✅ `/career/queue/ready`
- ✅ `/intelligence/*`
- ✅ `/analytics/*`

### 2. Usage Limits

Add to `app/models/career.py`:

```python
class UserProfile(Base):
    # ... existing fields ...
    cover_letters_this_month: int = 0
    cover_letter_limit: int = 10  # Free tier limit
    last_reset_date: datetime = None
```

Add to `app/services/application_preparer.py`:

```python
async def prepare_application(self, profile: UserProfile, ...):
    # Check usage limit
    if profile.cover_letters_this_month >= profile.cover_letter_limit:
        logger.info(f"User {profile.user_id} hit cover letter limit")
        return None  # Don't generate cover letter

    # Generate cover letter
    cover_letter = await self._generate_cover_letter(...)

    # Increment usage
    profile.cover_letters_this_month += 1
    await db.commit()
```

### 3. Error Handling for Friends

Add to `mobile/src/services/api.ts`:

```typescript
// Better error messages for friends
this.client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Friendly error messages
    const friendlyMessages: Record<number, string> = {
      401: "Please log in again",
      403: "You don't have permission to do that",
      404: "Not found. Try refreshing the app",
      429: "Too many requests. Please wait a minute",
      500: "Something went wrong. We're looking into it!",
    };

    const status = error.response?.status;
    const message = status ? friendlyMessages[status] : "Network error";

    // Show friendly message to user
    alert(message);

    return Promise.reject(error);
  }
);
```

---

## Final Checklist Before Inviting Friends

- [ ] Backend deployed and accessible via HTTPS
- [ ] All API endpoints have user_id checks (data isolation)
- [ ] Usage limits implemented (cover letters)
- [ ] Error handling shows friendly messages
- [ ] Privacy policy created and shared
- [ ] Cost-sharing plan decided
- [ ] Support channel created (Discord/group chat)
- [ ] You've tested the full flow yourself
- [ ] At least 2 friends have tested successfully
- [ ] You have a way to monitor costs (Railway dashboard, OpenAI usage)

---

## My Recommendation

**For most people reading this:**

1. **Start Simple (Scenario 1):**
   - Deploy to Railway this weekend (~2 hours)
   - Test with Expo Go
   - Invite 3-5 close friends
   - Keep costs under $30/month
   - Learn and iterate

2. **Decide in 2 Weeks:**
   - If friends love it → Invest in TestFlight (Scenario 2)
   - If it's just OK → Keep it simple (Scenario 1)
   - If no one uses it → Shut it down (no sunk cost)

3. **Scale Only If Needed:**
   - Don't optimize prematurely
   - Don't build features no one asks for
   - Do fix bugs and improve UX based on feedback

**The goal:** Get something working quickly, see if friends actually use it, then invest more if it's valuable.

---

## What I Need From You

To give you a **specific step-by-step deployment guide**, please answer:

1. **Which scenario matches you?** (1, 2, or 3)
2. **How many friends initially?** (Number)
3. **What's your timeline?** (This weekend, 2 weeks, or 1 month)
4. **Are you comfortable with command line?** (Yes/No)
5. **Do you have an Apple Developer account?** (Yes/No/Willing to buy)

**Example answers:**
```
1. Scenario 2 (professional but affordable)
2. 10 friends
3. Within 2 weeks
4. Yes, comfortable with terminal
5. Don't have yet, but willing to buy if worth it
```

Once you answer, I'll create a **concrete implementation guide** with exact commands to run!
