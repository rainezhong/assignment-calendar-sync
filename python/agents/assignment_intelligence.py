#!/usr/bin/env python3
"""
Assignment Intelligence - Deep Analysis System
Teaching concepts: NLP Analysis, Skill Extraction, Semantic Similarity, Resource Recommendation
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
from collections import Counter, defaultdict
import hashlib

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Natural Language Processing for Education
# Extract structured information from unstructured assignment text
# This is key to building intelligent academic assistants

@dataclass
class ComplexityAnalysis:
    """
    Multi-dimensional complexity assessment

    Teaching Concepts:
    - Multi-dimensional feature analysis
    - Composite scoring
    - Explainable AI (show reasoning)
    """
    overall_score: float  # 0-1 scale
    cognitive_level: str  # bloom's taxonomy: remember, understand, apply, analyze, evaluate, create
    technical_depth: float  # 0-1: how technical/specialized
    scope: str  # small, medium, large, very_large
    ambiguity: float  # 0-1: how clear are requirements
    estimated_hours: float

    # Breakdown for explainability
    factors: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""

    # Confidence in analysis
    confidence: float = 0.7

    @property
    def difficulty_level(self) -> str:
        """Human-readable difficulty"""
        if self.overall_score < 0.2:
            return "trivial"
        elif self.overall_score < 0.4:
            return "easy"
        elif self.overall_score < 0.6:
            return "moderate"
        elif self.overall_score < 0.8:
            return "hard"
        else:
            return "very_hard"

@dataclass
class SkillRequirement:
    """
    Individual skill needed for assignment

    Teaching Concepts:
    - Skill taxonomy
    - Prerequisite detection
    - Learning path construction
    """
    skill_name: str
    category: str  # technical, writing, research, analytical, creative, collaborative
    proficiency_needed: str  # beginner, intermediate, advanced, expert
    is_prerequisite: bool  # Must know before starting?
    learning_resources: List[str] = field(default_factory=list)
    estimated_learning_time: Optional[timedelta] = None

@dataclass
class AssignmentAnalysis:
    """
    Complete assignment intelligence

    This is the output of deep analysis - everything you need to know
    """
    assignment_id: str
    assignment_text: str

    # Complexity assessment
    complexity: ComplexityAnalysis

    # Skills analysis
    skills_needed: List[SkillRequirement]
    missing_skills: List[SkillRequirement] = field(default_factory=list)

    # Historical context
    similar_past_assignments: List[Dict[str, Any]] = field(default_factory=list)
    success_rate_for_similar: float = 0.0

    # Time predictions
    time_estimate: timedelta = field(default_factory=lambda: timedelta(hours=5))
    time_estimate_range: Tuple[float, float] = (3.0, 7.0)  # min, max hours

    # Resources
    recommended_resources: List[Dict[str, str]] = field(default_factory=list)
    relevant_course_materials: List[str] = field(default_factory=list)

    # Strategic advice
    suggested_approach: List[str] = field(default_factory=list)
    potential_pitfalls: List[str] = field(default_factory=list)
    optimization_tips: List[str] = field(default_factory=list)

    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    analysis_confidence: float = 0.7

# LEARNING CONCEPT 2: Bloom's Taxonomy for Cognitive Level Detection
# Educational framework for classifying learning objectives

class BloomsTaxonomyAnalyzer:
    """
    Classify assignments by cognitive level using Bloom's Taxonomy

    Teaching Concepts:
    - Educational theory in code
    - Hierarchical classification
    - Keyword-based + AI classification
    """

    # Bloom's Taxonomy levels (from simple to complex)
    TAXONOMY_LEVELS = [
        "remember",    # Recall facts
        "understand",  # Explain ideas
        "apply",       # Use knowledge in new situations
        "analyze",     # Break down information
        "evaluate",    # Justify decisions
        "create"       # Produce original work
    ]

    # Keywords for each level
    LEVEL_KEYWORDS = {
        "remember": [
            "define", "list", "recall", "identify", "name", "state",
            "describe", "recognize", "select", "match", "label"
        ],
        "understand": [
            "explain", "summarize", "paraphrase", "interpret", "discuss",
            "describe", "classify", "compare", "contrast", "illustrate"
        ],
        "apply": [
            "implement", "use", "execute", "apply", "solve", "demonstrate",
            "calculate", "complete", "construct", "modify", "operate"
        ],
        "analyze": [
            "analyze", "examine", "investigate", "categorize", "compare",
            "contrast", "differentiate", "organize", "deconstruct", "attribute"
        ],
        "evaluate": [
            "evaluate", "assess", "judge", "critique", "justify", "argue",
            "defend", "prioritize", "rate", "select", "support", "recommend"
        ],
        "create": [
            "create", "design", "develop", "compose", "construct", "formulate",
            "generate", "plan", "produce", "invent", "devise", "build"
        ]
    }

    def classify_cognitive_level(self, assignment_text: str) -> Tuple[str, float]:
        """
        Determine cognitive level from assignment text

        LEARNING CONCEPT: Multi-strategy classification
        1. Keyword matching (fast, reliable for clear text)
        2. Contextual analysis (for ambiguous cases)
        """
        text_lower = assignment_text.lower()
        level_scores = Counter()

        # Count keywords for each level
        for level, keywords in self.LEVEL_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                level_scores[level] += matches

        if not level_scores:
            return "understand", 0.3  # Default with low confidence

        # Get highest scoring level
        top_level = level_scores.most_common(1)[0][0]
        total_matches = sum(level_scores.values())
        confidence = min(1.0, level_scores[top_level] / max(total_matches, 1))

        return top_level, confidence

    def get_complexity_score(self, cognitive_level: str) -> float:
        """
        Map cognitive level to complexity score (0-1)

        Higher levels = more complex
        """
        try:
            level_index = self.TAXONOMY_LEVELS.index(cognitive_level)
            return level_index / (len(self.TAXONOMY_LEVELS) - 1)
        except ValueError:
            return 0.5  # Default

# LEARNING CONCEPT 3: Semantic Similarity for Finding Similar Assignments
# Use embeddings to find similar past assignments (even with different words)

class AssignmentSimilarityEngine:
    """
    Find similar past assignments using semantic similarity

    Teaching Concepts:
    - Text embeddings
    - Cosine similarity
    - Semantic search
    """

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.past_assignments = self._load_past_assignments()

    def _load_past_assignments(self) -> List[Dict[str, Any]]:
        """Load historical assignments"""
        history_file = self.storage_dir / "assignment_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load assignment history: {e}")
        return []

    def find_similar_assignments(self,
                                current_assignment: Dict[str, Any],
                                limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar past assignments

        LEARNING CONCEPT: Feature-based similarity
        Since we don't have embeddings, use feature overlap
        In production, use sentence-transformers or OpenAI embeddings
        """
        if not self.past_assignments:
            return []

        current_text = f"{current_assignment.get('title', '')} {current_assignment.get('description', '')}"
        current_features = self._extract_features(current_text, current_assignment)

        similarities = []

        for past in self.past_assignments:
            past_text = f"{past.get('title', '')} {past.get('description', '')}"
            past_features = self._extract_features(past_text, past)

            # Calculate similarity score
            similarity = self._calculate_similarity(current_features, past_features)

            similarities.append({
                'assignment': past,
                'similarity': similarity
            })

        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:limit]

    def _extract_features(self, text: str, assignment: Dict) -> Dict[str, Any]:
        """
        Extract features for similarity comparison

        LEARNING CONCEPT: Feature extraction for similarity
        """
        text_lower = text.lower()

        return {
            'course': assignment.get('course', ''),
            'type': assignment.get('type', ''),
            'word_count': len(text.split()),
            'keywords': self._extract_keywords(text_lower),
            'has_code': 'code' in text_lower or 'implement' in text_lower,
            'has_writing': 'essay' in text_lower or 'paper' in text_lower or 'write' in text_lower,
            'has_research': 'research' in text_lower or 'sources' in text_lower,
            'points': assignment.get('points_possible', 100)
        }

    def _extract_keywords(self, text: str) -> set:
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}

        words = re.findall(r'\b[a-z]{4,}\b', text)  # Words 4+ chars
        keywords = set(w for w in words if w not in stop_words)

        return keywords

    def _calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate similarity score between two feature sets

        LEARNING CONCEPT: Multi-factor similarity
        Combine multiple similarity measures
        """
        score = 0.0

        # Same course: +0.3
        if features1['course'] == features2['course'] and features1['course']:
            score += 0.3

        # Same type: +0.2
        if features1['type'] == features2['type'] and features1['type']:
            score += 0.2

        # Keyword overlap: +0.3
        keywords1 = features1['keywords']
        keywords2 = features2['keywords']
        if keywords1 and keywords2:
            overlap = len(keywords1 & keywords2)
            total = len(keywords1 | keywords2)
            keyword_similarity = overlap / max(total, 1)
            score += keyword_similarity * 0.3

        # Similar characteristics: +0.2
        char_matches = 0
        if features1['has_code'] == features2['has_code']:
            char_matches += 1
        if features1['has_writing'] == features2['has_writing']:
            char_matches += 1
        if features1['has_research'] == features2['has_research']:
            char_matches += 1
        score += (char_matches / 3) * 0.2

        return min(1.0, score)

    def record_assignment_outcome(self,
                                 assignment: Dict[str, Any],
                                 actual_hours: float,
                                 grade: Optional[float] = None,
                                 difficulty: Optional[str] = None):
        """
        Record assignment outcome for future similarity matching

        LEARNING CONCEPT: Learning from outcomes
        """
        assignment_record = {
            'id': hashlib.md5(f"{assignment.get('title', '')}{datetime.now()}".encode()).hexdigest(),
            'title': assignment.get('title', ''),
            'description': assignment.get('description', ''),
            'course': assignment.get('course', ''),
            'type': assignment.get('type', ''),
            'points_possible': assignment.get('points_possible', 100),
            'actual_hours': actual_hours,
            'grade': grade,
            'difficulty': difficulty,
            'completed_at': datetime.now().isoformat()
        }

        self.past_assignments.append(assignment_record)

        # Save to disk
        history_file = self.storage_dir / "assignment_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.past_assignments, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save assignment history: {e}")

# LEARNING CONCEPT 4: AI-Powered Resource Recommendation
# Use LLMs to suggest relevant learning resources

class ResourceRecommender:
    """
    Recommend learning resources for assignments

    Teaching Concepts:
    - Retrieval-Augmented Generation (RAG)
    - Knowledge base integration
    - Personalized recommendations
    """

    def __init__(self, ai_client):
        self.ai_client = ai_client

    async def suggest_resources(self,
                               assignment: Dict[str, Any],
                               skills_needed: List[SkillRequirement]) -> List[Dict[str, str]]:
        """
        Suggest learning resources using AI

        LEARNING CONCEPT: Prompt engineering for recommendations
        """
        # Build context
        skills_list = "\n".join([
            f"- {skill.skill_name} ({skill.proficiency_needed} level)"
            for skill in skills_needed
        ])

        recommendation_prompt = f"""
