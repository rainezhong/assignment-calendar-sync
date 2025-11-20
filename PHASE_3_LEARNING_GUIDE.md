# Phase 3: Key Software Development Concepts
## Ordered by Importance & Novelty

This guide complements the implementation with detailed explanations of advanced concepts. Use this as you trace through the code.

---

## 🥇 **1. IMAP Protocol & OAuth2 Authentication**
**Files:** `email_assistant.py:65-215`
**Importance:** 10/10 | **Novelty:** 9/10

### Why It Matters
IMAP is how modern email clients (like Gmail, Outlook) access emails without downloading them. OAuth2 provides secure authentication without passwords - critical for production applications.

### How It Works
```python
# TRACE THIS: Complete IMAP + OAuth2 flow

# Step 1: Generate OAuth2 authentication string
def _generate_oauth2_string(self) -> bytes:
    # XOAUTH2 format: base64("user={email}\x01auth=Bearer {token}\x01\x01")
    auth_string = (
        f"user={self.credentials.email_address}\x01"
        f"auth=Bearer {self.credentials.access_token}\x01\x01"
    )
    return auth_string.encode()

# Step 2: Connect via IMAP SSL (port 993)
self.connection = imaplib.IMAP4_SSL("imap.gmail.com", 993)

# Step 3: Authenticate with OAuth2
self.connection.authenticate('XOAUTH2', lambda x: auth_string)

# Step 4: Select mailbox
self.connection.select("INBOX")

# Step 5: Search emails
search_criteria = f'(SINCE {date})'
status, message_numbers = self.connection.search(None, search_criteria)

# Step 6: Fetch individual emails
status, msg_data = self.connection.fetch(email_id, '(RFC822)')
```

### Key Concepts
- **Stateful Protocol**: IMAP maintains connection state (unlike HTTP)
- **OAuth2 XOAUTH2**: Specialized OAuth flow for IMAP/SMTP
- **MIME Parsing**: Emails are multipart MIME documents
- **Incremental Fetching**: Fetch headers first, then body (efficiency)

### Learning Resources
- RFC 3501 (IMAP4): https://tools.ietf.org/html/rfc3501
- OAuth2 for IMAP: https://developers.google.com/gmail/imap/xoauth2-protocol

---

## 🥈 **2. CalDAV Protocol & iCalendar Format**
**Files:** `event_intelligence.py:40-135`
**Importance:** 9/10 | **Novelty:** 9/10

### Why It Matters
CalDAV is the universal protocol for calendar access - works with Google Calendar, iCloud, Outlook. iCalendar (.ics) is the standard format for event data.

### How It Works
```python
# TRACE THIS: CalDAV event fetching

# Step 1: Connect to CalDAV server
client = caldav.DAVClient(
    url="https://calendar.google.com/calendar/dav",
    username=username,
    password=password  # Or OAuth token
)

# Step 2: Get principal (user account)
principal = client.principal()

# Step 3: List calendars
calendars = principal.calendars()

# Step 4: Search events in date range
events = calendar.date_search(
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31)
)

# Step 5: Parse iCalendar format
for event in events:
    ical_data = event.data
    calendar = Calendar.from_ical(ical_data)

    for component in calendar.walk():
        if component.name == "VEVENT":
            title = component.get('summary')
            start = component.get('dtstart').dt
            end = component.get('dtend').dt
```

### iCalendar Format Structure
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Academic Assistant//EN
BEGIN:VEVENT
UID:assignment-123@academic.com
DTSTART:20250115T140000Z
DTEND:20250115T160000Z
SUMMARY:CS101 Assignment 3 Due
DESCRIPTION:Complete problem set 3
LOCATION:Canvas
END:VEVENT
END:VCALENDAR
```

### Key Concepts
- **CalDAV**: WebDAV extension for calendars (like IMAP for calendars)
- **VEVENT**: Event component in iCalendar
- **VTODO**: Task/todo component
- **RFC 5545**: iCalendar specification

---

## 🥉 **3. Feature Engineering for Machine Learning**
**Files:** `smart_reminders.py:38-150, 240-380`
**Importance:** 10/10 | **Novelty:** 10/10

### Why It Matters
This is **the most important ML concept**: transforming raw data into numerical features that predict outcomes. Great feature engineering beats fancy algorithms.

### How It Works
```python
# TRACE THIS: Complete feature extraction pipeline

