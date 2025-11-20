# Quick Reference Guide
## Key Concepts at a Glance

Use this as your **cheat sheet** while coding!

---

## 🔥 Top 10 Concepts (Must Master)

| # | Concept | File | Line | Difficulty | Value |
|---|---------|------|------|------------|-------|
| 1 | Feature Engineering | `smart_reminders.py` | 240-380 | ⭐⭐⭐⭐ | 🏆🏆🏆🏆🏆 |
| 2 | Predictive Modeling | `predictive_assistant.py` | 20-250 | ⭐⭐⭐⭐⭐ | 🏆🏆🏆🏆🏆 |
| 3 | Prompt Engineering | `email_assistant.py` | 236-295 | ⭐⭐⭐⭐ | 🏆🏆🏆🏆🏆 |
| 4 | Protocol Pattern | `base_agent.py` | 20-32 | ⭐⭐⭐ | 🏆🏆🏆🏆 |
| 5 | Time Series Analysis | `performance_analytics.py` | 185-350 | ⭐⭐⭐⭐ | 🏆🏆🏆🏆🏆 |
| 6 | IMAP & OAuth2 | `email_assistant.py` | 65-215 | ⭐⭐⭐⭐ | 🏆🏆🏆🏆 |
| 7 | Active Learning | `smart_reminders.py` | 458-490 | ⭐⭐⭐⭐ | 🏆🏆🏆🏆 |
| 8 | Multi-Factor Scoring | `event_intelligence.py` | 85-110 | ⭐⭐⭐ | 🏆🏆🏆🏆 |
| 9 | Optimization Algorithms | `predictive_assistant.py` | 285-450 | ⭐⭐⭐⭐⭐ | 🏆🏆🏆🏆 |
| 10 | Bloom's Taxonomy | `assignment_intelligence.py` | 65-118 | ⭐⭐⭐ | 🏆🏆🏆 |

---

## 📂 File Navigator

### Phase 1-2: Foundation
```
python/agents/
├── base_agent.py              ← START HERE (Protocols, ABC, Factory)
├── visual_agent.py            ← Browser automation
├── assignment_parser.py       ← NLP extraction
├── memory_system.py           ← Vector DB, Learning
└── ai_orchestrator.py         ← System integration
```

### Phase 3: Production Systems
```
python/agents/
├── email_assistant.py         ← IMAP, OAuth2, Email parsing
├── event_intelligence.py      ← CalDAV, Scheduling, Productivity
└── smart_reminders.py         ← ML, Feature engineering, Adaptive
```

### Phase 4: AI Intelligence
```
python/agents/
├── assignment_intelligence.py ← Complexity analysis, Bloom's, Resources
├── performance_analytics.py   ← Time series, Health metrics, Trends
└── predictive_assistant.py    ← Risk prediction, Optimization, Recommendations
```

---

## 🎯 Common Patterns Quick Reference

### Protocol-Oriented Programming
```python
# WHEN: Define behavior contract without implementation
# WHY: More flexible than inheritance

from typing import Protocol

class AIClient(Protocol):
    async def analyze(self, text: str) -> dict: ...

# Any class with this method satisfies protocol
class OpenAIClient:  # No inheritance!
    async def analyze(self, text: str) -> dict:
        return await openai.complete(text)
```

### Factory Pattern
```python
# WHEN: Create objects dynamically
# WHY: Plugin system, extensibility

class AgentFactory:
    _agents = {}

    @classmethod
    def register(cls, name: str, agent_class: type):
        cls._agents[name] = agent_class

    @classmethod
    def create(cls, name: str):
        return cls._agents[name]()

# Usage
AgentFactory.register('email', EmailAgent)
agent = AgentFactory.create('email')  # Dynamic!
```

### Context Manager
```python
# WHEN: Manage resources (files, connections)
# WHY: Guarantee cleanup

class ResourceManager:
    async def __aenter__(self):
        # Setup
        self.resource = await connect()
        return self.resource

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup (ALWAYS runs)
        await self.resource.close()
        return False  # Don't suppress exceptions

# Usage
async with ResourceManager() as resource:
    await resource.do_work()
# Cleanup happens automatically!
```

---

## 🤖 AI Integration Patterns

### Prompt Engineering Template
```python
perfect_prompt = f"""
# 1. ROLE
You are an expert [domain] assistant with [credentials].

# 2. CONTEXT
Current date: {datetime.now()}
User: {user_context}

# 3. INPUT
{input_data}

# 4. TASK (with reasoning)
Analyze this and:
1. First, [step 1]
2. Then, [step 2]
3. Finally, [step 3]

# 5. EXAMPLES (few-shot)
Example 1: {example_1}
Example 2: {example_2}

# 6. OUTPUT FORMAT
{{
    "result": "value",
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}}

# 7. CONSTRAINTS
- Use null for missing data
- Be conservative with confidence
- Explain your reasoning
"""
```