You are an academic advisor helping a student find resources for an assignment.

ASSIGNMENT:
Title: {assignment.get('title', 'Unknown')}
Course: {assignment.get('course', 'Unknown')}
Description: {assignment.get('description', '')[:500]}

SKILLS NEEDED:
{skills_list}

TASK:
Recommend 5-8 high-quality learning resources to help with this assignment.

For each resource, provide:
1. Resource name/title
2. Type (tutorial, documentation, video, book, article, tool)
3. URL (if applicable) or "Search for: [search query]"
4. Why it's relevant (1 sentence)
5. Estimated time to complete/read

OUTPUT FORMAT (JSON):
{{
    "resources": [
        {{
            "name": "Resource name",
            "type": "tutorial|documentation|video|book|article|tool",
            "url": "URL or search query",
            "relevance": "Why this helps",
            "time_minutes": 30
        }}
    ],
    "learning_path": "Suggested order to use these resources",
    "quick_start_tip": "Best resource to start with immediately"
}}

IMPORTANT:
- Prioritize free, accessible resources
- Include both beginner and advanced resources
- Suggest specific tools if the assignment requires coding
- Include official documentation when relevant
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=recommendation_prompt,
                response_format="json"
            )

            recommendations = json.loads(response)
            logger.info(f"Generated {len(recommendations.get('resources', []))} resource recommendations")
            return recommendations.get('resources', [])

        except Exception as e:
            logger.error(f"Resource recommendation failed: {e}")
            return self._fallback_recommendations(assignment)

    def _fallback_recommendations(self, assignment: Dict[str, Any]) -> List[Dict[str, str]]:
        """Fallback recommendations when AI fails"""
        course = assignment.get('course', '').upper()
        assignment_type = assignment.get('type', 'assignment')

        # Generic but useful recommendations
        recommendations = [
            {
                'name': f"{course} Course Materials",
                'type': 'documentation',
                'url': f"Search for: {course} syllabus and lecture notes",
                'relevance': "Official course materials are the primary resource",
                'time_minutes': 30
            },
            {
                'name': "Office Hours",
                'type': 'help',
                'url': "Check course website for office hours schedule",
                'relevance': "Get personalized help from instructor or TAs",
                'time_minutes': 30
            }
        ]

        return recommendations

