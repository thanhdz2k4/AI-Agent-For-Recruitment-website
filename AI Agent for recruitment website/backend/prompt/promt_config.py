class PromptConfig:
    def __init__(self):
        self.prompts = {
            "job_description_analysis": (
                "Analyze the following job description and extract key skills, qualifications, "
                "and responsibilities required for the role:\n\n{job_description}\n\n"
                "Provide a summary in bullet points."
            ),
            "extract_features_question_about_job": (
                """You are an information extraction engine. Your task is to map Vietnamese and English user job queries into MongoDB fields.

SCHEMA (only these fields allowed):
- title: job position/role (e.g., "Data Analyst", "Unity Developer")
- company: company name (e.g., "FPT Software", "Viettel")
- location: work location (e.g., "Hà Nội", "Hồ Chí Minh", "Đà Nẵng")
- skills: required skills/technologies (e.g., "Python", "React.js")
- experience: experience level (e.g., "1-2 năm", "Internship", "3 năm")

OUTPUT RULES:
1) Output valid JSON only (no extra text, no comments, no code fences).
2) Include ALL relevant fields that are explicitly present in the input. Omit keys that are absent.
3) Use exact field names from SCHEMA.
4) If no field matches at all, return {{}} exactly.
5) Never hallucinate values. Only extract if explicitly mentioned or as a direct synonym/alias mapping (see LOCATION CANONICALIZATION).
6) Do not output null/empty-string values. Include a key only if you have a concrete value.
7) For fields that can have multiple values (e.g., skills), join by ", " in a single string (e.g., "Python, SQL").

LANGUAGE + NORMALIZATION:
- Handle both Vietnamese and English inputs.
- Be case-insensitive and diacritic-insensitive during matching, but output should preserve canonical forms below.

LOCATION CANONICALIZATION (map common variants/synonyms to these exact outputs):
- "Hà Nội": ["Hà Nội", "Ha Noi", "Hanoi", "HN"]
- "Hồ Chí Minh": ["Hồ Chí Minh", "Ho Chi Minh", "Ho Chi Minh City", "TP.HCM", "TP HCM", "HCM", "Sài Gòn", "Saigon", "SG"]
- "Đà Nẵng": ["Đà Nẵng", "Da Nang", "Danang", "ĐN", "DN"]
(If a location is not in this list but clearly mentioned in the input, output it as written in the input.)

DECISION RULES:
- title vs skills:
  - A job position/role → "title" (e.g., "Java Developer", "thực tập sinh AI").
  - A technology/tool/framework → "skills" (e.g., "React.js", "Python").
  - If the phrase is "<TECH> developer" (VN/EN variants like "lập trình viên <TECH>"), set both:
      title = "<TECH> developer" (or the VN phrase as in input)
      skills includes "<TECH>".
- company:
  - Extract company names when explicitly mentioned (patterns like "tại <company>", "ở <company>", "at <company>", "with <company>").
- location:
  - Extract when patterns like "ở/tại/in/at <place>" appear.
  - Apply LOCATION CANONICALIZATION for Hà Nội / Hồ Chí Minh / Đà Nẵng.
  - If the query only mentions a location (e.g., "Công việc tại Đà Nẵng"), return just location field — do NOT return empty object.
- experience:
  - Vietnamese: patterns like "<n> năm", "1-2 năm", "thực tập", "thực tập sinh".
  - English: "Intern"/"Internship", "<n> years".
- description:
  - General non-technical keywords that describe the job but are not clearly title/skills/company/location/experience (e.g., "remote", "toàn thời gian", "full-time", "onsite").

SPECIAL NOTES:
- Keep values as they appear, except location canonicalization. Do not rewrite or translate titles/skills/company.
- If multiple skills/technologies are mentioned (e.g., "Python, SQL"), include them in "skills" as "Python, SQL".

EXAMPLES (strictly follow these):
Input: "có bao nhiêu công ty đang tuyển việc tại Hà Nội"
Output: {{"location": "Hà Nội"}}

Input: "Hà Nội có tuyển Data Analyst không?"
Output: {{"location": "Hà Nội", "title": "Data Analyst"}}

Input: "tôi muốn tìm việc làm Java Developer"
Output: {{"title": "Java Developer"}}

Input: "công ty nào yêu cầu Python"
Output: {{"skills": "Python"}}

Input: "thực tập sinh AI tại FPT"
Output: {{"title": "thực tập sinh AI", "company": "FPT"}}

Input: "senior developer 3 năm kinh nghiệm"
Output: {{"title": "senior developer", "experience": "3 năm"}}

Input: "Tìm các công ty đang tuyển IOS Developer"
Output: {{"title": "IOS Developer"}}

Input: "Công việc ở Hà Nội, là IT"
Output: {{"location": "Hà Nội", "title": "IT"}}

Input: "Công việc tại Đà Nẵng"
Output: {{"location": "Đà Nẵng"}}

Input: "Job in Ho Chi Minh City for React.js developer"
Output: {{"location": "Hồ Chí Minh", "title": "React.js developer", "skills": "React.js"}}

---
INPUT: "{user_input}"
OUTPUT:
"""
            )
        }

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Return the prompt text. If kwargs are provided, format placeholders.
        Example: get_prompt("extract_features_question_about_job", user_input="Tìm việc ở Hà Nội")
        """
        template = self.prompts.get(prompt_name, "Prompt not found.")
        return template.format(**kwargs)  # <-- inject user_input etc.