async def _extract_features(self, assignment: Dict[str, Any]) -> Dict[str, float]:
    """
    Transform raw assignment data into predictive features
    Each feature is normalized to 0-1 range
    """
    features = {}

    # FEATURE 1: Assignment Type Complexity
    # Insight: Projects are harder than quizzes
    type_complexity = {
        'quiz': 0.1,      # ~30 minutes
        'homework': 0.3,  # ~2 hours
        'essay': 0.6,     # ~6 hours
        'project': 0.8,   # ~15 hours
    }
    features['assignment_type_score'] = type_complexity.get(type, 0.5)

    # FEATURE 2: Historical Course Difficulty
    # Insight: Same course assignments have similar difficulty
    avg_hours = self._get_course_average_hours(course)
    features['course_difficulty'] = min(1.0, avg_hours / 20.0)

    # FEATURE 3: Text Complexity (AI-powered)
    # Insight: Longer, technical descriptions = harder assignments
    complexity = await self._analyze_text_with_ai(description)
    features['length_complexity'] = complexity

    # FEATURE 4: Points Normalization
    # Insight: More points = more important/harder
    features['points_score'] = min(1.0, points / 200.0)

    # FEATURE 5: Time Pressure
    # Insight: Less time = higher effective difficulty
    days_until_due = (due_date - datetime.now()).days
    features['time_available'] = max(0.0, min(1.0, days_until_due / 14.0))

    # FEATURE 6: Requirements Count
    # Insight: More requirements = more work
    features['requirements_count'] = min(1.0, len(requirements) / 10.0)

    return features

# PREDICTION: Combine features with weights
def predict_difficulty(features: Dict[str, float]) -> float:
    # Weighted sum of features
    weights = {
        'assignment_type_score': 0.30,   # Type is most predictive
        'course_difficulty': 0.25,       # Historical data is reliable
        'length_complexity': 0.20,       # AI analysis adds context
        'points_score': 0.10,
        'time_available': 0.10,
        'requirements_count': 0.05
    }

    score = sum(features[k] * weights[k] for k in weights)

    # Map 0-1 score to difficulty level
    if score < 0.2: return "trivial"   # < 1 hour
    elif score < 0.4: return "easy"    # 1-3 hours
    elif score < 0.6: return "moderate" # 3-8 hours
    elif score < 0.8: return "hard"    # 8-15 hours
    else: return "very_hard"           # > 15 hours
```

### Feature Engineering Principles

1. **Domain Knowledge**: Use what you know about the problem
   - Example: "Projects take longer than quizzes" → encode as feature

2. **Normalization**: Scale all features to same range (0-1)
   - Why: Prevents large-value features from dominating

3. **Temporal Features**: Extract time-based patterns
   - Example: Hour of day → productivity score

4. **Interaction Features**: Combine features
   - Example: `difficulty × time_pressure = urgency`

5. **Historical Features**: Learn from past data
   - Example: Average completion time for this course

### Advanced: Transfer Learning
```python
# Use knowledge from similar assignments
def _adjust_with_history(features, historical_data):
    # Blend predicted features with historical averages
    historical_difficulty = historical_data['avg_hours'] / 20.0
    confidence = min(1.0, historical_data['sample_size'] / 10)

    # More history = more weight on historical data
    for key in features:
        features[key] = (
            features[key] * (1 - confidence) +
            historical_difficulty * confidence
        )

    return features
```

---

## 4. **Time Series Analysis & Pattern Recognition**
**Files:** `event_intelligence.py:180-305`
**Importance:** 9/10 | **Novelty:** 8/10

### Why It Matters
Time series analysis extracts patterns from temporal data - essential for predicting user behavior, optimizing schedules, and adaptive systems.

### How It Works
```python
# TRACE THIS: Learning productivity patterns from completion logs

def analyze_completion_history(logs: List[Dict]) -> UserProductivityPattern:
    """
    Aggregate time-series data to discover patterns
    """

    # STEP 1: Group events by temporal features
    hourly_completions = defaultdict(list)
    daily_completions = defaultdict(list)

    for log in logs:
        started = log['started_at']
        completed = log['completed_at']
        duration = (completed - started).total_seconds() / 3600  # hours

        # Extract temporal features
        hour = started.hour          # 0-23
        day_of_week = started.weekday()  # 0-6 (Mon-Sun)

        # Group by features
        hourly_completions[hour].append(duration)
        daily_completions[day_of_week].append(duration)

    # STEP 2: Calculate statistics per group
    pattern = UserProductivityPattern()

    # Calculate median baseline
    all_durations = [d for durations in hourly_completions.values() for d in durations]
    median_duration = statistics.median(all_durations)

    # STEP 3: Calculate productivity scores
    for hour, durations in hourly_completions.items():
        avg_duration = statistics.mean(durations)

        # Inverse relationship: faster = more productive
        productivity = median_duration / max(avg_duration, 0.1)

        # Normalize to 0-1
        pattern.hourly_productivity[hour] = min(1.0, max(0.0, productivity))

    return pattern