# Main Assignment Intelligence class
class AssignmentIntelligence:
    """
    Complete assignment analysis and intelligence system

    Orchestrates:
    - Complexity analysis
    - Skill extraction
    - Similarity search
    - Resource recommendation
    - Strategic advice generation
    """

    def __init__(self, ai_client, storage_dir: Path = None):
        self.ai_client = ai_client

        if storage_dir is None:
            storage_dir = Path.home() / ".academic_assistant" / "assignment_intelligence"
        storage_dir.mkdir(parents=True, exist_ok=True)

        self.storage_dir = storage_dir
        self.blooms_analyzer = BloomsTaxonomyAnalyzer()
        self.similarity_engine = AssignmentSimilarityEngine(storage_dir)
        self.resource_recommender = ResourceRecommender(ai_client)

    async def analyze_assignment(self, assignment: Dict[str, Any]) -> AssignmentAnalysis:
        """
        Perform comprehensive assignment analysis

        This is the main entry point - returns everything you need to know
        """
        assignment_text = f"{assignment.get('title', '')} {assignment.get('description', '')}"
        assignment_id = assignment.get('id', hashlib.md5(assignment_text.encode()).hexdigest())

        logger.info(f"Starting deep analysis of assignment: {assignment.get('title', 'Unknown')}")

        # STEP 1: Analyze complexity
        complexity = await self._estimate_workload(assignment_text, assignment)

        # STEP 2: Identify required skills
        skills_needed = await self._identify_requirements(assignment_text, assignment)

        # STEP 3: Find similar past assignments
        similar_assignments = self.similarity_engine.find_similar_assignments(assignment)

        # STEP 4: Calculate time estimate from similar assignments
        time_estimate, time_range = self._predict_completion_time(assignment, similar_assignments, complexity)

        # STEP 5: Recommend resources
        resources = await self._suggest_helpful_resources(assignment, skills_needed)

        # STEP 6: Generate strategic advice
        approach, pitfalls, tips = await self._generate_strategic_advice(assignment, complexity, skills_needed)

        # Create complete analysis
        analysis = AssignmentAnalysis(
            assignment_id=assignment_id,
            assignment_text=assignment_text,
            complexity=complexity,
            skills_needed=skills_needed,
            similar_past_assignments=similar_assignments,
            success_rate_for_similar=self._calculate_success_rate(similar_assignments),
            time_estimate=time_estimate,
            time_estimate_range=time_range,
            recommended_resources=resources,
            suggested_approach=approach,
            potential_pitfalls=pitfalls,
            optimization_tips=tips,
            analysis_confidence=self._calculate_overall_confidence(complexity, skills_needed)
        )

        logger.info(f"Analysis complete: {complexity.difficulty_level} difficulty, {time_estimate.total_seconds()/3600:.1f}h estimated")
        return analysis

    async def _estimate_workload(self, assignment_text: str, assignment: Dict) -> ComplexityAnalysis:
        """
        Estimate assignment complexity and workload

        LEARNING CONCEPT: Multi-dimensional complexity analysis
        """
        # Get cognitive level
        cognitive_level, cog_confidence = self.blooms_analyzer.classify_cognitive_level(assignment_text)
        cognitive_score = self.blooms_analyzer.get_complexity_score(cognitive_level)

        # Use AI for deep analysis
        complexity_prompt = f"""
Analyze this assignment's complexity on multiple dimensions.

ASSIGNMENT:
{assignment_text[:1000]}

Type: {assignment.get('type', 'unknown')}
Course: {assignment.get('course', 'unknown')}
Points: {assignment.get('points_possible', 'unknown')}

ANALYZE:
1. Technical depth (0-1): How much specialized knowledge is needed?
2. Scope (small/medium/large/very_large): How much work is there?
3. Ambiguity (0-1): How clear are the requirements?
4. Innovation required (0-1): How much original thinking is needed?

OUTPUT (JSON):
{{
    "technical_depth": 0.0-1.0,
    "scope": "small|medium|large|very_large",
    "ambiguity": 0.0-1.0,
    "innovation_required": 0.0-1.0,
    "estimated_hours": number,
    "reasoning": "Brief explanation of assessment"
}}
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=complexity_prompt,
                response_format="json"
            )

            ai_analysis = json.loads(response)

            # Combine multiple factors
            factors = {
                'cognitive_level': cognitive_score,
                'technical_depth': ai_analysis.get('technical_depth', 0.5),
                'scope': self._scope_to_score(ai_analysis.get('scope', 'medium')),
                'ambiguity': ai_analysis.get('ambiguity', 0.3),
                'innovation': ai_analysis.get('innovation_required', 0.5)
            }

            # Weighted average
            overall_score = (
                factors['cognitive_level'] * 0.25 +
                factors['technical_depth'] * 0.25 +
                factors['scope'] * 0.30 +
                factors['innovation'] * 0.20
            )

            complexity = ComplexityAnalysis(
                overall_score=overall_score,
                cognitive_level=cognitive_level,
                technical_depth=factors['technical_depth'],
                scope=ai_analysis.get('scope', 'medium'),
                ambiguity=factors['ambiguity'],
                estimated_hours=ai_analysis.get('estimated_hours', 5.0),
                factors=factors,
                reasoning=ai_analysis.get('reasoning', ''),
                confidence=min(cog_confidence, 0.8)
            )

            return complexity

        except Exception as e:
            logger.error(f"AI complexity analysis failed: {e}")
            return self._fallback_complexity_estimate(assignment_text, assignment)

    def _scope_to_score(self, scope: str) -> float:
        """Convert scope string to numeric score"""
        scope_map = {
            'small': 0.2,
            'medium': 0.5,
            'large': 0.8,
            'very_large': 1.0
        }
        return scope_map.get(scope.lower(), 0.5)

    def _fallback_complexity_estimate(self, text: str, assignment: Dict) -> ComplexityAnalysis:
        """Simple heuristic fallback"""
        word_count = len(text.split())
        type_complexity = {
            'quiz': 0.2,
            'homework': 0.4,
            'essay': 0.6,
            'project': 0.8,
            'exam': 0.7
        }

        assignment_type = assignment.get('type', 'homework')
        base_score = type_complexity.get(assignment_type, 0.5)

        # Adjust for length
        if word_count > 500:
            base_score = min(1.0, base_score + 0.2)

        return ComplexityAnalysis(
            overall_score=base_score,
            cognitive_level="apply",
            technical_depth=0.5,
            scope="medium",
            ambiguity=0.3,
            estimated_hours=5.0,
            reasoning="Heuristic estimate (AI analysis unavailable)"
        )

    async def _identify_requirements(self, text: str, assignment: Dict) -> List[SkillRequirement]:
        """
        Extract skills needed for assignment

        LEARNING CONCEPT: Skill taxonomy and extraction
        """
        skills_prompt = f"""
