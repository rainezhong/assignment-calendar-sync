#!/usr/bin/env python3
"""
Agent Memory and Learning System
Teaching concepts: Vector Databases, Machine Learning, Pattern Recognition, Caching
"""

import json
import sqlite3
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import logging
from collections import defaultdict, Counter

# For vector similarity (in production, use proper vector DB like Pinecone/Weaviate)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
except ImportError:
    print("Install scikit-learn: pip install scikit-learn")

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Vector Database Concepts
# Vector databases store high-dimensional vectors that represent semantic meaning
# This allows us to find similar patterns even when text varies

@dataclass
class NavigationPattern:
    """Represents a successful navigation pattern for learning"""
    platform: str                    # "gradescope", "blackboard", etc.
    goal: str                        # "login", "find_assignments", etc.
    page_context: str                # URL pattern or page identifier
    successful_steps: List[Dict]     # Steps that worked
    success_rate: float              # How often this pattern works
    confidence_score: float          # AI confidence in the pattern
    timestamp: datetime
    usage_count: int = 0
    avg_execution_time: float = 0.0

    def to_vector_text(self) -> str:
        """Convert pattern to text for vectorization"""
        steps_text = " ".join([
            f"{step.get('action', '')} {step.get('target', '')} {step.get('reasoning', '')}"
            for step in self.successful_steps
        ])
        return f"{self.platform} {self.goal} {self.page_context} {steps_text}"

@dataclass
class LearningContext:
    """Context for learning from navigation attempts"""
    platform: str
    url_pattern: str
    page_title: str
    page_elements: List[str]         # Key elements found on page
    screenshot_hash: str             # Hash of screenshot for visual similarity
    success: bool
    execution_time: float
    error_message: Optional[str] = None

class VectorMemoryStore:
    """
    Vector-based memory store for semantic pattern matching

    Teaching Concepts:
    - TF-IDF for text vectorization
    - Cosine similarity for pattern matching
    - Clustering for pattern discovery
    - Dimensionality reduction concepts
    """

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(exist_ok=True)

        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)  # Capture phrases like "click submit button"
        )

        self.patterns: List[NavigationPattern] = []
        self.pattern_vectors = None
        self.clusterer = KMeans(n_clusters=10, random_state=42)

        self.load_patterns()
        self._rebuild_vectors()

    def add_pattern(self, pattern: NavigationPattern) -> None:
        """Add a new successful pattern to memory"""
        # Check for duplicates or similar patterns
        similar_idx = self._find_similar_pattern(pattern)

        if similar_idx is not None:
            # Update existing pattern with new data
            existing = self.patterns[similar_idx]
            existing.usage_count += 1
            existing.success_rate = (existing.success_rate + pattern.success_rate) / 2
            existing.avg_execution_time = (
                existing.avg_execution_time + pattern.avg_execution_time
            ) / 2
            existing.timestamp = pattern.timestamp
        else:
            # Add as new pattern
            self.patterns.append(pattern)

        self._rebuild_vectors()
        self.save_patterns()

    def find_similar_patterns(self,
                            context: str,
                            platform: str = None,
                            goal: str = None,
                            top_k: int = 5) -> List[Tuple[NavigationPattern, float]]:
        """
        Find patterns similar to the given context using vector similarity

        This is the key innovation: instead of exact matching,
        we find semantically similar navigation contexts
        """
        if not self.patterns or self.pattern_vectors is None:
            return []

        # Vectorize the query context
        query_vector = self.vectorizer.transform([context])

        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.pattern_vectors)[0]

        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            pattern = self.patterns[idx]
            similarity_score = similarities[idx]

            # Apply filters if specified
            if platform and pattern.platform != platform:
                continue
            if goal and pattern.goal != goal:
                continue

            # Only return patterns with reasonable similarity
            if similarity_score > 0.1:  # Threshold for relevance
                results.append((pattern, similarity_score))

        return results

    def _find_similar_pattern(self, new_pattern: NavigationPattern) -> Optional[int]:
        """Find if a very similar pattern already exists"""
        new_text = new_pattern.to_vector_text()

        for i, existing in enumerate(self.patterns):
            if (existing.platform == new_pattern.platform and
                existing.goal == new_pattern.goal):

                existing_text = existing.to_vector_text()

                # Simple similarity check (in production, use proper vector similarity)
                if len(set(new_text.split()) & set(existing_text.split())) > 5:
                    return i

        return None

    def _rebuild_vectors(self) -> None:
        """Rebuild the vector representation of all patterns"""
        if not self.patterns:
            return

        pattern_texts = [p.to_vector_text() for p in self.patterns]
        self.pattern_vectors = self.vectorizer.fit_transform(pattern_texts)

        # Perform clustering to discover pattern families
        if len(self.patterns) >= 10:
            cluster_labels = self.clusterer.fit_predict(self.pattern_vectors.toarray())
            logger.info(f"Discovered {len(set(cluster_labels))} pattern clusters")

    def get_platform_statistics(self) -> Dict[str, Dict]:
        """Get learning statistics by platform"""
        platform_stats = defaultdict(lambda: {
            'total_patterns': 0,
            'avg_success_rate': 0.0,
            'most_common_goals': Counter(),
            'avg_execution_time': 0.0
        })

        for pattern in self.patterns:
            stats = platform_stats[pattern.platform]
            stats['total_patterns'] += 1
            stats['avg_success_rate'] += pattern.success_rate
            stats['most_common_goals'][pattern.goal] += 1
            stats['avg_execution_time'] += pattern.avg_execution_time

        # Calculate averages
        for platform, stats in platform_stats.items():
            count = stats['total_patterns']
            stats['avg_success_rate'] /= count
            stats['avg_execution_time'] /= count

        return dict(platform_stats)

    def save_patterns(self) -> None:
        """Persist patterns to disk"""
        patterns_file = self.memory_dir / "navigation_patterns.pkl"
        with open(patterns_file, 'wb') as f:
            pickle.dump(self.patterns, f)

    def load_patterns(self) -> None:
        """Load patterns from disk"""
        patterns_file = self.memory_dir / "navigation_patterns.pkl"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'rb') as f:
                    self.patterns = pickle.load(f)
                logger.info(f"Loaded {len(self.patterns)} navigation patterns")
            except Exception as e:
                logger.error(f"Failed to load patterns: {e}")
                self.patterns = []