# USAGE: Predict productivity at specific time
def get_productivity_score(dt: datetime) -> float:
    hour = dt.hour
    day = dt.weekday()

    # Weighted combination of temporal features
    hour_score = pattern.hourly_productivity.get(hour, 0.5)
    day_score = pattern.daily_productivity.get(day, 0.5)

    return (hour_score * 0.7) + (day_score * 0.3)
```

### Time Series Concepts

1. **Temporal Aggregation**: Group by time periods
   ```python
   # Group by hour of day
   for event in events:
       hour = event.timestamp.hour
       hourly_data[hour].append(event)
   ```

2. **Moving Averages**: Smooth noisy data
   ```python
   # 7-day moving average
   window = 7
   smoothed = [
       sum(data[i:i+window]) / window
       for i in range(len(data) - window)
   ]
   ```

3. **Trend Detection**: Identify improving/declining patterns
   ```python
   # Compare recent vs historical
   recent_avg = mean(data[-30:])
   historical_avg = mean(data[:-30])
   trend = recent_avg - historical_avg  # Positive = improving
   ```

4. **Seasonality**: Detect recurring patterns
   ```python
   # Weekly patterns
   day_of_week_avg = {
       day: mean([d for d in data if d.weekday() == day])
       for day in range(7)
   }
   ```

---

## 5. **Constraint Satisfaction & Scheduling Algorithms**
**Files:** `event_intelligence.py:340-530`
**Importance:** 9/10 | **Novelty:** 7/10

### Why It Matters
Scheduling is a classic CS problem - optimizing time allocation with constraints. Used in OS task scheduling, meeting planners, project management.

### How It Works
```python
# TRACE THIS: Greedy scheduling with constraints

def suggest_study_schedule(assignments, existing_events, start, end):
    """
    Constraint satisfaction problem:
    - Maximize: Productivity (schedule during high-productivity times)
    - Constraints: No conflicts, complete before deadline, realistic hours
    """

    # STEP 1: Generate all possible time slots
    available_slots = generate_available_slots(existing_events, start, end)
    # Result: List of free 2-hour blocks

    # STEP 2: Score each slot
    for slot in available_slots:
        slot['score'] = calculate_productivity_score(slot['start'])
        slot['zone'] = get_productivity_zone(slot['start'])

    # STEP 3: Sort assignments by urgency (deadline first)
    sorted_assignments = sorted(
        assignments,
        key=lambda a: (a['due_date'], -a['importance'])
    )

    # STEP 4: Greedy allocation
    for assignment in sorted_assignments:
        # Estimate hours needed
        hours_needed = estimate_study_hours(assignment)

        # Sort slots by productivity (greedy: best first)
        best_slots = sorted(
            [s for s in available_slots if s['start'] < assignment['due_date']],
            key=lambda s: s['score'],
            reverse=True
        )

        # Allocate hours to best slots
        allocated_hours = 0
        for slot in best_slots:
            if allocated_hours >= hours_needed:
                break

            # Take what we need (up to slot duration)
            hours_to_allocate = min(
                hours_needed - allocated_hours,
                slot['duration_hours']
            )

            # Create study session
            create_study_session(assignment, slot, hours_to_allocate)
            allocated_hours += hours_to_allocate

            # Remove allocated slot
            available_slots.remove(slot)

    return study_sessions
```

### Algorithm Analysis

**Time Complexity**: O(n × m) where n = assignments, m = slots
**Space Complexity**: O(m) for storing slots
**Algorithm Type**: Greedy with constraints

### Optimization Techniques

1. **Greedy Algorithm**: Choose best option at each step
   - Fast: O(n log n)
   - Not always optimal but "good enough"

2. **Backtracking**: Try options, undo if they fail
   ```python
   def schedule_with_backtracking(assignments, slots, current=[]):
       if not assignments:
           return current  # Success!

       assignment = assignments[0]
       for slot in slots:
           if is_valid(assignment, slot):
               # Try this slot
               result = schedule_with_backtracking(
                   assignments[1:],
                   remove(slots, slot),
                   current + [(assignment, slot)]
               )
               if result:
                   return result

       return None  # No solution
   ```

3. **Dynamic Programming**: Optimal but complex
   - Breaks problem into overlapping subproblems
   - Memoizes solutions

---

## 6. **Active Learning Loop (ML Feedback)**
**Files:** `smart_reminders.py:458-490`
**Importance:** 9/10 | **Novelty:** 9/10

### Why It Matters
This is how ML systems improve over time - by learning from actual outcomes and updating predictions. Critical for adaptive systems.

### How It Works
```python
# TRACE THIS: Complete active learning cycle