Identify the specific skills needed to complete this assignment.

ASSIGNMENT:
{text[:800]}

Course: {assignment.get('course', 'Unknown')}
Type: {assignment.get('type', 'Unknown')}

EXTRACT skills in these categories:
- Technical (programming, tools, platforms)
- Writing (composition, grammar, citation)
- Research (finding sources, analysis)
- Analytical (data analysis, critical thinking)
- Creative (design, innovation)
- Collaborative (teamwork, communication)

For each skill, specify:
- Proficiency needed (beginner/intermediate/advanced/expert)
- Is it a prerequisite (must know before starting)?

OUTPUT (JSON):
{{
    "skills": [
        {{
            "skill_name": "Specific skill",
            "category": "technical|writing|research|analytical|creative|collaborative",
            "proficiency_needed": "beginner|intermediate|advanced|expert",
            "is_prerequisite": true/false
        }}
    ]
}}
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=skills_prompt,
                response_format="json"
            )

            skills_data = json.loads(response)
            skills = []

            for skill_dict in skills_data.get('skills', []):
                skill = SkillRequirement(
                    skill_name=skill_dict['skill_name'],
                    category=skill_dict['category'],
                    proficiency_needed=skill_dict['proficiency_needed'],
                    is_prerequisite=skill_dict.get('is_prerequisite', False)
                )
                skills.append(skill)

            logger.info(f"Identified {len(skills)} skills needed")
            return skills

        except Exception as e:
            logger.error(f"Skill identification failed: {e}")
            return self._fallback_skill_identification(text, assignment)

    def _fallback_skill_identification(self, text: str, assignment: Dict) -> List[SkillRequirement]:
        """Simple keyword-based skill detection"""
        text_lower = text.lower()
        skills = []

        # Technical skills
        if any(word in text_lower for word in ['code', 'program', 'implement', 'develop']):
            skills.append(SkillRequirement(
                skill_name="Programming",
                category="technical",
                proficiency_needed="intermediate",
                is_prerequisite=True
            ))

        # Writing skills
        if any(word in text_lower for word in ['write', 'essay', 'paper', 'report']):
            skills.append(SkillRequirement(
                skill_name="Academic Writing",
                category="writing",
                proficiency_needed="intermediate",
                is_prerequisite=False
            ))

        # Research skills
        if any(word in text_lower for word in ['research', 'sources', 'references', 'citations']):
            skills.append(SkillRequirement(
                skill_name="Research",
                category="research",
                proficiency_needed="intermediate",
                is_prerequisite=False
            ))

        return skills

    def _predict_completion_time(self,
                                assignment: Dict,
                                similar_assignments: List[Dict],
                                complexity: ComplexityAnalysis) -> Tuple[timedelta, Tuple[float, float]]:
        """
        Predict completion time using multiple sources

        LEARNING CONCEPT: Ensemble prediction
        Combine complexity estimate + historical data
        """
        # Start with complexity-based estimate
        base_hours = complexity.estimated_hours

        # Adjust based on similar assignments
        if similar_assignments:
            similar_hours = []
            for sim in similar_assignments:
                if sim['assignment'].get('actual_hours'):
                    similar_hours.append(sim['assignment']['actual_hours'])

            if similar_hours:
                avg_similar = sum(similar_hours) / len(similar_hours)
                # Blend estimates: 60% complexity, 40% historical
                base_hours = (base_hours * 0.6) + (avg_similar * 0.4)

        # Calculate range (±30%)
        min_hours = base_hours * 0.7
        max_hours = base_hours * 1.3

        return timedelta(hours=base_hours), (min_hours, max_hours)

    async def _suggest_helpful_resources(self,
                                        assignment: Dict,
                                        skills: List[SkillRequirement]) -> List[Dict[str, str]]:
        """Get resource recommendations"""
        return await self.resource_recommender.suggest_resources(assignment, skills)

    async def _generate_strategic_advice(self,
                                        assignment: Dict,
                                        complexity: ComplexityAnalysis,
                                        skills: List[SkillRequirement]) -> Tuple[List[str], List[str], List[str]]:
        """
        Generate strategic advice for completing assignment

        Returns: (approach, pitfalls, optimization_tips)
        """
        advice_prompt = f"""
Provide strategic advice for completing this assignment successfully.

ASSIGNMENT:
Title: {assignment.get('title', 'Unknown')}
Type: {assignment.get('type', 'Unknown')}
Difficulty: {complexity.difficulty_level}
Cognitive Level: {complexity.cognitive_level}
Estimated Hours: {complexity.estimated_hours}

SKILLS NEEDED:
{', '.join([s.skill_name for s in skills[:5]])}

GENERATE:
1. Suggested Approach (3-5 steps): How to tackle this assignment
2. Potential Pitfalls (2-4 items): Common mistakes to avoid
3. Optimization Tips (2-4 items): How to work more efficiently

OUTPUT (JSON):
{{
    "approach": ["Step 1", "Step 2", ...],
    "pitfalls": ["Pitfall 1", "Pitfall 2", ...],
    "optimization_tips": ["Tip 1", "Tip 2", ...]
}}
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=advice_prompt,
                response_format="json"
            )

            advice = json.loads(response)
            return (
                advice.get('approach', []),
                advice.get('pitfalls', []),
                advice.get('optimization_tips', [])
            )

        except Exception as e:
            logger.error(f"Strategic advice generation failed: {e}")
            return self._fallback_strategic_advice(complexity)

    def _fallback_strategic_advice(self, complexity: ComplexityAnalysis) -> Tuple[List[str], List[str], List[str]]:
        """Generic strategic advice"""
        approach = [
            "Read all requirements carefully and identify deliverables",
            "Break down the assignment into smaller, manageable tasks",
            "Create a timeline with milestones",
            "Start with the most challenging parts first",
            "Review and refine your work before submission"
        ]

        pitfalls = [
            "Starting too late (begin at least 3 days before deadline)",
            "Not clarifying ambiguous requirements with instructor",
            "Skipping the outline/planning phase",
            "Not leaving time for review and revision"
        ]

        tips = [
            "Work in focused 90-minute sessions with breaks",
            "Use office hours if you get stuck",
            "Review similar examples from course materials",
            "Have someone else review your work before submitting"
        ]

        return approach, pitfalls, tips

    def _calculate_success_rate(self, similar_assignments: List[Dict]) -> float:
        """Calculate success rate for similar assignments"""
        if not similar_assignments:
            return 0.0

        completed = sum(1 for s in similar_assignments if s['assignment'].get('grade', 0) >= 70)
        return completed / len(similar_assignments)

    def _calculate_overall_confidence(self,
                                     complexity: ComplexityAnalysis,
                                     skills: List[SkillRequirement]) -> float:
        """Calculate confidence in analysis"""
        base_confidence = complexity.confidence
        has_skills_data = len(skills) > 0

        if has_skills_data:
            return min(0.9, base_confidence + 0.1)
        return base_confidence


# Example usage
if __name__ == "__main__":
    print("🧠 Assignment Intelligence System")
    print("=" * 60)
    print()
    print("Key Concepts Demonstrated:")
    print("1. Bloom's Taxonomy for Cognitive Classification")
    print("2. Multi-dimensional Complexity Analysis")
    print("3. Semantic Similarity Matching")
    print("4. Skill Extraction and Taxonomy")
    print("5. AI-Powered Resource Recommendation")
    print("6. Strategic Advice Generation")
    print()
    print("This system can:")
    print("✅ Analyze assignment complexity across multiple dimensions")
    print("✅ Identify required skills and proficiency levels")
    print("✅ Find similar past assignments for context")
    print("✅ Predict accurate completion times")
    print("✅ Recommend relevant learning resources")
    print("✅ Generate strategic advice and identify pitfalls")
    print("✅ Learn from past assignment outcomes")
