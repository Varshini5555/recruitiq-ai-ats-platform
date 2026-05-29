import pdfplumber
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def extract_text_from_pdf(file) -> str:
    """
    Extracts text from an uploaded PDF file.

    Args:
        file: file-like object (from FastAPI UploadFile)

    Returns:
        str: extracted text
    """
    text = ""

    try:
        file.seek(0)
        
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        raise RuntimeError(f"Error extracting text: {str(e)}")

    return text.strip()

def normalize_text(text: str) -> str:

    # Force uppercase for consistency
    text = text.upper()

    # Fix merged headers
    text = re.sub(r"EDUCATION\s+CONTACT", "EDUCATION", text)
    
    # Add newline before known headers
    headers = [
        "SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION",
        "CERTIFICATES", "ACHIEVEMENTS", "LANGUAGES",
        "HOBBIES", "PERSONAL SKILLS"
    ]

    for h in headers:
        text = re.sub(rf"\s*{h}\s*", f"\n{h}\n", text)

    return text



def parse_resume_sections(text: str) -> dict:
    """
    Extract structured sections from resume text
    """
    SECTION_ALIASES = {
        "skills": ["SKILLS", "TECHNICAL SKILLS", "CORE SKILLS"],
        "experience": ["EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "INTERNSHIPS", "INTERNSHIP EXPERIENCE"],
        "projects": ["PROJECTS", "PERSONAL PROJECTS", "ACADEMIC PROJECTS"],
        "education": ["EDUCATION", "ACADEMIC BACKGROUND"],
        "certificates": ["CERTIFICATES", "CERTIFICATIONS"],
        "achievements": ["ACHIEVEMENTS", "ACCOMPLISHMENTS", "AWARDS"],
        "volunteer": ["VOLUNTEER", "VOLUNTEERING", "VOLUNTEERING EXPERIENCE"],
        "summary": ["SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE"],
        "extracurricular": ["EXTRACURRICULAR ACTIVITIES", "HOBBIES AND INTERESTS", "HOBBIES"],
        "languages": ["LANGUAGE SKILLS","LANGUAGE PROFICIENCIES"]


    }

    sections = {key:"" for key in SECTION_ALIASES.keys()}

    lines = text.upper().split("\n")

    current_section = None

    for line in lines:
        line = line.strip()

        for section, aliases in SECTION_ALIASES.items():
            if any(alias in line for alias in aliases):
                current_section = section
                break

        if current_section:
            sections[current_section] += line + "\n"

    return sections



def normalize_llm_output(data: dict) -> dict:
    schema = {
        "summary": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "achievements": [],
        "volunteer": [],
        "extracurricular": [],
        "languages": []
    }

    # Ensure all keys exist
    for key in schema:
        if key not in data:
            data[key] = schema[key]

    # Fix common key issues
    if "Languages" in data:
        data["languages"] = data.pop("Languages")

    if "Extracurricular activities" in data:
        data["extracurricular"] = data.pop("Extracurricular activities")


    return data



def normalize_skills(skills):
    cleaned = []

    for skill in skills:
        skill = skill.strip()

        # Split combined skills like AWS/Azure
        if "/" in skill:
            parts = skill.split("/")
            cleaned.extend([p.strip() for p in parts])
        else:
            cleaned.append(skill)

    # Remove duplicates
    return list(set(cleaned))



def parse_resume_llm(text: str) -> dict:
    import json
    import re

    prompt = f"""
    You are an expert ATS system.

    Extract structured information from the resume.

    - important: Extract every text until you reach the next section or next heading not just the first line.
    -"Languages" must ONLY include spoken languages (e.g., English, Hindi)
    - Do NOT include programming languages in "languages"
    - Do NOT include soft skills like "positive attitude" unless explicitly listed
    - Keep skills technical and ATS-relevant
    -For projects, extract ALL technologies explicitly mentioned (libraries, frameworks, APIs, tools)
    -Split experience and project descriptions into bullet-point achievements
    -return the certification section as objects with title and issuer
    - capture information like github link, linkedink id, ph no, mail id and address if available into "contact details" like linkedin: and the link , ph no" and the phone number
    
    Return ONLY valid JSON in this format:

{{
  "summary": string,
  "contact detailes": list of objects
  "skills": list of strings,
  "experience": list of objects,
  "projects": list of objects,
  "education": list of objects,
  "certifications": list,
  "achievements": list,
  "volunteer": list,
  "extracurricular": list,
  "languages": list
}}

    Do NOT wrap in markdown.

    Resume:
    {text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a resume parsing expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a resume parsing expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # 🔥 Clean markdown
        content = re.sub(r"```json|```", "", content).strip()

        # 🔥 Extract JSON
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            return {"error": "No JSON found", "raw": content}

        parsed = json.loads(match.group())

        # ✅ POST PROCESSING
        parsed = normalize_llm_output(parsed)

        return parsed

    except Exception as e:
        return {"error": str(e)}