# PHASE 1: Make Prediction
async def estimate_difficulty(assignment):
    features = extract_features(assignment)
    prediction = predict_from_features(features)

    # Store prediction for later comparison
    store_prediction(assignment.id, prediction)
    return prediction

# PHASE 2: User Completes Assignment
def on_assignment_completed(assignment_id, actual_time_spent):
    # Get original prediction
    prediction = get_stored_prediction(assignment_id)

    # PHASE 3: Calculate Error
    error = actual_time_spent - prediction.estimated_hours

    # PHASE 4: Update Model
    record_actual_difficulty(
        assignment_id,
        actual_hours=actual_time_spent,
        predicted_hours=prediction.estimated_hours
    )

    # PHASE 5: Retrain (Improve Future Predictions)
    update_feature_weights(error, features_used)

# Feature Weight Update (Gradient Descent)
def update_feature_weights(error, features):
    learning_rate = 0.01

    for feature_name, feature_value in features.items():
        # Gradient descent update
        weights[feature_name] -= learning_rate * error * feature_value

# RESULT: Next prediction uses updated weights
# Over time, predictions become more accurate!
```

### Active Learning Concepts

1. **Feedback Loop**: prediction → action → outcome → learning
   ```
   Predict difficulty (5 hours)
   ↓
   User spends time (actual: 7 hours)
   ↓
   Calculate error (+2 hours)
   ↓
   Update model (increase weight for "project" type)
   ↓
   Next project prediction is more accurate
   ```

2. **Error Metrics**: Measure prediction quality
   ```python
   # Mean Absolute Error
   MAE = mean([abs(actual - predicted) for actual, predicted in pairs])

   # Root Mean Squared Error (penalizes large errors more)
   RMSE = sqrt(mean([(actual - predicted)**2 for actual, predicted in pairs]))
   ```

3. **Online Learning**: Update model incrementally
   - vs Batch Learning: Retrain on all data periodically

4. **Exploration vs Exploitation**:
   - Exploitation: Use best-known strategy
   - Exploration: Try new strategies to learn

---

## 7. **Hybrid AI + Traditional Approaches**
**Files:** `email_assistant.py:318-360`
**Importance:** 9/10 | **Novelty:** 8/10

### Why It Matters
**Most important production lesson**: Don't use AI for everything! Hybrid systems are faster, cheaper, and more reliable.

### Decision Framework
```python
# TRACE THIS: When to use AI vs traditional code

def analyze_email(email_data):
    # STEP 1: Fast heuristic pre-filter (NO AI)
    # Cost: ~0.001 seconds, $0
    if not quick_academic_check(email_data):
        return mark_as_non_academic(email_data)

    # STEP 2: Traditional regex for structured data (NO AI)
    # Cost: ~0.01 seconds, $0
    dates = extract_dates_with_regex(email_data['body'])
    course_codes = extract_course_codes(email_data['subject'])

    # STEP 3: AI only for complex analysis
    # Cost: ~1 second, $0.01
    if is_ambiguous(email_data):
        ai_analysis = await ai_client.analyze(email_data)
        return merge(dates, course_codes, ai_analysis)

    return construct_result(dates, course_codes)
```

### Cost Analysis
```
Without Pre-filtering:
- 1000 emails × $0.01 = $10.00
- Time: 1000 seconds = 16.7 minutes

With Pre-filtering:
- 50 academic emails × $0.01 = $0.50
- 950 filtered × $0.00 = $0.00
- Time: ~60 seconds
- Savings: 95% cost, 94% time
```

### When to Use What

| Task | Approach | Why |
|------|----------|-----|
| Extract dates | **Regex** | Structured format, fast, free |
| Classify sentiment | **AI** | Nuanced, context-dependent |
| Find email addresses | **Regex** | Predictable pattern |
| Understand intent | **AI** | Requires reasoning |
| Parse JSON | **json.loads()** | Structured data |
| Summarize text | **AI** | Requires understanding |

### Implementation Pattern
```python
def hybrid_analysis(text):
    # Layer 1: Fast filters
    if not meets_basic_criteria(text):
        return quick_reject()

    # Layer 2: Traditional NLP
    features = {
        'word_count': len(text.split()),
        'has_dates': bool(re.search(date_pattern, text)),
        'has_urls': bool(re.search(url_pattern, text)),
        'sentiment_words': count_sentiment_words(text)
    }

    # Layer 3: AI only when needed
    if features['complexity_score'] > threshold:
        ai_result = await ai_client.analyze(text)
        return merge(features, ai_result)

    return classify_from_features(features)
