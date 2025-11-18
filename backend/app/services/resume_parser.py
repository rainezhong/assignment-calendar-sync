"""
Resume parser to extract skills, education, and experience from PDF resumes.
"""
import re
from typing import Dict, List
import PyPDF2
from io import BytesIO


class ResumeParser:
    """Parse resume PDFs and extract structured information."""

    def __init__(self):
        # Common tech skills to look for
        self.tech_skills = [
            # Programming languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL',

            # Web technologies
            'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask',
            'FastAPI', 'Spring', 'Rails', 'ASP.NET', 'HTML', 'CSS', 'Tailwind',

            # Mobile
            'React Native', 'Flutter', 'iOS', 'Android', 'Xamarin',

            # Databases
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB',
            'Oracle', 'SQL Server', 'Cassandra', 'Neo4j',

            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins',
            'CI/CD', 'Linux', 'Git', 'GitHub', 'GitLab',

            # Data & ML
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Pandas', 'NumPy', 'Data Analysis', 'Data Science', 'NLP', 'Computer Vision',
            'Tableau', 'Power BI', 'Apache Spark', 'Hadoop',

            # Soft skills
            'Leadership', 'Communication', 'Problem Solving', 'Team Collaboration',
            'Project Management', 'Agile', 'Scrum', 'Critical Thinking',
        ]

        self.degree_patterns = [
            r'Bachelor(?:\'s|\s+of\s+(?:Science|Arts))',
            r'B\.S\.|B\.A\.|BS|BA',
            r'Master(?:\'s|\s+of\s+(?:Science|Arts|Business))',
            r'M\.S\.|M\.A\.|MBA|MS|MA',
            r'Ph\.?D\.?|Doctorate',
            r'Associate(?:\'s)?',
        ]

    def parse(self, pdf_content: bytes) -> Dict:
        """
        Parse resume PDF and extract structured information.

        Args:
            pdf_content: Raw PDF file bytes

        Returns:
            Dictionary with extracted information
        """
        # Extract text from PDF
        text = self._extract_text_from_pdf(pdf_content)

        # Parse sections
        return {
            'text': text,
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'links': self._extract_links(text),
            'skills': self._extract_skills(text),
            'education': self._extract_education(text),
            'experience': self._extract_experience(text),
        }

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            pdf_file = BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def _extract_email(self, text: str) -> str | None:
        """Extract email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def _extract_phone(self, text: str) -> str | None:
        """Extract phone number from text."""
        phone_patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}',
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return ''.join(matches[0]) if isinstance(matches[0], tuple) else matches[0]

        return None

    def _extract_links(self, text: str) -> Dict[str, str]:
        """Extract LinkedIn, GitHub, portfolio URLs."""
        links = {}

        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            links['linkedin'] = f"https://{linkedin_matches[0]}"

        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            links['github'] = f"https://{github_matches[0]}"

        # Portfolio (look for personal websites)
        url_pattern = r'https?://[\w.-]+\.[\w.]+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            if 'linkedin' not in url.lower() and 'github' not in url.lower():
                links['portfolio'] = url
                break

        return links

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using keyword matching."""
        found_skills = []
        text_lower = text.lower()

        for skill in self.tech_skills:
            # Look for skill with word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)

        return found_skills

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education history."""
        education = []

        # Look for degree keywords
        for pattern in self.degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around the degree (±200 characters)
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]

                # Extract university name (capitalize words that look like university names)
                university = self._extract_university_from_context(context)

                # Extract GPA if present
                gpa_pattern = r'GPA[:\s]+([0-9.]+)'
                gpa_match = re.search(gpa_pattern, context, re.IGNORECASE)
                gpa = float(gpa_match.group(1)) if gpa_match else None

                # Extract year
                year_pattern = r'20[0-9]{2}'
                years = re.findall(year_pattern, context)
                graduation_year = years[-1] if years else None

                education.append({
                    'degree': match.group(0),
                    'school': university,
                    'gpa': gpa,
                    'graduation_year': graduation_year,
                })

        return education

    def _extract_university_from_context(self, context: str) -> str | None:
        """Extract university name from context text."""
        # Look for "University" or "College"
        university_pattern = r'([A-Z][a-zA-Z\s&]+(?:University|College|Institute))'
        matches = re.findall(university_pattern, context)
        return matches[0].strip() if matches else None

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience."""
        experience = []

        # Look for common job title keywords
        job_titles = [
            'Engineer', 'Developer', 'Analyst', 'Manager', 'Intern',
            'Consultant', 'Specialist', 'Coordinator', 'Designer',
            'Scientist', 'Researcher', 'Associate', 'Lead'
        ]

        for title_keyword in job_titles:
            pattern = r'([A-Z][a-zA-Z\s]+' + title_keyword + r')'
            matches = re.finditer(pattern, text)

            for match in matches:
                # Get context
                start = max(0, match.start() - 300)
                end = min(len(text), match.end() + 300)
                context = text[start:end]

                # Extract company name (line after job title, often)
                lines = context.split('\n')
                job_line_idx = next((i for i, line in enumerate(lines) if match.group(0) in line), None)

                company = None
                if job_line_idx is not None and job_line_idx + 1 < len(lines):
                    company = lines[job_line_idx + 1].strip()

                # Extract date range
                date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+20[0-9]{2})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+20[0-9]{2}|Present)'
                date_match = re.search(date_pattern, context, re.IGNORECASE)
                duration = date_match.group(0) if date_match else None

                experience.append({
                    'title': match.group(0).strip(),
                    'company': company,
                    'duration': duration,
                })

        return experience[:5]  # Return top 5 experiences


# Helper function for API endpoint
def parse_resume_from_bytes(pdf_bytes: bytes) -> Dict:
    """
    Convenience function to parse resume from bytes.

    Usage:
        pdf_content = await file.read()
        parsed = parse_resume_from_bytes(pdf_content)
    """
    parser = ResumeParser()
    return parser.parse(pdf_bytes)