### Hybrid AI + Rules
```python
# WHEN: Balance cost and accuracy
# WHY: 95% cost savings possible

def process(data):
    # Fast filter (free)
    if not quick_check(data):
        return reject()  # 90% filtered here

    # Traditional extraction (fast, cheap)
    features = extract_with_regex(data)

    # AI only when needed (slow, expensive)
    if is_ambiguous(features):
        ai_result = await ai_client.analyze(data)
        return merge(features, ai_result)

    return features  # Skip AI when possible
```

---

## 🔬 ML Patterns Quick Reference

### Feature Engineering
```python
# WHEN: Transform raw data → ML features
# WHY: Features > algorithms

def extract_features(assignment):
    return {
        # Categorical → numeric
        'type_score': type_map[assignment['type']],

        # Normalize to 0-1
        'length_score': min(1.0, word_count / 1000),

        # Time-based
        'urgency': days_until_due / 14,

        # Historical
        'course_difficulty': get_avg_hours(course),

        # Interaction features
        'complexity': length * difficulty
    }

# Prediction = weighted sum of features
score = sum(feature * weight for feature, weight in features.items())
```

### Predictive Modeling
```python
# WHEN: Predict future events
# WHY: Proactive vs reactive

def predict_risk(assignment, history):
    # Multi-factor probability
    probability = (
        time_pressure * 0.5 +      # Most important
        (1 - success_rate) * 0.3 + # Historical
        stress_level * 0.2          # Current load
    )

    # Risk = Probability × Impact
    risk_score = probability * impact

    if risk_score > 0.7:
        return "CRITICAL"
    elif risk_score > 0.5:
        return "HIGH"
    else:
        return "LOW"
```

### Time Series Analysis
```python
# WHEN: Analyze temporal data
# WHY: Trends, forecasting, anomalies

# Moving average (smoothing)
def smooth(data, window=7):
    return [
        sum(data[i:i+window]) / window
        for i in range(len(data) - window + 1)
    ]

# Trend detection
def detect_trend(data):
    # Fit line: y = mx + b
    slope = calculate_slope(data)

    if slope > 2:
        return "improving"
    elif slope < -2:
        return "declining"
    else:
        return "stable"

# Anomaly detection
def find_outliers(data):
    mean = statistics.mean(data)
    std = statistics.stdev(data)

    return [
        x for x in data
        if abs((x - mean) / std) > 2  # 2 std devs
    ]
```

---

## 💾 Database Patterns

### Time Series Schema
```sql
-- Store events with timestamps
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_type TEXT NOT NULL,
    value REAL NOT NULL,
    metadata JSON,
    timestamp DATETIME NOT NULL,

    INDEX idx_type_time (event_type, timestamp)
);

-- Efficient time-range queries
SELECT event_type, AVG(value)
FROM events
WHERE timestamp BETWEEN ? AND ?
GROUP BY event_type;
```

### Learning Database
```sql
-- Store predictions + actuals for learning
CREATE TABLE predictions (
    id TEXT PRIMARY KEY,
    predicted_value REAL,
    features JSON,
    predicted_at DATETIME
);

CREATE TABLE actuals (
    prediction_id TEXT REFERENCES predictions(id),
    actual_value REAL,
    error REAL,  -- actual - predicted
    completed_at DATETIME
);

-- Calculate model accuracy
SELECT
    AVG(ABS(error)) as mean_absolute_error,
    AVG(error * error) as mean_squared_error
FROM actuals
WHERE completed_at > DATE('now', '-30 days');
```

---

## 🎯 Common Algorithms

### Greedy Scheduling
```python
# O(n log n) time, ~85% optimal
def greedy_schedule(tasks, max_hours_per_day):
    # Sort by deadline
    tasks.sort(key=lambda t: t['deadline'])

    schedule = []
    current_day = 0
    hours_today = 0

    for task in tasks:
        hours_needed = task['hours']

        while hours_needed > 0:
            available = max_hours_per_day - hours_today

            if available > 0:
                take = min(available, hours_needed)
                schedule.append((current_day, task, take))
                hours_needed -= take
                hours_today += take
            else:
                current_day += 1
                hours_today = 0

    return schedule
```

### Load Balancing
```python
# Distribute work evenly across days
def balance_workload(tasks, days):
    daily_schedule = [[] for _ in range(days)]
    daily_hours = [0] * days

    # Sort by size (largest first)
    tasks.sort(key=lambda t: t['hours'], reverse=True)

    for task in tasks:
        # Assign to day with least work
        min_day = daily_hours.index(min(daily_hours))
        daily_schedule[min_day].append(task)
        daily_hours[min_day] += task['hours']

    return daily_schedule, daily_hours
```