```

---

## 8. **Prompt Engineering Best Practices**
**Files:** `email_assistant.py:236-295`, `smart_reminders.py:290-340`
**Importance:** 10/10 | **Novelty:** 10/10

### Why It Matters
Prompt engineering is **the most important skill for AI systems**. A great prompt can replace complex code.

### Anatomy of a Great Prompt
```python
# TRACE THIS: Perfect prompt structure

perfect_prompt = f"""
{role_definition}

{context_and_constraints}

{input_data}

{task_instructions_with_steps}

{examples_few_shot}

{output_format_specification}

{edge_cases_and_constraints}
"""
```

### Complete Example
```python
analysis_prompt = f"""
# 1. ROLE DEFINITION
You are an expert academic email analyzer with 10 years of experience helping students.

# 2. CONTEXT
CURRENT DATE: {datetime.now().strftime('%Y-%m-%d')}
USER TIMEZONE: PST
STUDENT YEAR: Junior

# 3. INPUT DATA
EMAIL TO ANALYZE:
From: {email.sender}
Subject: {email.subject}
Body:
{email.body[:1000]}

# 4. TASK WITH REASONING STEPS
Analyze this email and extract assignment information.

REASONING PROCESS (think step-by-step):
1. Is this truly an academic email, or just administrative?
2. What type of content: assignment, grade, announcement, other?
3. Are there explicit deadlines mentioned? (look for dates, "due", "submit")
4. What course is this for? (look for course codes like "CS 101")
5. Does the student need to take action?
6. How urgent is this? (combine deadline proximity + importance)

# 5. FEW-SHOT EXAMPLES
EXAMPLES OF GOOD ANALYSIS:

Example 1:
Input: "CS 106A: Problem Set 3 due Friday Oct 15 at 11:59 PM - worth 100 points"
Output: {{
    "is_academic": true,
    "email_type": "assignment",
    "course": "CS 106A",
    "assignments": [{{
        "title": "Problem Set 3",
        "due_date": "2025-10-15T23:59:00",
        "points": 100
    }}],
    "urgency": "high",
    "reasoning": "Clear assignment with specific deadline and point value"
}}

Example 2:
Input: "Department potluck this Friday at noon in the commons"
Output: {{
    "is_academic": false,
    "email_type": "social",
    "reasoning": "Social event, not coursework-related"
}}

# 6. OUTPUT FORMAT
Return valid JSON with this exact structure:
{{
    "is_academic": boolean,
    "email_type": "assignment|grade|announcement|office_hours|other",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of your analysis",
    "course": "course code or null",
    "assignments": [
        {{
            "title": "string",
            "due_date": "ISO-8601 format or null",
            "points_possible": number or null,
            "description": "string or null"
        }}
    ],
    "urgency": "low|medium|high|critical",
    "action_required": boolean
}}

# 7. CONSTRAINTS & EDGE CASES
IMPORTANT:
- Only mark is_academic=true if GENUINELY related to coursework
- Be conservative with confidence scores (< 0.9 if any ambiguity)
- Parse dates carefully - consider current date: {datetime.now()}
- Use null for missing information (never guess)
- If you see multiple assignments, extract ALL of them
- Urgency = combination of deadline proximity + importance
"""
```

### Prompt Engineering Principles

1. **Role Definition**: Tell the AI what it is
   - "You are an expert [domain] assistant..."
   - Provides context for tone and depth

2. **Chain-of-Thought**: Make it reason step-by-step
   - "First analyze X, then check Y, finally conclude Z"
   - Dramatically improves accuracy

3. **Few-Shot Learning**: Provide examples
   - 0-shot: No examples (least accurate)
   - 1-shot: One example (better)
   - Few-shot: 3-5 examples (best)

4. **Output Format**: Specify exact structure
   - JSON schema with types
   - Example output
   - Constraints (e.g., "0.0-1.0")

5. **Edge Cases**: Explicitly handle ambiguity
   - "If you're unsure, return confidence < 0.5"
   - "Use null for missing data, never guess"

6. **Context Injection**: Provide relevant data
   - Current date (for relative dates)
   - User preferences
   - Historical patterns

---

## 9. **Database Design for Learning Systems**
**Files:** `smart_reminders.py:103-125`, `memory_system.py:245-277`
**Importance:** 8/10 | **Novelty:** 6/10

### Why It Matters
Persistent storage is critical for learning systems - without historical data, you can't improve. Good schema design enables fast queries.

### Complete Schema Design
```sql
-- TRACE THIS: Database design for ML systems