# LEARNING CONCEPT 2: Adaptive Learning System
# This system learns which strategies work best for different scenarios
# and adapts its approach based on historical success

class AdaptiveLearningEngine:
    """
    Machine learning engine that improves agent performance over time

    Teaching Concepts:
    - Reinforcement learning principles
    - Performance optimization
    - Statistical analysis of success patterns
    - Automated strategy selection
    """

    def __init__(self, memory_store: VectorMemoryStore):
        self.memory_store = memory_store
        self.success_db = self._init_success_database()

    def _init_success_database(self) -> sqlite3.Connection:
        """Initialize SQLite database for tracking execution results"""
        db_path = self.memory_store.memory_dir / "learning_results.db"
        conn = sqlite3.connect(str(db_path))

        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_results (
                id INTEGER PRIMARY KEY,
                platform TEXT,
                goal TEXT,
                strategy_hash TEXT,
                success BOOLEAN,
                execution_time REAL,
                error_type TEXT,
                timestamp DATETIME,
                page_url TEXT,
                confidence_score REAL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                strategy_hash TEXT PRIMARY KEY,
                total_attempts INTEGER,
                successful_attempts INTEGER,
                avg_execution_time REAL,
                success_rate REAL,
                last_updated DATETIME
            )
        """)

        conn.commit()
        return conn

    def record_execution_result(self,
                              platform: str,
                              goal: str,
                              navigation_steps: List[Dict],
                              success: bool,
                              execution_time: float,
                              context: LearningContext) -> None:
        """Record the result of a navigation attempt for learning"""

        # Create a hash of the strategy used
        strategy_text = json.dumps(navigation_steps, sort_keys=True)
        strategy_hash = hashlib.md5(strategy_text.encode()).hexdigest()

        # Record individual execution
        self.success_db.execute("""
            INSERT INTO execution_results
            (platform, goal, strategy_hash, success, execution_time, error_type, timestamp, page_url, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            platform, goal, strategy_hash, success, execution_time,
            context.error_message, datetime.now(), context.url_pattern, 0.8
        ))

        # Update strategy performance
        self._update_strategy_performance(strategy_hash, success, execution_time)

        # If successful, add to pattern memory
        if success:
            pattern = NavigationPattern(
                platform=platform,
                goal=goal,
                page_context=context.url_pattern,
                successful_steps=navigation_steps,
                success_rate=self._calculate_strategy_success_rate(strategy_hash),
                confidence_score=0.8,
                timestamp=datetime.now(),
                usage_count=1,
                avg_execution_time=execution_time
            )
            self.memory_store.add_pattern(pattern)

        self.success_db.commit()

    def _update_strategy_performance(self, strategy_hash: str, success: bool, execution_time: float) -> None:
        """Update the performance metrics for a strategy"""
        cursor = self.success_db.execute(
            "SELECT total_attempts, successful_attempts, avg_execution_time FROM strategy_performance WHERE strategy_hash = ?",
            (strategy_hash,)
        )
        result = cursor.fetchone()

        if result:
            total, successful, avg_time = result
            new_total = total + 1
            new_successful = successful + (1 if success else 0)
            new_avg_time = (avg_time * total + execution_time) / new_total
            success_rate = new_successful / new_total

            self.success_db.execute("""
                UPDATE strategy_performance
                SET total_attempts = ?, successful_attempts = ?, avg_execution_time = ?,
                    success_rate = ?, last_updated = ?
                WHERE strategy_hash = ?
            """, (new_total, new_successful, new_avg_time, success_rate, datetime.now(), strategy_hash))
        else:
            # First time seeing this strategy
            success_rate = 1.0 if success else 0.0
            self.success_db.execute("""
                INSERT INTO strategy_performance
                (strategy_hash, total_attempts, successful_attempts, avg_execution_time, success_rate, last_updated)
                VALUES (?, 1, ?, ?, ?, ?)
            """, (strategy_hash, 1 if success else 0, execution_time, success_rate, datetime.now()))

    def _calculate_strategy_success_rate(self, strategy_hash: str) -> float:
        """Calculate current success rate for a strategy"""
        cursor = self.success_db.execute(
            "SELECT success_rate FROM strategy_performance WHERE strategy_hash = ?",
            (strategy_hash,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0.0

    def get_optimal_strategy(self, platform: str, goal: str, context: str) -> Optional[NavigationPattern]:
        """
        Get the optimal navigation strategy based on learning history

        This demonstrates how AI systems can optimize themselves:
        1. Find similar past contexts
        2. Rank by success rate and recency
        3. Return the most promising approach
        """

        # Get similar patterns from vector memory
        similar_patterns = self.memory_store.find_similar_patterns(
            context=context,
            platform=platform,
            goal=goal,
            top_k=10
        )

        if not similar_patterns:
            return None

        # Score patterns based on multiple factors
        scored_patterns = []
        for pattern, similarity in similar_patterns:
            # Calculate recency bonus (more recent = better)
            days_old = (datetime.now() - pattern.timestamp).days
            recency_score = max(0.1, 1.0 - (days_old / 30))  # Decay over 30 days

            # Calculate usage bonus (more used = more reliable)
            usage_score = min(1.0, pattern.usage_count / 10)  # Cap at 10 uses

            # Combine factors
            composite_score = (
                pattern.success_rate * 0.4 +      # Success rate most important
                similarity * 0.3 +                # Similarity to current context
                recency_score * 0.2 +            # How recent the pattern is
                usage_score * 0.1                # How well-tested it is
            )

            scored_patterns.append((pattern, composite_score))

        # Return the best scoring pattern
        if scored_patterns:
            best_pattern, score = max(scored_patterns, key=lambda x: x[1])
            logger.info(f"Selected strategy with score {score:.3f} for {platform}/{goal}")
            return best_pattern

        return None

    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate a comprehensive learning report"""
        platform_stats = self.memory_store.get_platform_statistics()

        # Get overall success trends
        cursor = self.success_db.execute("""
            SELECT DATE(timestamp) as date,
                   COUNT(*) as attempts,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
            FROM execution_results
            WHERE timestamp > DATE('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        """)
        daily_stats = cursor.fetchall()

        # Get top performing strategies
        cursor = self.success_db.execute("""
            SELECT strategy_hash, success_rate, total_attempts
            FROM strategy_performance
            WHERE total_attempts >= 3
            ORDER BY success_rate DESC, total_attempts DESC
            LIMIT 10
        """)
        top_strategies = cursor.fetchall()

        return {
            'platform_statistics': platform_stats,
            'daily_performance': daily_stats,
            'top_strategies': top_strategies,
            'total_patterns_learned': len(self.memory_store.patterns),
            'learning_span_days': self._get_learning_span_days(),
            'improvement_trend': self._calculate_improvement_trend()
        }

    def _get_learning_span_days(self) -> int:
        """Calculate how many days we've been learning"""
        if not self.memory_store.patterns:
            return 0

        oldest = min(p.timestamp for p in self.memory_store.patterns)
        return (datetime.now() - oldest).days

    def _calculate_improvement_trend(self) -> float:
        """Calculate if success rates are improving over time"""
        cursor = self.success_db.execute("""
            SELECT timestamp, success
            FROM execution_results
            ORDER BY timestamp
        """)
        results = cursor.fetchall()

        if len(results) < 10:
            return 0.0

        # Compare recent performance to earlier performance
        midpoint = len(results) // 2
        early_results = results[:midpoint]
        recent_results = results[midpoint:]

        early_success_rate = sum(1 for _, success in early_results if success) / len(early_results)
        recent_success_rate = sum(1 for _, success in recent_results if success) / len(recent_results)

        return recent_success_rate - early_success_rate  # Positive = improving

# LEARNING CONCEPT 3: Integration with Agent Architecture
# This shows how to integrate learning into the existing agent system

class LearningAwareAgent:
    """
    Wrapper that adds learning capabilities to any BaseLMSAgent

    Teaching Concepts:
    - Decorator pattern for adding functionality
    - Aspect-oriented programming
    - Performance monitoring and optimization
    - Data-driven decision making
    """

    def __init__(self, base_agent, memory_dir: Path = None):
        self.base_agent = base_agent

        if memory_dir is None:
            memory_dir = Path.home() / ".academic_assistant" / "agent_memory"

        self.memory_store = VectorMemoryStore(memory_dir)
        self.learning_engine = AdaptiveLearningEngine(self.memory_store)

    async def navigate_with_learning(self, goal: str, context: str) -> bool:
        """Navigate using learned patterns, falling back to AI if needed"""
        start_time = datetime.now()

        # Try to use learned pattern first
        optimal_strategy = self.learning_engine.get_optimal_strategy(
            platform=self.base_agent.__class__.__name__.lower().replace('agent', ''),
            goal=goal,
            context=context
        )

        success = False
        steps_used = []

        if optimal_strategy:
            logger.info(f"Using learned strategy for {goal}")
            # Execute the learned pattern
            success = await self._execute_learned_pattern(optimal_strategy)
            steps_used = optimal_strategy.successful_steps

        if not success:
            logger.info(f"Learned strategy failed or not available, using AI navigation")
            # Fall back to AI-powered navigation
            if hasattr(self.base_agent, 'analyze_page_for_navigation'):
                nav_plan = await self.base_agent.analyze_page_for_navigation(goal)
                success = await self.base_agent.execute_navigation_plan(nav_plan)
                steps_used = nav_plan.steps

        # Record the result for learning
        execution_time = (datetime.now() - start_time).total_seconds()
        learning_context = LearningContext(
            platform=self.base_agent.__class__.__name__.lower().replace('agent', ''),
            url_pattern=context,
            page_title=goal,
            page_elements=[],
            screenshot_hash="",
            success=success,
            execution_time=execution_time
        )

        self.learning_engine.record_execution_result(
            platform=learning_context.platform,
            goal=goal,
            navigation_steps=steps_used,
            success=success,
            execution_time=execution_time,
            context=learning_context
        )

        return success

    async def _execute_learned_pattern(self, pattern: NavigationPattern) -> bool:
        """Execute a previously learned navigation pattern"""
        try:
            for step in pattern.successful_steps:
                # Execute each step from the learned pattern
                success = await self.base_agent._execute_single_step(step)
                if not success:
                    return False

                # Wait between steps
                if hasattr(self.base_agent, 'page'):
                    await self.base_agent.page.wait_for_timeout(1000)

            return True
        except Exception as e:
            logger.error(f"Failed to execute learned pattern: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    print("🧠 Agent Memory and Learning System")
    print("=" * 50)
    print()
    print("Key Concepts Demonstrated:")
    print("1. Vector Databases and Semantic Search")
    print("2. Machine Learning for Strategy Optimization")
    print("3. Reinforcement Learning Principles")
    print("4. Performance Analysis and Reporting")
    print("5. Adaptive System Architecture")
    print()
    print("This system enables agents to:")
    print("✅ Remember successful navigation patterns")
    print("✅ Learn from failures and adapt")
    print("✅ Share knowledge between platform agents")
    print("✅ Optimize performance over time")
    print("✅ Reduce dependency on AI API calls")
    print("✅ Generate insights about platform changes")
    print()
    print("Learning Architecture:")
    print("📊 Vector similarity for pattern matching")
    print("🎯 Multi-factor strategy scoring")
    print("📈 Performance trend analysis")
    print("🔄 Continuous improvement feedback loop")