### Moving Average
```python
# Smooth noisy time series
def moving_average(data, window=7):
    return [
        sum(data[i:i+window]) / window
        for i in range(len(data) - window + 1)
    ]

# Example: [10, 50, 20, 80, 30, 60]
# Window=3: [26.7, 50.0, 43.3, 56.7]
# Smoother trend visible
```

---

## ⚡ Performance Optimization Tricks

### Caching
```python
# 3-level cache (L1 → L2 → L3)
memory_cache = {}  # L1: RAM (1μs)
file_cache = {}    # L2: Disk (100μs)

def get_with_cache(key):
    # L1: Memory
    if key in memory_cache:
        return memory_cache[key]

    # L2: File
    if key in file_cache:
        result = load_from_file(key)
        memory_cache[key] = result
        return result

    # L3: Compute (expensive)
    result = expensive_operation(key)
    file_cache[key] = result
    memory_cache[key] = result
    return result
```

### Batch Processing
```python
# Process multiple items in single AI call
async def batch_process(items, batch_size=10):
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]

        # Single API call for batch (5× faster)
        batch_results = await ai_client.batch_analyze(batch)
        results.extend(batch_results)

        await asyncio.sleep(0.1)  # Rate limiting

    return results
```

### Pre-filtering
```python
# Filter before expensive operations
def process(data):
    # Quick filter (1ms)
    if not passes_heuristics(data):
        return None  # 90% filtered

    # Expensive AI (1000ms)
    return ai_analyze(data)  # Only 10% reach here

# Result: 100× faster overall!
```

---

## 🐛 Debugging Tips

### Add Instrumentation
```python
import logging
import time

logger = logging.getLogger(__name__)

def instrumented_function(data):
    start = time.time()

    try:
        result = process(data)

        logger.info(
            "Function succeeded",
            extra={
                'duration_ms': (time.time() - start) * 1000,
                'data_size': len(data),
                'result_count': len(result)
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Function failed: {e}",
            extra={
                'duration_ms': (time.time() - start) * 1000,
                'error_type': type(e).__name__
            },
            exc_info=True  # Include traceback
        )
        raise
```

### Assert Invariants
```python
def calculate_score(features):
    # Pre-conditions
    assert all(0 <= v <= 1 for v in features.values()), \
        "Features must be normalized"

    score = sum(features.values()) / len(features)

    # Post-conditions
    assert 0 <= score <= 1, f"Invalid score: {score}"

    return score
```

---

## 📚 Where to Find Answers

### Quick Lookup
```
Concept not clear?
  ↓
Check: PHASE_X_LEARNING_GUIDE.md

Want to see code?
  ↓
Check: File reference in guides

Need architecture overview?
  ↓
Check: PHASE_X_ARCHITECTURE.md

Want complete roadmap?
  ↓
Check: COMPLETE_LEARNING_ROADMAP.md

This cheat sheet?
  ↓
You're reading it! (QUICK_REFERENCE.md)
```

### Search Strategy
```python
# 1. Search for "# TRACE THIS:" comments in code
grep -r "# TRACE THIS:" python/agents/

# 2. Search for concept name
grep -r "Feature Engineering" *.md

# 3. Check table of contents
head -30 PHASE_*_LEARNING_GUIDE.md
```

---

## 🎯 Learning Strategy

### When Stuck
```
1. Read the concept explanation (learning guide)
2. Find "# TRACE THIS:" in code
3. Step through with debugger
4. Modify and experiment
5. Build mini version
6. Explain to someone (rubber duck)
```

### Daily Practice
```
- Morning: Read 1 new concept (30 min)
- Afternoon: Code implementation (2 hours)
- Evening: Review and document (30 min)

Weekly: Build project using week's concepts
Monthly: Review all concepts, fill gaps
```

---

## 💪 Final Tips

### DO:
✅ Read code, don't just skim
✅ Actually type examples (don't copy-paste)
✅ Break things and fix them
✅ Build your own variations
✅ Explain concepts out loud

### DON'T:
❌ Try to learn everything at once
❌ Skip the fundamentals
❌ Just watch tutorials
❌ Move on before understanding
❌ Code without thinking

---

## 🚀 Next Steps

**Right now:**
1. Pick ONE concept from top 10
2. Read that section in learning guide
3. Find "# TRACE THIS:" in code
4. Step through with debugger
5. Modify and experiment

**This week:**
- Master 2-3 concepts
- Build mini-project
- Document learnings

**This month:**
- Complete one phase
- Build portfolio project
- Write blog post

---

**Remember:** You learn by DOING, not reading!

Now close this file and start coding! 🔥