-- 1. PREDICTIONS TABLE: Store all predictions
CREATE TABLE predictions (
    prediction_id TEXT PRIMARY KEY,
    assignment_hash TEXT NOT NULL,
    assignment_title TEXT,
    assignment_type TEXT,

    -- Prediction details
    estimated_hours REAL,
    estimated_difficulty TEXT,
    confidence_score REAL,
    features_json TEXT,  -- Store feature vector as JSON

    -- Timestamps
    predicted_at DATETIME NOT NULL,

    -- Indexes for fast queries
    INDEX idx_assignment_hash (assignment_hash),
    INDEX idx_predicted_at (predicted_at)
);

-- 2. ACTUALS TABLE: Store real outcomes
CREATE TABLE actuals (
    actual_id TEXT PRIMARY KEY,
    prediction_id TEXT REFERENCES predictions(prediction_id),
    assignment_hash TEXT NOT NULL,

    -- Actual outcome
    actual_hours REAL NOT NULL,
    actual_difficulty TEXT,
    started_at DATETIME,
    completed_at DATETIME,

    -- Calculated error
    hours_error REAL GENERATED AS (actual_hours - (
        SELECT estimated_hours FROM predictions
        WHERE predictions.prediction_id = actuals.prediction_id
    )),

    INDEX idx_assignment_hash (assignment_hash),
    INDEX idx_completed_at (completed_at)
);

-- 3. FEATURES TABLE: Track feature importance over time
CREATE TABLE feature_importance (
    feature_name TEXT PRIMARY KEY,
    weight REAL DEFAULT 0.5,
    update_count INTEGER DEFAULT 0,
    last_updated DATETIME,

    -- Statistics
    avg_error REAL,
    std_error REAL
);

-- 4. USER PATTERNS TABLE: Learn user behavior
CREATE TABLE user_patterns (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT,  -- 'hourly_productivity', 'completion_rate', etc.

    -- Pattern data (JSON)
    pattern_data TEXT,  -- e.g., {"hour_0": 0.3, "hour_1": 0.4, ...}

    -- Metadata
    sample_size INTEGER,
    confidence REAL,
    last_updated DATETIME,

    INDEX idx_pattern_type (pattern_type)
);
```

### Query Patterns

```python
# 1. Get average error per feature
def analyze_feature_performance():
    query = """
        SELECT
            feature_name,
            AVG(ABS(a.hours_error)) as avg_error,
            COUNT(*) as sample_size
        FROM predictions p
        JOIN actuals a ON p.prediction_id = a.prediction_id
        CROSS JOIN json_each(p.features_json) f  -- Unnest JSON
        WHERE a.actual_hours IS NOT NULL
        GROUP BY feature_name
        ORDER BY avg_error DESC
    """
    # Result: Which features have highest prediction error?

# 2. Get improvement trend over time
def calculate_improvement_trend():
    query = """
        WITH monthly_errors AS (
            SELECT
                strftime('%Y-%m', a.completed_at) as month,
                AVG(ABS(a.hours_error)) as avg_error
            FROM actuals a
            GROUP BY month
        )
        SELECT
            month,
            avg_error,
            LAG(avg_error) OVER (ORDER BY month) as prev_month_error,
            avg_error - LAG(avg_error) OVER (ORDER BY month) as improvement
        FROM monthly_errors
    """
    # Result: Is the model improving over time?

# 3. Find similar historical assignments
def find_similar_assignments(course, type, limit=5):
    query = """
        SELECT
            p.assignment_title,
            p.estimated_hours,
            a.actual_hours,
            p.features_json,
            a.completed_at
        FROM predictions p
        JOIN actuals a ON p.prediction_id = a.prediction_id
        WHERE p.assignment_type = ?
        AND p.assignment_title LIKE ?
        AND a.actual_hours IS NOT NULL
        ORDER BY a.completed_at DESC
        LIMIT ?
    """
    results = cursor.execute(query, (type, f"%{course}%", limit))
    # Result: Learn from similar past assignments
```

### Performance Optimization

```python
# 1. Indexes for common queries
CREATE INDEX idx_composite ON predictions(assignment_type, predicted_at);

# 2. Partial indexes (only index relevant rows)
CREATE INDEX idx_completed ON actuals(completed_at)
WHERE actual_hours IS NOT NULL;

# 3. Materialized views for expensive queries
CREATE TABLE productivity_summary AS
    SELECT
        strftime('%H', completed_at) as hour,
        AVG(actual_hours) as avg_hours,
        COUNT(*) as count
    FROM actuals
    GROUP BY hour;

# 4. Denormalization for read performance
-- Instead of JOIN on every query, duplicate data
ALTER TABLE predictions ADD COLUMN actual_hours REAL;
```

---

## 10. **Multi-Factor Scoring Systems**
**Files:** `event_intelligence.py:85-110`, `memory_system.py:361-408`
**Importance:** 8/10 | **Novelty:** 7/10

### Why It Matters
Real-world decisions rarely depend on one factor. Multi-factor scoring combines multiple signals into a single decision - used in recommendation systems, search ranking, priority queues.

### Complete Implementation
```python
# TRACE THIS: Building a multi-factor scoring system

class MultiFactorScorer:
    """
    Score items based on multiple weighted factors
    Used for: event priority, reminder timing, assignment urgency
    """

    def score_event_urgency(self, event: IntelligentEvent) -> float:
        """
        Calculate urgency score (0-1) from multiple factors

        Factors:
        1. Time until event (time pressure)
        2. Event importance (inherent priority)
        3. Preparation time needed (complexity)
        4. User's productivity at event time (efficiency)
        """

        # FACTOR 1: Time Pressure (40% weight)
        hours_until = event.time_until_start.total_seconds() / 3600

        if hours_until < 0:
            time_score = 0.0  # Past event
        elif hours_until < 24:
            time_score = 1.0  # Critical: < 1 day
        elif hours_until < 72:
            time_score = 0.8  # High: < 3 days
        elif hours_until < 168:
            time_score = 0.5  # Medium: < 1 week
        else:
            time_score = 0.3  # Low: > 1 week

        # FACTOR 2: Importance (30% weight)
        importance_score = event.importance_score  # Already 0-1

        # FACTOR 3: Preparation Complexity (20% weight)
        if event.estimated_prep_time:
            prep_hours = event.estimated_prep_time.total_seconds() / 3600
            prep_score = min(1.0, prep_hours / 20)  # Normalize to 0-1
        else:
            prep_score = 0.5

        # FACTOR 4: User Productivity (10% weight)
        # Higher productivity at event time = lower urgency (can do it efficiently)
        productivity = event.user_productivity_at_time
        productivity_score = 1.0 - (productivity / 1.0)  # Invert

        # COMBINE with weighted sum
        weights = {
            'time_pressure': 0.40,
            'importance': 0.30,
            'preparation': 0.20,
            'productivity': 0.10
        }

        urgency_score = (
            time_score * weights['time_pressure'] +
            importance_score * weights['importance'] +
            prep_score * weights['preparation'] +
            productivity_score * weights['productivity']
        )

        return urgency_score

    def select_optimal_strategy(self,
                               patterns: List[Pattern],
                               context_similarity: List[float]) -> Pattern:
        """
        Select best strategy using multi-factor scoring

        Factors:
        1. Success rate (has it worked before?)
        2. Context similarity (is it relevant?)
        3. Recency (is it up-to-date?)
        4. Usage count (is it well-tested?)
        """

        scored_patterns = []

        for pattern, similarity in zip(patterns, context_similarity):
            # FACTOR 1: Success Rate (40%)
            success_score = pattern.success_rate  # 0-1

            # FACTOR 2: Similarity (30%)
            similarity_score = similarity  # 0-1

            # FACTOR 3: Recency (20%)
            days_old = (datetime.now() - pattern.timestamp).days
            recency_score = max(0.1, 1.0 - (days_old / 30))  # Decay over 30 days

            # FACTOR 4: Reliability (10%)
            # More usage = more reliable (up to 10 uses)
            reliability_score = min(1.0, pattern.usage_count / 10)

            # COMBINE
            composite_score = (
                success_score * 0.40 +
                similarity_score * 0.30 +
                recency_score * 0.20 +
                reliability_score * 0.10
            )

            scored_patterns.append((pattern, composite_score))

        # Select highest scoring pattern
        best_pattern, best_score = max(scored_patterns, key=lambda x: x[1])

        logger.info(f"Selected pattern with score {best_score:.3f}")
        return best_pattern
```

### Weight Tuning Strategies

```python
# 1. MANUAL TUNING: Based on domain knowledge
weights = {
    'time_pressure': 0.40,  # Most important: don't miss deadlines
    'importance': 0.30,     # Second: prioritize important work
    'preparation': 0.20,    # Third: complex tasks need time
    'productivity': 0.10    # Least: nice to have optimization
}

# 2. GRID SEARCH: Try all combinations
best_weights = None
best_accuracy = 0

for w1 in [0.2, 0.3, 0.4, 0.5]:
    for w2 in [0.2, 0.3, 0.4]:
        for w3 in [0.1, 0.2, 0.3]:
            w4 = 1.0 - (w1 + w2 + w3)  # Ensure sum = 1.0

            weights = {'time': w1, 'importance': w2, 'prep': w3, 'prod': w4}
            accuracy = evaluate_weights(weights, validation_data)

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_weights = weights

# 3. GRADIENT DESCENT: Optimize mathematically
def optimize_weights(training_data, learning_rate=0.01, epochs=100):
    weights = [0.25, 0.25, 0.25, 0.25]  # Start equal

    for epoch in range(epochs):
        for sample in training_data:
            # Calculate prediction
            predicted = sum(
                w * f for w, f in zip(weights, sample.features)
            )

            # Calculate error
            error = sample.actual - predicted

            # Update weights (gradient descent)
            for i in range(len(weights)):
                gradient = -2 * error * sample.features[i]
                weights[i] -= learning_rate * gradient

        # Normalize to sum to 1.0
        total = sum(weights)
        weights = [w / total for w in weights]

    return weights
```

### When to Use Multi-Factor Scoring

✅ **Good use cases:**
- Ranking search results
- Prioritizing tasks
- Selecting recommendations
- Resource allocation

❌ **Bad use cases:**
- Binary decisions (yes/no)
- When one factor dominates
- Real-time critical systems (too slow)

---

## Summary: Learning Path

### Beginner → Intermediate
1. Start with **IMAP & OAuth2** - understand protocols
2. Learn **Feature Engineering** - foundation of ML
3. Study **Prompt Engineering** - practical AI skills
4. Master **Database Design** - persistent systems

### Intermediate → Advanced
5. **Time Series Analysis** - pattern recognition
6. **Multi-Factor Scoring** - decision systems
7. **Constraint Satisfaction** - optimization algorithms
8. **Active Learning** - self-improving systems

### Advanced
9. **Hybrid AI Systems** - production architecture
10. **CalDAV & iCalendar** - calendar integration

---

## Practical Exercises

### Exercise 1: Feature Engineering
```python
# Extract features from this assignment description:
assignment = {
    'title': 'Machine Learning Final Project',
    'description': 'Implement neural network from scratch, write 10-page paper',
    'course': 'CS 229',
    'points': 200,
    'due_date': datetime(2025, 12, 15)
}

# TODO: Extract 6+ features, predict difficulty
```

### Exercise 2: Multi-Factor Scoring
```python
# Score these events by urgency:
events = [
    {'title': 'CS exam', 'hours_until': 24, 'importance': 0.9, 'prep_hours': 10},
    {'title': 'History essay', 'hours_until': 72, 'importance': 0.7, 'prep_hours': 8},
    {'title': 'Lab report', 'hours_until': 168, 'importance': 0.6, 'prep_hours': 3}
]

# TODO: Implement scoring, rank by urgency
```

### Exercise 3: Active Learning
```python
# Simulate learning loop:
predictions = [
    {'estimated': 5.0, 'actual': 7.0},  # Underestimated
    {'estimated': 8.0, 'actual': 6.0},  # Overestimated
    {'estimated': 10.0, 'actual': 12.0}
]

# TODO: Calculate errors, update model weights
```

---

## Additional Resources

### Books
- **"Feature Engineering for Machine Learning"** by Alice Zheng
- **"Designing Data-Intensive Applications"** by Martin Kleppmann
- **"The Hundred-Page Machine Learning Book"** by Andriy Burkov

### Papers
- "Chain-of-Thought Prompting Elicits Reasoning in LLMs" (Wei et al., 2022)
- "Feature Engineering and Selection" (Kuhn & Johnson, 2019)

### Documentation
- RFC 3501 (IMAP): https://tools.ietf.org/html/rfc3501
- RFC 5545 (iCalendar): https://tools.ietf.org/html/rfc5545
- CalDAV: https://tools.ietf.org/html/rfc4791

---

**Remember**: The best way to learn is by tracing through the code! Use the `# TRACE THIS:` comments to step through complex logic. Build your understanding incrementally.
