import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


def load_level_weights():

    level_weights_path = os.path.join(
        BASE_DIR,
        "data",
        "level_weights.json"
    )

    with open(level_weights_path, "r") as f:
        return json.load(f)


def get_level_weights(level: str):

    weights = load_level_weights()

    level = level.lower()

    if level not in weights:
        raise ValueError(f"Invalid level: {level}")

    return weights[level]
    

    

def load_jd(role: str):
    """
    role examples:
    - ai_engineer
    - data_scientist
    - ml_engineer
    - data_engineer
    - data_analyst
    """

    filename_map = {
        "ai engineer": "ai_engineer_final.json",
        "data scientist": "data_scientist_final.json",
        "ml engineer": "ML_engineer_final.json",
        "data engineer": "data_engineer_final.json",
        "data analyst": "data_analyst_final.json",

        "ai_engineer": "ai_engineer_final.json",
        "data_scientist": "data_scientist_final.json",
        "ml_engineer": "ML_engineer_final.json",
        "data_engineer": "data_engineer_final.json",
        "data_analyst": "data_analyst_final.json"
    }

    role=role.lower()

    if role not in filename_map:
        raise ValueError(f"Unsupported role: {role}")
    
    path = os.path.join(BASE_DIR,"data","jds",filename_map[role])

    with open(path,"r") as f:
        return json.load(f)
    


def load_custom_jd(jd_text: str) -> dict:
    """
    Convert raw JD text into the structured MASTER format using LLM.
    """

    # We provide the exact structure you shared to the LLM as a template
    prompt = f"""
    You are an expert technical recruiter.
    Convert the following raw Job Description text into a highly structured JSON format.
    
    ### STRICT JSON STRUCTURE TO FOLLOW:
    {{
      "job_id": "CUSTOM_JD_001",
      "role": "Extracted Job Title",
      "company": "Extracted Company Name or 'Unknown'",
      "experience_level": "e.g., Junior, Mid-Level, Senior",
      "job_summary": "Short 1-2 sentence summary",
      "skills": {{
        "must_have": [{{ "name": "Skill Name", "weight": 1.0 }}],
        "good_to_have": [{{ "name": "Skill Name", "weight": 0.8 }}],
        "specialized": [{{ "name": "Skill Name", "weight": 0.9 }}]
      }},
      "tools_and_technologies": [],
      "responsibilities": [],
      "qualifications": {{
        "education": "Required degree",
        "certifications": []
      }},
      "experience_requirements": {{
        "min_years": 0,
        "max_years": 0
      }},
      "keywords": []
    }}

    ### INSTRUCTIONS:
    1. Place core required technical skills in 'must_have'.
    2. Place domain-specific expertise or advanced tools in 'specialized'.
    3. Place soft skills or preferred tools in 'good_to_have'.
    4. Return ONLY valid JSON.

    RAW JD TEXT:
    {jd_text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a hiring expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    import re
    import json

    content = response.choices[0].message.content.strip()
    content = re.sub(r"```json|```", "", content).strip()

    match = re.search(r"\{.*\}", content, re.DOTALL)

    if match:
        return json.loads(match.group())

    return {"error": "Failed to parse JD"}

def get_jd(role: str = None, jd_text: str = None):
    """"
    Priority:
    1. If user uploads JD -> use that
    2. Else use system JD
    """

    if jd_text:
        return load_custom_jd(jd_text)
    
    if role:
        return load_jd(role)
    
    raise ValueError("Either role or jd_text must be provided")



SKILL_MAP = {
    "ml": "machine learning",
    "machine learning": "machine learning",
    "llm": "large language models",
    "llms": "large language models",
    "llm apis": "large language models",
    "llm application": "large language models",
    "context-aware generation": "large language models",
    "genai": "generative ai",
    "generative ai": "generative ai",
    "nlp": "natural language processing",
    "text analytics": "natural language processing",
    "transformer": "natural language processing", 
    "roberta": "natural language processing",    
    "aws": "cloud platforms",
    "azure": "cloud platforms",
    "gcp": "cloud platforms",
    "api": "apis / system integration",
    "apis": "apis / system integration",
    "deployment": "model deployment",
    "streamlit": "model tool",
    "fastapi": "model tool",
    "hugging face": "large language models",
    "claude": "large language models",
    "chatgpt": "large language models",
    "classification": "model development",
    "regression": "model development",
    "scikit-learn": "model development"
}

SKILL_GROUPS = {
    "cloud platforms": ["aws", "azure", "gcp"],
    "large language models": ["llm", "openai", "hugging face", "groq"],
    "apis / system integration": ["api", "rest", "integration"],
}

# TIER 2: Professional use (Good)
INTERMEDIATE_VERBS = ["built", "developed", "implemented", "engineered", "designed"]

# TIER 3: Expert-level context (Best)
ADVANCED_KEYWORDS = ["deployed", "production", "pipeline", "end-to-end", "automated", "optimized", "fine-tuned", "scaled", "architected"]

SKILL_HIERARCHY = {
    "python": ["pandas", "numpy", "scikit-learn", "sklearn", "matplotlib", "seaborn", "statsmodels", "requests"],
    "sql": ["advanced joins", "window functions", "postgresql", "mysql", "t-sql", "query optimization"],
    "power bi": ["dax", "power query", "data modeling"],
    "large language models": ["prompt engineering", "few-shot learning", "rag", "langchain", "context-aware generation"],
    "machine learning": ["classification", "regression", "svm", "random forest", "model evaluation", "eda"]
}


def compute_skill_score(resume_data: dict, jd: dict) -> dict:

    # 1. Normalize skill text
    def normalize_skill(skill):
        if not skill:
            return ""
        if isinstance(skill, list): 
            skill = " ".join(skill)
        skill = str(skill).lower().strip()
        
        # Use a partial match to ensure 'LLMs' in a sentence maps to the group
        for key in SKILL_MAP:
            if key in skill:
                return SKILL_MAP[key]
        return skill

    # 2. Extract all resume text
    def extract_all_text(resume_data):
        texts = []
        texts += resume_data.get("skills", [])
        texts += resume_data.get("technical_skills", [])
        for proj in resume_data.get("projects", []):
            texts += proj.get("technologies", [])
            texts += proj.get("achievements", [])
        for exp in resume_data.get("experience", []):
            texts += exp.get("achievements", [])
        return [str(t).lower() for t in texts if t]

    raw_texts = extract_all_text(resume_data)
    # UPDATED: Pre-normalize all raw texts for the depth detector to use
    normalized_raw_texts = [normalize_skill(t) for t in raw_texts]

    # 3. Strong evidence check
    def has_strong_evidence(text):
        return any(v in text.lower() for v in ADVANCED_KEYWORDS or INTERMEDIATE_VERBS)

    # 4. Group matching
    def group_match(jd_skill, text):
        jd_skill = jd_skill.lower()
        if jd_skill in SKILL_GROUPS:
            return any(tool in text.lower() for tool in SKILL_GROUPS[jd_skill])
        return False

    # 5. Improved matching logic
    def match_score(jd_skill_name):
        norm_jd_skill = normalize_skill(jd_skill_name)
        jd_tokens = set(norm_jd_skill.split())
        score = 0

        for i, text in enumerate(raw_texts):
            norm_text = normalized_raw_texts[i]
            
            # Check match against BOTH raw and normalized text
            if norm_jd_skill in norm_text or norm_jd_skill in text:
                if has_strong_evidence(text):
                    score += 2.5
                else:
                    score += 1.0

            # Token overlap
            text_tokens = set(text.split())
            overlap = jd_tokens.intersection(text_tokens)
            if len(overlap) >= max(1, len(jd_tokens) // 2):
                score += 1.0

            if group_match(jd_skill_name, text):
                score += 2.5
        return score

    # 6. Skill depth detection
    # Now uses normalized text to catch LLM experience effectively
    def detect_depth_for_skill(skill):
        norm_skill_target = normalize_skill(skill)
        occurrence_count = 0
        highest_detected_level = "basic"

    # Combine all entries to check them individually
    
    # NEW LOGIC: Project Inheritance
        for p in resume_data.get("projects", []):
            techs = [str(t).lower() for t in p.get("technologies", [])]
            achievements = " ".join(p.get("achievements", [])).lower()
        
        # If the skill is in the tech list OR the achievement text
            if norm_skill_target in techs or any(norm_skill_target in normalize_skill(t) for t in techs) or norm_skill_target in achievements:
                occurrence_count += 1
            # Check achievements for depth keywords
                if any(v in achievements for v in ADVANCED_KEYWORDS):
                    highest_detected_level = "advanced"
                elif any(v in achievements for v in INTERMEDIATE_VERBS) and highest_detected_level != "advanced":
                    highest_detected_level = "intermediate"
    
    # Standard Experience Check
        for e in resume_data.get("experience", []):
         exp_text = " ".join(e.get("achievements", [])).lower()

         if norm_skill_target in exp_text or norm_skill_target in normalize_skill(exp_text):
          occurrence_count += 1
          if any(v in exp_text for v in ADVANCED_KEYWORDS):
            highest_detected_level = "advanced"
          elif any(v in exp_text for v in INTERMEDIATE_VERBS) and highest_detected_level != "advanced":
            highest_detected_level = "intermediate"

    # --- NEW LOGIC: Upgrade based on Frequency ---
        if occurrence_count >= 2:
            return "advanced"  # Used in 3+ different projects/jobs
        elif occurrence_count == 1 and highest_detected_level == "basic":
            return "intermediate" # Used in 2 different places, even without strong verbs
    
        return highest_detected_level

    # 7. JD Skills
    must_have = jd["skills"].get("must_have", [])
    good_to_have = jd["skills"].get("good_to_have", [])
    specialized = jd["skills"].get("specialized", [])

    matched, weak_matches, missing = [], [], []
    score, total_weight = 0, 0

    # 8. Process skills
    def process_skills(skill_list, multiplier):
        nonlocal score, total_weight

        # Map the multiplier to a descriptive priority label
        priority_map = {
            1.5: "Critical Requirement",
            1.2: "Specialized Skill",
            1.0: "Preferred/General"
        }
        current_priority = priority_map.get(multiplier, "Standard")

        for skill in skill_list:
            jd_name_raw = skill["name"]
            jd_name = normalize_skill(jd_name_raw)

            weight = skill["weight"] * multiplier
            total_weight += weight

            m_score = match_score(jd_name)

            if m_score >= 2:
                score += weight
                matched.append({
                    "skill": jd_name_raw,
                    "match_type": "Full Match",
                    "priority": current_priority  # Shows 'Critical', 'Specialized', etc.
                })

            elif m_score > 0:
                score += weight * 0.5
                weak_matches.append({
                    "skill": jd_name_raw,
                    "match_type": "Partial Match",
                    "priority": current_priority
                })

            else:
                missing.append(jd_name_raw)

    process_skills(must_have, 1.5)
    process_skills(specialized, 1.2)
    process_skills(good_to_have, 1.0)

    # 9. Final calculations
    final_score = (score / total_weight) * 100 if total_weight > 0 else 0
    
  # -----------------------------
    # 10. Deduplicated Skill Depth (UPDATED)
    # -----------------------------
    level_weights = {"advanced": 3, "intermediate": 2, "basic": 1}
    best_skill_levels = {}

    resume_skill_list = resume_data.get("skills", []) + resume_data.get("technical_skills", [])
    
    for skill in resume_skill_list:
        norm_name = normalize_skill(skill)
        current_level = detect_depth_for_skill(skill)
        
        # Logic: If we see the same skill again, only keep the higher level
        if norm_name not in best_skill_levels or level_weights[current_level] > level_weights[best_skill_levels[norm_name]]:
            best_skill_levels[norm_name] = current_level

    # Now, "Shadow" children if the parent exists at the same or higher level
    final_display_skills = best_skill_levels.copy()
    
    for parent, children in SKILL_HIERARCHY.items():
        if parent in best_skill_levels:
            parent_level = level_weights[best_skill_levels[parent]]
            for child in children:
                if child in final_display_skills:
                    child_level = level_weights[final_display_skills[child]]
                    # Only remove the child if its evidence level isn't higher than the parent
                    if child_level <= parent_level:
                        del final_display_skills[child]

    # Reconstruct the depth_output buckets using the deduplicated results
    depth_output = {"advanced": [], "intermediate": [], "basic": []}
    for skill_name, level in final_display_skills.items():
        depth_output[level].append(skill_name)

    # -----------------------------
    # 11. Skill credibility (Refined)
    # -----------------------------
    advanced = len(depth_output["advanced"])
    intermediate = len(depth_output["intermediate"])
    basic = len(depth_output["basic"])
    total_unique_skills = len(best_skill_levels)

    skill_credibility = (
        (advanced * 1.0) + 
        (intermediate * 0.75) + 
        (basic * 0.)
    ) / max(1, total_unique_skills)

    return {
        "overall_fit_score": round(final_score, 2),
        "found_requirements": matched,
        "partial_requirements": weak_matches,
        "missing_skills": list(set(missing)),
        
        # New "Evidence" Labeling
        "depth_analysis": {
            "High Evidence (Project/Exp Verified)": depth_output["advanced"],
            "Medium Evidence (Mentioned in Context)": depth_output["intermediate"],
            "Low Evidence (Skill List Only)": depth_output["basic"]
        },

        "resume_credibility_index": round(skill_credibility, 2)
    }


DOMAIN_KEYWORDS = {
        "nlp": ["nlp", "transformer", "roberta", "bert", "sentiment", "text analytics"],
        "genai": ["llm","generative ai", "rag", "prompt engineering", "langchain", "transformer"],
        "analytics": ["eda", "analysis", "visualization", "pandas", "numpy", "seaborn", "matplotlib"],
        "dashboard": ["power bi", "tableau", "dashboard"],
        "ml": ["classification", "regression", "svm", "random forest"],
        "api": ["api", "fastapi", "rest api"]
    }
# Project scoring
def compute_project_score(resume_data: dict, jd: dict, candidate_level="fresher") -> dict:

    level_config = get_level_weights(candidate_level)

    # --- HELPER FUNCTIONS ---
    def normalize_text(text):
        text = str(text).lower().strip()
        normalized_parts = []
        # Assuming SKILL_MAP is defined globally in your scorer file
        for word in text.split():
            mapped = word
            for key in SKILL_MAP:
                if key in word:
                    mapped = SKILL_MAP[key]
            normalized_parts.append(mapped)
        return " ".join(normalized_parts)

    # --- CONFIGURATION ---
    STRONG_VERBS = ["built", "developed", "implemented", "engineered", "designed", "created"]
    ADVANCED_SIGNALS = ["deployed", "production", "pipeline", "automated", "optimized", "scalable", "fine-tuned", "end-to-end"]
    IMPACT_WORDS = ["improved", "reduced", "increased", "optimized", "boosted", "accelerated"]
    TUTORIAL_PROJECTS = ["iris", "titanic", "mnist", "basic chatbot", "tutorial", "youtube tutorial", "simple chatbot"]

    

    # --- INITIALIZATION ---
    projects = resume_data.get("projects", [])
    analyzed_projects = []
    total_project_score = 0
    detected_domain = set()
    advanced_project_count = 0

    # Step-2: Extract JD skills
    jd_skills = []
    jd_skills_data = jd.get("skills", {})
    for category in ["must_have", "good_to_have", "specialized"]:
        for skill in jd_skills_data.get(category, []):
            jd_skills.append(skill["name"].lower())

    # --- Step-3: PROCESS EACH PROJECT (Looping through the list) ---
    for project in projects:
        # Access individual project dictionary
        title = project.get("title", "") or project.get("name") or project.get("project_name") or "Untitled Project"
        technologies = project.get("technologies", []) or project.get("tools") or []
        achievements = project.get("achievements", [])

        # Step-4: Create project text
        project_text = " ".join([
            title,
            " ".join(technologies),
            " ".join(achievements)
        ]).lower()
        normalized_project_text = normalize_text(project_text)

        # Step-5: Detect matched skills
        matched_skills = []
        for skill in jd_skills:
            normalized_jd_skill = normalize_text(skill)
            if normalized_jd_skill in normalized_project_text or skill in project_text:
                matched_skills.append(skill)
        matched_skills = list(set(matched_skills))

        # Step-6: Detect strong verbs
        found_strong_verbs = [v for v in STRONG_VERBS if v in project_text]

        # Step-7: Detect advanced signals
        found_advanced_signals = [s for s in ADVANCED_SIGNALS if s in project_text]

        # Step-8: Detect impact metrics
        impact_metrics = re.findall(r"\d+%", project_text)
        for word in IMPACT_WORDS:
            if word in project_text:
                impact_metrics.append(word)

        # Step-9: Detect project domain
        project_domains = []
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in project_text:
                    project_domains.append(domain)
                    detected_domain.add(domain)
                    break

        # Step-10: Relevance score
        relevance_score = len(matched_skills) * 5

        # Step-11: Complexity score
        complexity_score = (len(found_strong_verbs) * 2) + (len(found_advanced_signals) * 4)
        if len(technologies) >= 3:
            complexity_score += 5

        # Step-12: Impact score
        impact_score = len(impact_metrics) * 3

        # Step-13: Tutorial penalty
        tutorial_penalty = sum(10 for t in TUTORIAL_PROJECTS if t in project_text)

        # Step-14: Evidence level
        if len(found_advanced_signals) >= 1:
            evidence_level = "High"
            advanced_project_count += 1
        elif len(found_strong_verbs) >= 1:
            evidence_level = "Medium"
        else:
            evidence_level = "Low"

        # Step-15: Final score for THIS project
        final_project_score = max(0, (relevance_score + complexity_score + impact_score - tutorial_penalty))

        # Step-16: Store analysis for THIS project
        analyzed_projects.append({
            "project_title": title,
            "matched_skills": matched_skills,
            "strong_verbs": found_strong_verbs,
            "advanced_signals": found_advanced_signals,
            "impact_metrics": impact_metrics,
            "domains": project_domains,
            "relevance_score": relevance_score,
            "complexity_score": complexity_score,
            "impact_score": impact_score,
            "tutorial_penalty": tutorial_penalty,
            "final_project_score": final_project_score,
            "evidence_level": evidence_level
        })

        # Step-17: Increment the total score
        total_project_score += final_project_score

    # --- Step-18: POST-PROCESS (Outside the loop) ---
    num_projects = len(projects)
    
    if num_projects > 0:
        # Calculate the base quality average
        average_project_score = total_project_score / num_projects
    else:
        average_project_score = 0

    # Apply the diversity bonus to the average
    diversity_bonus = len(detected_domain) * 3

    # Final score is Average Quality + Diversity Bonus and level configuration
   

    final_project_score = (
    average_project_score +
    diversity_bonus
)

# -----------------------------------
# LEVEL-BASED PROJECT ADJUSTMENTS
# -----------------------------------

    project_multiplier = level_config.get(
    "project_multiplier",
    1.0
)

    final_project_score *= project_multiplier

# -----------------------------------
# ADVANCED PROJECT EXPECTATION
# -----------------------------------

    required_advanced_projects = level_config.get(
    "advanced_project_expectation",
    0
)

    if advanced_project_count < required_advanced_projects:

      advanced_gap = (
        required_advanced_projects -
        advanced_project_count
    )

      final_project_score -= advanced_gap * 5

# -----------------------------------
# COMPLEXITY EXPECTATION
# -----------------------------------

    required_complexity = level_config.get(
    "minimum_project_complexity",
    0
)

    if average_project_score < required_complexity:

       complexity_gap = (
        required_complexity -
        average_project_score
    )

       final_project_score -= complexity_gap * 0.8

# -----------------------------------
# Prevent negative score
# -----------------------------------

    final_project_score = max(
    0,
    final_project_score
)

# -----------------------------------
# Cap score
# -----------------------------------

    normalized_project_score = min(
    100,
    round(final_project_score, 2)
)

    return {
        "project_score": round(normalized_project_score, 2),
        "project_diversity_score": diversity_bonus,
        "advanced_project_score": advanced_project_count,
        "projects_analyzed": analyzed_projects
    }


#impact score
def compute_impact_score(resume_data: dict, jd: dict, skill_analysis: dict = None, project_analysis: dict = None, candidate_level="fresher") -> dict:
    
    level_config = get_level_weights(candidate_level)

    IMPACT_VERBS = {
        "improved","reduced","increased","optimized","accelerated",
        "enhanced","boosted","automated","scaled","streamlined","reducing",
        "improving","driving","supporting","refining"
    }

    OWNERSHIP_VERBS = {
        "built","developed","engineered","designed","architected",
        "implemented","led","created"
    }

    SCALE_SIGNALS = {
        "global","enterprise","high-volume","large-scale","production",
        "real-time","distributed"
    }

    ADVANCED_TECHNICAL_SIGNALS = {
        "pipeline","end-to-end","deployment","fine-tuned","llm","rag","transformer","mlops","api",
        "sql","classification","analytics","validation","auditing","workflow","transformation"
    }

    LEADERSHIP_SIGNALS = [
        "led",
        "managed",
        "mentored",
        "coordinated",
        "stakeholder",
        "cross-functional",
        "ownership"
    ]

    ARCHITECTURE_SIGNALS = [
        "architected",
        "scalable",
        "distributed",
        "production",
        "end-to-end",
        "infrastructure",
        "system design",
        "platform"
    ]

    #1.Extract JD skills

    jd_skills = set()

    for category in ["must_have","specialized","good_to_have"]:
        for skill in jd.get("skills",{}).get(category,[]):
            skill_name =  str(skill.get("name","")).lower()

            if skill_name:
                jd_skills.add(skill_name)

    #2. Extract all Bullets
    
    bullets= []

    for exp in resume_data.get("experience", []):
        for achievement in exp.get("achievements",[]):

            bullets.append({
                "source": "experience", "text": achievement
            })

    for proj in resume_data.get("project", []):
        for achievement in proj.get("achievements",[]):

            bullets.append({
                "source": "project", "text": achievement
            })

    #3.Helper Function

    def contains_any(text, keywords):

        text = text.lower()

        return [word for word in keywords if word in text]
    
    
    def extract_metrics(text):

         metric_patterns = [
             r"\d+(?:\.\d+)?%",          # 99.9%
             r"\d+(?:\.\d+)?\s?x",       # 2x
             r"\$\d+(?:,\d+)*",          # $10,000
             r"\d+(?:\.\d+)?\s?(million|thousand|k)",
             r"\d+(?:\.\d+)?\s?(ms|sec|seconds)",
            ]
         
         metrics = []

         for pattern in metric_patterns:
             
             matches = re.findall(pattern, text.lower())

             if matches:
                 if isinstance(matches[0], tuple):
                     metrics.extend(
                         [" ".join(m).strip() for m in matches]
                     )
                 else:
                     metrics.extend(matches)   

         return list(set(metrics))      
      
    
    def jd_alignment(text):
         
         text = text.lower()

         matched = []

         for skill in jd_skills:
             if skill in text:
                 matched.append(skill)

         return matched
    
    # 4.Analyze each bullet

    analyzed_bullets = []

    total_bullet_score = 0

    total_metrics = 0
    total_impact_signals = 0
    total_ownership_signals = 0
    total_scale_signals = 0
    leadership_count = 0
    architecture_count = 0

    strongest_bullet = None
    strongest_score = 0

    for bullet in bullets:

        text = bullet["text"]
        lower_text = text.lower()
        
        metrics = extract_metrics(lower_text)

        impact_hits = contains_any(
            lower_text,
            IMPACT_VERBS
        )

        ownership_hits = contains_any(
            lower_text,
            OWNERSHIP_VERBS
        )

        scale_hits = contains_any(
            lower_text,
            SCALE_SIGNALS
        )

        technical_hits = contains_any(
            lower_text,
            ADVANCED_TECHNICAL_SIGNALS
        )

        leadership_hits = [
            word for word in LEADERSHIP_SIGNALS
            if word in lower_text
        ]

        architecture_hits = [
            word for word in ARCHITECTURE_SIGNALS
            if word in lower_text
        ]

        jd_matches = jd_alignment(lower_text)

        #5. Bullet Scoring
    
        bullet_score = 0

         # Quantifiable metrics
        bullet_score += len(metrics) * 5

        # Business impact
        bullet_score += len(impact_hits) * 3

        # Ownership
        bullet_score += len(ownership_hits) * 5

        # Scale
        bullet_score += len(scale_hits) * 4

        # Technical depth
        bullet_score += len(technical_hits) * 3

        # JD relevance bonus
        bullet_score += len(jd_matches) * 4

         # leadership + architecture bonus
        bullet_score += len(leadership_hits) * 6
        bullet_score += len(architecture_hits) * 6

        # Experience bullets slightly more important
        if bullet["source"] == "experience":
            bullet_score *= 1.1

        #6.Evidence level

        if bullet_score >=25:
            evidence_level = "High"
        
        elif bullet_score >= 12:
            evidence_level = "Medium"

        else:
            evidence_level = "Low"

        #7. Store Analysis
        analyzed_bullets.append({

            "source": bullet["source"],

            "bullet": text,

            "metrics_found": metrics,

            "impact_signals": impact_hits,

            "ownership_signals": ownership_hits,

            "scale_signals": scale_hits,

            "technical_signals": technical_hits,

            "jd_alignment": jd_matches,
            
            "leadership_signals": leadership_hits,
            
            "architecture_signals": architecture_hits,

            "bullet_impact_score": round(bullet_score, 2),

            "evidence_level": evidence_level
        })

        #8. Track Totals
        total_bullet_score += bullet_score

        total_metrics += len(metrics)

        total_impact_signals += len(impact_hits)

        total_ownership_signals += len(ownership_hits)

        total_scale_signals += len(scale_hits)
        
        leadership_count += len(leadership_hits)

        architecture_count += len(architecture_hits)

        # Strongest bullet
        if bullet_score > strongest_score:

            strongest_score = bullet_score

            strongest_bullet = text


    # 9. BASE IMPACT SCORE

    impact_score = min(100, total_bullet_score)

   
    # 10. COMBINE WITH SKILL + PROJECT SCORES

    skill_score = 0
    project_score = 0

    if skill_analysis:
        skill_score = skill_analysis.get(
            "overall_fit_score",
            skill_analysis.get("skill_score", 0)
        )

    if project_analysis:
        project_score = project_analysis.get(
            "project_score",
            0
        )

    # 11. FINAL COMBINED SCORE

    # Weighted composition
    final_impact_score = (

        (impact_score * 0.5) +
        (skill_score * 0.25) +
        (project_score * 0.25)

    )

    #level configuration
    # -----------------------------------
# LEVEL-BASED IMPACT ADJUSTMENTS
# -----------------------------------

    impact_multiplier = level_config.get(
      "impact_multiplier",
      1.0
)

    final_impact_score *= impact_multiplier

# -----------------------------------
# Leadership expectation penalty
# -----------------------------------

    required_leadership = level_config.get(
    "leadership_expectation",
    0
)

    required_architecture = level_config.get(
    "architecture_expectation",
    0
)

    if leadership_count < required_leadership:
        
        leadership_gap = (
        required_leadership - leadership_count
    )
        
        final_impact_score -= leadership_gap * 5


    if architecture_count < required_architecture:
        architecture_gap = (
        required_architecture - architecture_count
    )

        final_impact_score -= architecture_gap * 5

# Prevent negative scores
    final_impact_score = max(0, final_impact_score)

# Cap score
    final_impact_score = min(
    100,
    round(final_impact_score, 2)
)

   
    # 12. OVERALL IMPACT QUALITY

    avg_bullet_score = (
        total_bullet_score / max(1, len(bullets))
    )

    if avg_bullet_score >= 15:
        impact_quality = "Excellent"

    elif avg_bullet_score >= 8:
        impact_quality = "Good"

    else:
        impact_quality = "Moderate"

    # 13. FINAL OUTPUT

    return {

        "overall_impact_score": final_impact_score,

        "bullet_impact_score": round(avg_bullet_score,2),

        "impact_quality": impact_quality,

        "strongest_impact_bullet": strongest_bullet,

        "quantified_achievements": total_metrics,

        "business_impact_signals": total_impact_signals,

        "ownership_signals": total_ownership_signals,

        "scale_indicators": total_scale_signals,

        "bullet_analysis": analyzed_bullets
    }



def compute_ats_format_score(resume_data: dict, candidate_level = "fresher") -> dict:


    REQUIRED_SECTIONS = ["skills","experience","education","projects"]

    ATS_RISK_SYMBOLS = [ 
        "█",
        "♦",
        "➜",
        "◉",
        "✓",
        "★"
    ]

    # 1. initial scores

    section_score = 0
    contact_score = 0
    length_score = 0
    parseability_score = 0
    consistency_score = 0

    issues_found = []
    strengths = []

    # 2. Raw resume text

    all_text_parts = []

    for key, value in resume_data.items():

        if isinstance(value, str):

            all_text_parts.append(value)
        
        elif isinstance(value, list):

            for item in value:
                
                if isinstance(item, str):
                    
                    all_text_parts.append(item)
                
                elif isinstance(item, dict):

                    for v in item.values():

                        if isinstance(v, str):

                            all_text_parts.append(v)

                        elif isinstance(v, list):

                            all_text_parts.extend(
                                [str(x) for x in v]
                            )

    resume_text = " ".join(all_text_parts)

    lower_resume_text = resume_text.lower()

    # 3. Section check

    found_sections = 0

    section_mapping = {
        "skills": "skills",
        "experience": "experience",
        "education": "education",
        "projects": "projects"
    }

    for section in REQUIRED_SECTIONS:

        mapped_key = section_mapping.get(section)

        section_data = resume_data.get(
            mapped_key
        )

        if section_data:

            found_sections += 1

    section_score = (
        found_sections /
        len(REQUIRED_SECTIONS)
    ) * 30

    if found_sections == len(REQUIRED_SECTIONS):

        strengths.append(
            "All essential ATS sections are present"
        )

    else:

        missing_count = (
            len(REQUIRED_SECTIONS) - 
            found_sections
        )

        issues_found.append(
            f"{missing_count} important resume sections may be missing"
        )

    # 4. Contact Information

    email_regex = (
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    )

    phone_regex = (
    r"(\+?\d{1,3}[- ]?)?([\dxX]{8,15})"
)

    linkedin_regex = r"linkedin\.com"

    github_regex = r"github\.com"

    contact_details = resume_data.get("contact_details", [])

    email_found = False
    phone_found = False
    linkedin_found = False
    github_found = False

    for item in contact_details:

        if not isinstance(item, dict):
            continue

        if item.get("email"):
            email_found = True

        if item.get("phone"):
            phone_found = True

        if item.get("github"):
            github_found = True

        if item.get("linkedin"):
            linkedin_found = True

    if not phone_found:
        phone_found = re.search(
            phone_regex,
            lower_resume_text
        )
    
    if not email_found:
        email_found = re.search(
            email_regex,
            lower_resume_text
        )

    if not linkedin_found:
        linkedin_found = re.search(
            linkedin_regex,
            lower_resume_text
        )

    if not github_found:

        github_found = re.search(
            github_regex,
            lower_resume_text
        )
    
    if email_found:

        contact_score += 6

    else:

        issues_found.append(
                "Email address missing"
         )

    if phone_found:

        contact_score += 6

    else:

        issues_found.append(
                "Phone number missing"
            )

    if linkedin_found:

          contact_score += 4

    else:

        issues_found.append(
            "LinkedIn profile missing"
         )

    if github_found:

        contact_score += 4

    else:

        issues_found.append(
            "GitHub profile missing"
        )
         
    # 5. Resume length

    word_count = len(
            resume_text.split()
        ) 
    if candidate_level.lower() == "fresher":
            
        if 350 <= word_count <= 700:
                
            length_score = 15

        elif 250 <= word_count <= 850:

            length_score = 10

        else:

            length_score = 5

    elif candidate_level.lower() == "mid":

        if 500 <= word_count <= 1100:

            length_score = 15

        else:

            length_score = 10

    else:

        if 700 <= word_count <= 1500:

            length_score = 15

        else:

            length_score = 10

    if length_score >= 12:

        strengths.append(
            "Resume length is ATS-friendly"
         )

    else:

        issues_found.append(
            "Resume length may not be ideal for the selected level"
        )
         
    # 6. ATS Parseability

    risk_symbol_count = sum(

        lower_resume_text.count(
            symbol.lower()
            )
            for symbol in ATS_RISK_SYMBOLS
            )

    if risk_symbol_count == 0:

        parseability_score = 25

        strengths.append(
            "Resume appears ATS parse-friendly"
        )

    elif risk_symbol_count <= 5:

        parseability_score = 18

        issues_found.append(
            "Minor ATS formatting risks detected"
        )

    else:

        parseability_score = 10

        issues_found.append(
            "Resume may contain ATS-unfriendly formatting or symbols"
        )
         
    # 7. FORMAT CONSISTENCY
    
    consistency_score = 10

    date_patterns = [

    r"\b\d{4}\b",

    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    ]

    found_date_patterns = 0

    for pattern in date_patterns:

        matches = re.findall(
            pattern,
            lower_resume_text
        )
        
        if matches:

         found_date_patterns += 1

    if found_date_patterns < len(date_patterns):

        consistency_score -= 3

        issues_found.append(
            "Date formatting may be inconsistent"
        )

    # 8.Bullet consistency check

    bullets = []

    for exp in resume_data.get(
         "experience",
        []
    ):

         bullets.extend(
            exp.get(
                "achievements",
                []
            )
        )

    for proj in resume_data.get(
         "projects",
        []
    ):

         bullets.extend(
            proj.get(
                "achievements",
                []
            )
        )

    short_bullets = 0

    for bullet in bullets:

        if len(bullet.split()) < 5:

            short_bullets += 1

    if short_bullets > 3:

        consistency_score -= 2

        issues_found.append(
            "Some bullets may be too short or inconsistent"
        )

    consistency_score = max(
         0,
        consistency_score
    )

    if consistency_score >= 8:

         strengths.append(
            "Resume formatting appears consistent"
        )

    # 9.FINAL ATS FORMAT SCORE

    ats_format_score = (

         section_score +
         contact_score +
         length_score +
         parseability_score +
         consistency_score

         )

    ats_format_score = min(
           100,
           round(ats_format_score, 2)
    )

    
    # 10.ATS FORMAT GRADE


    if ats_format_score >= 85:

         ats_grade = "Excellent"

    elif ats_format_score >= 70:

         ats_grade = "Good"

    elif ats_format_score >= 55:

         ats_grade = "Average"

    else:

         ats_grade = "Poor"

   
    # 11.FINAL OUTPUT

    return {

        "ats_format_score": ats_format_score,

        "ats_grade": ats_grade,

        "section_score": round(
             section_score,
            2
        ),

        "contact_score": round(
            contact_score,
            2
        ),

        "length_score": round(
            length_score,
            2
        ),

        "parseability_score": round(
            parseability_score,
            2
        ),

        "consistency_score": round(
            consistency_score,
            2
        ),

        "issues_found": list(
            set(issues_found)
        ),

        "strengths": list(
            set(strengths)
        )
    }





def compute_grammar_score(resume_data: dict,candidate_level="fresher") -> dict:

    #1. LEVEL-BASED CONFIGURATION

    LEVEL_SUMMARY_LIMITS = {

        "fresher": 55,

        "mid": 75,

        "senior": 100
    }

    summary_word_limit = LEVEL_SUMMARY_LIMITS.get(
        candidate_level.lower(),
        55
    )

    #2. CONFIGURATION

    ACTION_VERBS = [
        "built",
        "developed",
        "implemented",
        "engineered",
        "designed",
        "created",
        "performed",
        "led",
        "analyzed",
        "applied",
        "collaborated",
        "optimized",
        "deployed",
        "automated",
        "improved",
        "reduced",
        "increased",
        "extracted",
        "evaluated"
    ]

    IGNORE_PUNCTUATION_CASES = [
        "certificate",
        "certification",
        "bachelor",
        "master",
        "linkedin",
        "github"
    ]

    MAX_BULLET_WORDS = 35

    #3. INITIALIZATION

    grammar_score = 100

    issues_found = []

    strengths = []

    all_lines = []

    #4. HELPER FUNCTION

    def add_issue(issue_text, penalty=2):

        nonlocal grammar_score

        issues_found.append(issue_text)

        grammar_score -= penalty

    #5. SUMMARY ANALYSIS

    summary = resume_data.get(
        "summary",
        ""
    )

    if summary:

        summary_word_count = len(
            summary.split()
        )

        # Separate summary length validation
        if summary_word_count > summary_word_limit:

            add_issue(
                f"Summary may be too long for {candidate_level} level ({summary_word_count} words detected)",
                penalty=2
            )

        elif summary_word_count < 20:

            add_issue(
                "Summary may be too short or lack detail",
                penalty=2
            )

        else:

            strengths.append(
                "Professional summary length appears appropriate"
            )

        all_lines.append(summary)

    #6. EXPERIENCE ACHIEVEMENTS

    for exp in resume_data.get(
        "experience",
        []
    ):

        for achievement in exp.get(
            "achievements",
            []
        ):

            all_lines.append(achievement)

    #7. PROJECT ACHIEVEMENTS

    for proj in resume_data.get(
        "projects",
        []
    ):

        for achievement in proj.get(
            "achievements",
            []
        ):

            all_lines.append(achievement)

    #8. CERTIFICATIONS

    for cert in resume_data.get(
        "certifications",
        []
    ):

        cert_title = cert.get(
            "title",
            ""
        )

        if cert_title:

            all_lines.append(cert_title)

    #9. EXTRACURRICULARS

    for item in resume_data.get(
        "extracurricular",
        []
    ):

        all_lines.append(item)

    #10. ANALYZE EACH LINE
    for line in all_lines:
        if isinstance(line, dict):
            line_text = " ".join([str(v) for v in line.values() if isinstance(v, (str, int, float))])
        elif isinstance(line, list):
        # Handle if line is an array/list of words
           line_text = " ".join([str(item) for item in line])
        else:
        # Fallback for standard strings or numeric values
           line_text = str(line)

    # 2. Run your original string logic safely on the extracted text string
        clean_line = line_text.strip()
        lower_line = clean_line.lower()

        if not clean_line:
            continue
        word_count = len(clean_line.split())
    
    # 11. SKIP LONG SENTENCE CHECK FOR SUMMARY

        is_summary = (
            summary and clean_line == summary
        )

        if (
            not is_summary and
            word_count > MAX_BULLET_WORDS
        ):

            add_issue(
                f"Sentence may be too long for readability: '{clean_line}'",
                penalty=3
            )

    #12. PUNCTUATION CHECK

        should_ignore_punctuation = any(
            keyword in lower_line
            for keyword in IGNORE_PUNCTUATION_CASES
        )

        if (
            clean_line[-1] not in [".", "!", "?"]
            and not should_ignore_punctuation
        ):

            add_issue(
                f"Bullet may be missing ending punctuation: '{clean_line}'",
                penalty=2
            )

    #13. DOUBLE SPACE CHECK

        if "  " in clean_line:

            add_issue(
                f"Multiple consecutive spaces detected: '{clean_line}'",
                penalty=1
            )

    # 14. LOWERCASE START CHECK-

        first_char = clean_line[0]

        if (
            first_char.isalpha()
            and first_char.islower()
        ):

            add_issue(
                f"Sentence starts with lowercase letter: '{clean_line}'",
                penalty=2
            )

    #15. REPEATED WORD CHECK

        repeated_word_pattern = r"\b(\w+)\s+\1\b"

        repeated_words = re.search(
            repeated_word_pattern,
            lower_line
        )

        if repeated_words:

            add_issue(
                f"Repeated word detected: '{clean_line}'",
                penalty=2
            )

    #16. VERY SHORT BULLET CHECK

        if (
            not is_summary and
            word_count < 4
        ):

            add_issue(
                f"Very short sentence may lack clarity: '{clean_line}'",
                penalty=1
            )

     #17. STRONG ACTION VERB DETECTION

        starts_with_action_verb = any(
            lower_line.startswith(verb)
            for verb in ACTION_VERBS
        )

        if starts_with_action_verb:

            strengths.append(
                f"Strong action-oriented bullet detected: '{clean_line}'"
            )

    #18. NORMALIZE SCORE

    grammar_score = max(
        0,
        grammar_score
    )

    grammar_score = min(
        100,
        round(grammar_score, 2)
    )

    #19. QUALITY LABEL

    if grammar_score >= 90:

        grammar_quality = "Excellent"

    elif grammar_score >= 75:

        grammar_quality = "Good"

    elif grammar_score >= 60:

        grammar_quality = "Average"

    else:

        grammar_quality = "Poor"

    # 20. GENERAL STRENGTHS

    if grammar_score >= 90:

        strengths.append(
            "Resume writing quality appears excellent overall"
        )

    elif grammar_score >= 80:

        strengths.append(
            "Resume writing quality appears strong overall"
        )

    if len(issues_found) == 0:

        strengths.append(
            "No major grammar or readability issues detected"
        )

    #21. REMOVE DUPLICATES

    issues_found = list(
        set(issues_found)
    )

    strengths = list(
        set(strengths)
    )

    #22. FINAL OUTPUT

    return {

        "grammar_score": grammar_score,

        "grammar_quality": grammar_quality,

        "issues_found": issues_found,

        "strengths": strengths
    }


def compute_data_science_specific_score( resume_data: dict, jd: dict = None, candidate_level: str = "fresher") -> dict:


    MODELING_SIGNALS = [
        "regression",
        "classification",
        "clustering",
        "forecasting",
        "time-series",
        "transformer",
        "bert",
        "roberta",
        "neural network",
        "deep learning",
        "machine learning",
        "nlp",
        "llm",
        "rag"
    ]

    FEATURE_ENGINEERING_SIGNALS = [
        "feature engineering",
        "feature selection",
        "preprocessing",
        "normalization",
        "standardization",
        "encoding",
        "dimensionality reduction",
        "cleaning",
        "transformation"
    ]

    EVALUATION_SIGNALS = [
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc",
        "auc",
        "cross-validation",
        "confusion matrix",
        "evaluation",
        "benchmark",
        "validation"
    ]

    EXPERIMENTATION_SIGNALS = [
        "experiment",
        "ab testing",
        "tuning",
        "hyperparameter",
        "optimization",
        "compare",
        "evaluated multiple",
        "iteration"
    ]

    SCALE_SIGNALS = [
        "large-scale",
        "high-volume",
        "real-time",
        "pipeline",
        "distributed",
        "production",
        "streaming",
        "millions",
        "enterprise"
    ]

    PRODUCTION_SIGNALS = [
        "deployment",
        "deployed",
        "production",
        "api",
        "fastapi",
        "streamlit",
        "docker",
        "mlops",
        "ci/cd",
        "monitoring"
    ]

    TOOLCHAIN_SIGNALS = [
        "python",
        "sql",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "hugging face",
        "power bi",
        "tableau",
        "aws",
        "azure",
        "gcp"
    ]

    PIPELINE_SIGNALS = [
        "end-to-end",
        "pipeline",
        "workflow",
        "automation",
        "etl",
        "data preprocessing",
        "data extraction",
        "deployment"
    ]

    STATISTICS_SIGNALS = [
        "hypothesis testing",
        "probability",
        "statistics",
        "statistical analysis",
        "anova",
        "regression",
        "sampling",
        "distribution",
        "eda",
        "correlation"
    ]

    PROBLEM_FRAMING_SIGNALS = [
        "business problem",
        "decision-making",
        "stakeholder",
        "requirements",
        "analytics prototype",
        "optimization",
        "recommendation",
        "prediction",
        "insights"
    ]

    #2. Extract all text

    text_blocks = []

    if resume_data.get("summary"):
        text_blocks.append(resume_data["summary"])

    for exp in resume_data.get("experience",[]):

        text_blocks.append(exp.get("title",""))

        for achievement in exp.get("achievements",[]):
            text_blocks.append(achievement)

    for proj in resume_data.get("projects",[]):

        text_blocks.append(proj.get("title",""))

        for achievement in proj.get("achievements",[]):
            text_blocks.append(achievement)

    for skill in resume_data.get("skills",[]):
        text_blocks.append(skill)

    full_text = " ".join(text_blocks).lower()

    #3. Helper

    def count_matches(signals):

        matches = []

        for signal in signals:

            if signal.lower() in full_text:
                matches.append(signal)
        
        return list(set(matches))
    
    
    #4.signal detection
    modeling_hits = count_matches(
        MODELING_SIGNALS
    )

    feature_hits = count_matches(
        FEATURE_ENGINEERING_SIGNALS
    )

    evaluation_hits = count_matches(
        EVALUATION_SIGNALS
    )

    experimentation_hits = count_matches(
        EXPERIMENTATION_SIGNALS
    )

    scale_hits = count_matches(
        SCALE_SIGNALS
    )

    production_hits = count_matches(
        PRODUCTION_SIGNALS
    )

    toolchain_hits = count_matches(
        TOOLCHAIN_SIGNALS
    )

    pipeline_hits = count_matches(
        PIPELINE_SIGNALS
    )

    statistics_hits = count_matches(
        STATISTICS_SIGNALS
    )

    problem_framing_hits = count_matches(
        PROBLEM_FRAMING_SIGNALS
    )

    #5. project maturity
    project_maturity = (

        (len(modeling_hits) * 1.5) +
        (len(production_hits) * 1.5) +
        (len(scale_hits) * 1.2) +
        (len(pipeline_hits) * 1.2)

    )

    project_maturity = min(
        10,
        round(project_maturity, 1)
    )

    #6. MODELING RIGOR

    modeling_score = (

        len(modeling_hits) +
        len(evaluation_hits)
    )

    if modeling_score >= 10:
        modeling_rigor = "high"

    elif modeling_score >= 5:
        modeling_rigor = "medium"

    else:
        modeling_rigor = "low"

    #7. FEATURE ENGINEERING

    feature_engineering = min(
        10,
        round(
            len(feature_hits) * 1.5,
            1
        )
    )

    #EVALUATION DEPTH

    evaluation_score = len(evaluation_hits)

    if evaluation_score >= 8:
        evaluation_depth = "high"

    elif evaluation_score >= 4:
        evaluation_depth = "medium"

    else:
        evaluation_depth = "low"

    #EXPERIMENTATION

    experimentation = min(
        10,
        round(
            len(experimentation_hits) * 2,
            1
        )
    )

    #DATA SCALE AWARENESS-

    data_scale_awareness = min(
        10,
        round(
            len(scale_hits) * 2,
            1
        )
    )

    #PRODUCTION READINESS

    production_readiness = min(
        10,
        round(
            len(production_hits) * 1.8,
            1
        )
    )

    # TOOLCHAIN COHESION

    toolchain_cohesion = min(
        10,
        round(
            len(toolchain_hits) * 0.8,
            1
        )
    )

    # PIPELINE THINKING

    pipeline_thinking = min(
        10,
        round(
            len(pipeline_hits) * 1.7,
            1
        )
    )

    # STATISTICAL DEPTH

    statistical_depth = min(
        10,
        round(
            len(statistics_hits) * 1.5,
            1
        )
    )

    # PROBLEM FRAMING

    problem_framing = min(
        10,
        round(
            len(problem_framing_hits) * 1.8,
            1
        )
    )

    # LEVEL-BASED NORMALIZATION

    if candidate_level.lower() == "senior":

        project_maturity *= 0.9
        experimentation *= 0.85
        production_readiness *= 0.85

    elif candidate_level.lower() == "mid":

        project_maturity *= 0.95


    # ROUND FINAL SCORES

    project_maturity = round(project_maturity, 1)
    experimentation = round(experimentation, 1)
    production_readiness = round(production_readiness, 1)

    # FINAL OUTPUT

    return {

        "project_maturity": project_maturity,

        "modeling_rigor": modeling_rigor,

        "feature_engineering": feature_engineering,

        "evaluation_depth": evaluation_depth,

        "experimentation": experimentation,

        "data_scale_awareness": data_scale_awareness,

        "production_readiness": production_readiness,

        "toolchain_cohesion": toolchain_cohesion,

        "pipeline_thinking": pipeline_thinking,

        "statistical_depth": statistical_depth,

        "problem_framing": problem_framing,

        "detected_signals": {

            "modeling_signals": modeling_hits,

            "feature_engineering_signals": feature_hits,

            "evaluation_signals": evaluation_hits,

            "experimentation_signals": experimentation_hits,

            "scale_signals": scale_hits,

            "production_signals": production_hits,

            "toolchain_signals": toolchain_hits,

            "pipeline_signals": pipeline_hits,

            "statistics_signals": statistics_hits,

            "problem_framing_signals": problem_framing_hits
        }
    }


def compute_job_match_score(resume_data: dict,jd: dict, skill_analysis: dict,
                            project_analysis: dict, impact_analysis: dict, 
                            candidate_level = "fresher") -> dict:
    
    level_config = get_level_weights(candidate_level)

    # Extract existing scores

    skill_score = skill_analysis.get(
        "overall_fit_score", 0
    )

    project_score = project_analysis.get(
        "project_score", 0
    )

    impact_score = impact_analysis.get(
        "overall_impact_score",
        impact_analysis.get(
            "impact_score", 0
        )
        
    )

    # Extract Existing Varaiables

    missing_skills = skill_analysis.get(
        "missing_skills",
        []
    )


    projects_analyzed = project_analysis.get(
        "projects_analyzed",
        []
    )

    bullet_analysis = impact_analysis.get(
        "bullet_analysis",
        []
    )

    # Role alignment

    role_name = jd.get(
        "role",
        jd.get(
            "job_title",
            "unknown Role"
        )
    )

    role_summary = jd.get(
        "summary",
        ""
    ).lower()

    role_alignment = {
        "role": role_name,
        "alignement_strength": "Medium"
    }

    # Domain Detection

    detected_domains = set()

    # from projects

    for proj in projects_analyzed:

        for domain in proj.get(
            "domains",
            []
        ):
            detected_domains.add(domain)

    # from JD summary
    jd_detected_domains = set()

    for domain, keywords in DOMAIN_KEYWORDS.items():

        for keyword in keywords:

            if keyword in role_summary:

                jd_detected_domains.add(domain)

    # Domain Match Score

    matched_domain = []

    for domain in jd_detected_domains:

        normalized = domain.lower()

        for detected in detected_domains:

            if normalized in detected.lower():

                matched_domain.append(domain)

    matched_domain = list(
        set(matched_domain)
    )

    if len(jd_detected_domains) > 0:

        domain_match_score = (
            len(matched_domain)
            /
            len(jd_detected_domains)
        ) * 100

    else:

        domain_match_score = 70

    # Missing skill penalty

    missing_penalty = 0

    critical_missing = []

    for skill in missing_skills:

        lower_skill = skill.lower()

        if any(
            word in lower_skill
            for word in [
                "docker","kubernetes","rag","langchain","deep learning","deployment","ci/cd"]
        ):
            
            missing_penalty += 4
            critical_missing.append(skill)
        
        else:

            missing_penalty += 2

        # Experience Strength

        high_impact_bullets = 0

        for bullet in bullet_analysis:

            if bullet.get(
                "evidence_level"
            ) == "High":
                
                high_impact_bullets += 1

        if high_impact_bullets >= 4:
            experience_strength = "Strong"
            
            experience_bonus = 8

        elif high_impact_bullets >= 2:
            
            experience_strength = "Moderate"
            
            experience_bonus = 5

        else:
            experience_strength = "Weak"
            
            experience_bonus = 2

        # Advanced project bonus

        advanced_project_count = 0

        for proj in projects_analyzed:

          if proj.get(
            "evidence_level"
          ) == "High":

             advanced_project_count += 1

        project_bonus = advanced_project_count * 2

        # Final Match Score

        final_match_score = (
            (skill_score * 0.45) +
            (project_score * 0.20) +
            (impact_score * 0.20) +
            (domain_match_score *0.15)
        )

        final_match_score += experience_bonus
        final_match_score += project_bonus

        final_match_score -= missing_penalty

        # Level Normalization

        role_multiplier = level_config.get(
        "job_match_multiplier",
        1.0
        )

        final_match_score *= role_multiplier

        final_match_score = max(
           0,
           min(
              100,
              round(final_match_score, 2)
               )
        )

        # Match Quality

        if final_match_score >= 85:

         match_quality = "Excellent Match"

         role_alignment[
            "alignment_strength"
          ] = "Strong"

        elif final_match_score >= 70:

         match_quality = "Good Match"

         role_alignment[
            "alignment_strength"
         ] = "Good"

        elif final_match_score >= 55:

         match_quality = "Moderate Match"

         role_alignment[
            "alignment_strength"
        ] = "Moderate"

        else:

         match_quality = "Weak Match"

         role_alignment[
            "alignment_strength"
        ] = "Weak"

    # -----------------------------------
    # 12. RETURN
    # -----------------------------------

        return {

          "match_score": final_match_score,

          "match_quality": match_quality,

          "missing_skills": missing_skills,

          "critical_missing_skills": critical_missing,

          "matched_domains": matched_domain,

          "domain_match_score": round(
            domain_match_score,
            2
          ),

          "experience_strength": experience_strength,

          "advanced_project_count": advanced_project_count,

          "role_alignment": role_alignment,

          "score_breakdown": {

              "skill_score": round(
                skill_score,
                2
              ),

              "project_score": round(
                project_score,
                2
              ),

              "impact_score": round(
                impact_score,
                2
              ),

              "domain_score": round(
                domain_match_score,
                2
              ),

              "experience_bonus": experience_bonus,

              "project_bonus": project_bonus,

              "missing_skill_penalty": missing_penalty
          }
      }



def generate_recruiter_flags(resume_data: dict, jd: dict, skill_analysis: dict,
                             project_analysis: dict, impact_analysis: dict, 
                             ats_format_score: dict, grammar_score: dict, 
                             data_science_specific: dict,job_match: dict,
                             candidate_level = "fresher") -> dict:
    
    import json

    # -----------------------------------
    # 1. ROLE DETECTION
    # -----------------------------------

    target_role = jd.get(
        "role",
        jd.get(
            "job_title",
            "Data Science Role"
        )
    )

    # -----------------------------------
    # 2. IMPORTANT SCORE EXTRACTION
    # -----------------------------------

    skill_score = skill_analysis.get(
        "overall_fit_score",
        0
    )

    project_score = project_analysis.get(
        "project_score",
        0
    )

    impact_score = impact_analysis.get(
        "overall_impact_score",
        impact_analysis.get(
            "impact_score",
            0
        )
    )

    ats_score = ats_format_score.get(
        "ats_format_score",
        0
    )

    grammar_value = grammar_score.get(
        "grammar_score",
        0
    )

    job_match_score = job_match.get(
        "match_score",
        0
    )

    # -----------------------------------
    # 3. IMPORTANT DETAILS
    # -----------------------------------

    missing_skills = skill_analysis.get(
        "missing_skills",
        []
    )

    partial_requirements = skill_analysis.get(
        "partial_requirements",
        []
    )

    project_details = project_analysis.get(
        "projects_analyzed",
        []
    )

    strongest_bullet = impact_analysis.get(
        "strongest_impact_bullet",
        ""
    )

    quantified_achievements = impact_analysis.get(
        "quantified_achievements",
        0
    )

    production_readiness = data_science_specific.get(
        "production_readiness",
        0
    )

    experimentation = data_science_specific.get(
        "experimentation",
        0
    )

    pipeline_thinking = data_science_specific.get(
        "pipeline_thinking",
        0
    )

    evaluation_depth = data_science_specific.get(
        "evaluation_depth",
        "low"
    )

    modeling_rigor = data_science_specific.get(
        "modeling_rigor",
        "low"
    )

    # -----------------------------------
    # 4. RESUME SNAPSHOT
    # -----------------------------------

    summary = resume_data.get(
        "summary",
        ""
    )

    experience = resume_data.get(
        "experience",
        []
    )

    projects = resume_data.get(
        "projects",
        []
    )

    # -----------------------------------
    # 5. PROMPT
    # -----------------------------------

    recruiter_prompt = f"""
You are a senior technical recruiter hiring for:
{target_role}

Your task:
Generate realistic recruiter-style hiring observations for this resume.

IMPORTANT:
- Sound HUMAN.
- Sound like an actual recruiter or hiring manager and write like internal recruiter notes..
- Be concise and practical.
- Avoid robotic statements like "X is missing".
- Give honest hiring concerns and strengths.
- Focus ONLY on recruiter-relevant observations.
- Do NOT explain scores.
- Do NOT summarize the resume.
- Do NOT praise excessively.
- Comments should feel like internal recruiter notes.
- Avoid repeating the same concern in different wording.
- Combine similar concerns into one concise recruiter comment.
- Use natural recruiter phrasing.
- Prefer nuanced observations over blunt criticism.

Return ONLY valid JSON.

Format:
{{
  "recruiter_flags": [
    "comment 1",
    "comment 2",
    "comment 3"
  ],

  "recruiter_strengths": [
    "strength 1",
    "strength 2"
  ],

  "recruiter_recommendation": "Short final recruiter recommendation"
}}

Candidate Level:
{candidate_level}

Scores:
- Skill Score: {skill_score}
- Project Score: {project_score}
- Impact Score: {impact_score}
- ATS Score: {ats_score}
- Grammar Score: {grammar_value}
- Job Match Score: {job_match_score}

Missing Skills:
{missing_skills}

Partial Requirements:
{partial_requirements}

Production Readiness:
{production_readiness}

Experimentation:
{experimentation}

Pipeline Thinking:
{pipeline_thinking}

Evaluation Depth:
{evaluation_depth}

Modeling Rigor:
{modeling_rigor}

Quantified Achievements:
{quantified_achievements}

Strongest Impact Bullet:
{strongest_bullet}

Projects:
{json.dumps(project_details, indent=2)}

Resume Summary:
{summary}

Experience:
{json.dumps(experience, indent=2)}

Additional Instructions:
- Mention if projects feel academic/tutorial-like.
- Mention if deployment exposure is weak.
- Mention if business impact is weak.
- Mention if resume feels strong for fresher level.
- Mention if production exposure is missing.
- Mention if resume lacks measurable results.
- Mention if candidate shows good ownership.
- Mention if candidate has strong AI/ML fundamentals.
- Mention if candidate lacks system design maturity.
- Mention if candidate looks better for analyst vs engineer roles.
- Mention if profile appears over-keyword optimized.
- Mention if resume feels practical and implementation-focused.
"""

    # -----------------------------------
    # 6. GROQ CALL
    # -----------------------------------

    try:

        completion = client.chat.completions.create(

            model="llama-3.1-8b-instant",

             temperature=0.7,

             messages=[

               {
                  "role": "system",
                   "content": (
                    "You are an experienced senior recruiter "
                    "for AI, ML, Data Science, Analytics, "
                    "and Data Engineering roles."
                   )
                },

               {
                 "role": "user",
                 "content": recruiter_prompt
                }
            ]
       )

        response_text = (
          completion.choices[0]
          .message.content
          .strip()
        )

    # -----------------------------------
    # CLEAN RESPONSE
    # -----------------------------------

        response_text = response_text.replace(
            "```json",
            ""
        )

        response_text = response_text.replace(
          "```",
          ""
        ).strip()

    # -----------------------------------
    # EXTRACT JSON SAFELY
    # -----------------------------------

        json_start = response_text.find("{")

        json_end = response_text.rfind("}")

        if json_start == -1 or json_end == -1:

          raise ValueError(
            "No valid JSON found in GROQ response"
          )

        cleaned_json = response_text[
         json_start: json_end + 1
       ]

        parsed_response = json.loads(
         cleaned_json
        )

        return parsed_response

# -----------------------------------
# 7. FALLBACK
# -----------------------------------

    except Exception as e:

       return {

           "recruiter_flags": [
              "Could not generate recruiter insights"
            ],

            "recruiter_strengths": [],

           "recruiter_recommendation": (
            f"GROQ generation failed: {str(e)}"
           )
        }

def calculate_overall_ats_score(
    skill_analysis,
    project_analysis,
    impact_analysis,
    ats_format_score,
    grammar_score,
    data_science_specific,
    jd_match_score,
    recruiter_flags=None
):
    """
    Calculates FINAL OVERALL ATS SCORE out of 100.

    This score combines:
    - ATS formatting
    - Grammar quality
    - JD alignment
    - Technical depth
    - Projects
    - Business impact
    - DS/ML maturity
    - Recruiter concerns

    Returns recruiter-style ATS evaluation.
    """

    # =========================================================
    # EXTRACT SCORES
    # =========================================================

    format_score = ats_format_score.get("ats_format_score", 0)
    grammar = grammar_score.get("grammar_score", 0)

    skill_score = skill_analysis.get("overall_fit_score", 0)

    project_score = project_analysis.get("project_score", 0)

    impact_score = impact_analysis.get("overall_impact_score", 0)

    jd_score = jd_match_score.get("match_score", 0)

    credibility = skill_analysis.get("resume_credibility_index", 0) * 100

    # =========================================================
    # DATA SCIENCE SPECIFIC SCORING
    # =========================================================

    ds_score_components = []

    ds_score_components.append(
        data_science_specific.get("project_maturity", 0) * 10
    )

    ds_score_components.append(
        data_science_specific.get("feature_engineering", 0) * 10
    )

    ds_score_components.append(
        data_science_specific.get("production_readiness", 0) * 10
    )

    ds_score_components.append(
        data_science_specific.get("toolchain_cohesion", 0) * 10
    )

    ds_score_components.append(
        data_science_specific.get("pipeline_thinking", 0) * 10
    )

    ds_score_components.append(
        data_science_specific.get("statistical_depth", 0) * 10
    )

    ds_score_components.append(
        data_science_specific.get("problem_framing", 0) * 10
    )

    # Modeling rigor mapping
    rigor_map = {
        "low": 40,
        "medium": 70,
        "high": 90
    }

    ds_score_components.append(
        rigor_map.get(
            data_science_specific.get("modeling_rigor", "medium").lower(),
            70
        )
    )

    # Evaluation depth mapping
    eval_map = {
        "low": 40,
        "medium": 70,
        "high": 90
    }

    ds_score_components.append(
        eval_map.get(
            data_science_specific.get("evaluation_depth", "medium").lower(),
            70
        )
    )

    ds_maturity_score = round(
        sum(ds_score_components) / len(ds_score_components),
        2
    )

    # =========================================================
    # WEIGHTED ATS SCORE
    # =========================================================

    weighted_score = (
        format_score * 0.15 +          # ATS structure
        grammar * 0.08 +               # Writing quality
        skill_score * 0.18 +           # Skill alignment
        project_score * 0.15 +         # Project quality
        impact_score * 0.12 +          # Business impact
        jd_score * 0.22 +              # JD alignment
        ds_maturity_score * 0.10       # Technical maturity
    )

    # =========================================================
    # CREDIBILITY BONUS / PENALTY
    # =========================================================

    credibility_bonus = 0

    if credibility >= 60:
        credibility_bonus += 3

    elif credibility >= 40:
        credibility_bonus += 1

    elif credibility < 20:
        credibility_bonus -= 3

    # =========================================================
    # RECRUITER FLAG PENALTY
    # =========================================================

    recruiter_penalty = 0

    if recruiter_flags:

        flags = recruiter_flags.get("recruiter_flags", [])

        # Max penalty capped
        recruiter_penalty = min(len(flags) * 1.2, 8)

    # =========================================================
    # FINAL SCORE
    # =========================================================

    final_score = (
        weighted_score
        + credibility_bonus
        - recruiter_penalty
    )

    final_score = max(0, min(100, round(final_score, 2)))

    # =========================================================
    # SCORE BAND
    # =========================================================

    if final_score >= 85:
        overall_rating = "Excellent"

    elif final_score >= 75:
        overall_rating = "Strong"

    elif final_score >= 65:
        overall_rating = "Good"

    elif final_score >= 50:
        overall_rating = "Average"

    else:
        overall_rating = "Weak"

    # =========================================================
    # HIRING PROBABILITY
    # =========================================================

    if final_score >= 85:
        hiring_probability = "High Interview Probability"

    elif final_score >= 75:
        hiring_probability = "Good Interview Probability"

    elif final_score >= 65:
        hiring_probability = "Moderate Interview Probability"

    elif final_score >= 50:
        hiring_probability = "Low Interview Probability"

    else:
        hiring_probability = "Very Low Interview Probability"

    # =========================================================
    # STRENGTHS
    # =========================================================

    strengths = []

    if format_score >= 90:
        strengths.append("Excellent ATS formatting and structure")

    if grammar >= 90:
        strengths.append("Strong resume writing quality")

    if skill_score >= 70:
        strengths.append("Strong technical skill alignment")

    if jd_score >= 70:
        strengths.append("Good alignment with target job role")

    if impact_score >= 65:
        strengths.append("Good business impact and ownership signals")

    if ds_maturity_score >= 70:
        strengths.append("Good technical and ML project maturity")

    # =========================================================
    # WEAKNESSES
    # =========================================================

    weaknesses = []

    if project_score < 45:
        weaknesses.append(
            "Projects lack strong production-grade complexity"
        )

    if credibility < 20:
        weaknesses.append(
            "Several skills lack strong project/work evidence"
        )

    if impact_analysis.get("quantified_achievements", 0) <= 1:
        weaknesses.append(
            "Resume lacks quantified business impact"
        )

    if data_science_specific.get("production_readiness", 0) < 6:
        weaknesses.append(
            "Limited deployment and production exposure"
        )

    if len(jd_match_score.get("critical_missing_skills", [])) > 0:
        weaknesses.append(
            "Critical missing skills reduce role alignment"
        )

    # =========================================================
    # RETURN
    # =========================================================

    return {
        "overall_ats_score": final_score,
        "overall_rating": overall_rating,
        "hiring_probability": hiring_probability,

        "score_breakdown": {
            "ats_format": round(format_score, 2),
            "grammar": round(grammar, 2),
            "skills": round(skill_score, 2),
            "projects": round(project_score, 2),
            "impact": round(impact_score, 2),
            "jd_match": round(jd_score, 2),
            "ds_ml_maturity": round(ds_maturity_score, 2),
            "resume_credibility": round(credibility, 2),
            "recruiter_penalty": round(recruiter_penalty, 2),
            "credibility_bonus": round(credibility_bonus, 2)
        },

        "top_strengths": strengths[:5],

        "top_weaknesses": weaknesses[:5]
    }


def generate_resume_roadmap(analysis):
    roadmap = []

    skill_analysis = analysis.get("skill_analysis", {})
    project_analysis = analysis.get("project_analysis", {})
    ats_format = analysis.get("ats_format_score", {})
    impact = analysis.get("impact_analysis", {})

    # Missing skills
    missing_skills = skill_analysis.get("missing_skills", [])

    if missing_skills:
        roadmap.append({
            "priority": 1,
            "title": "Add Missing Skills",
            "impact": "+10 to +15 ATS score",
            "action": f"Add practical evidence for skills like {', '.join(missing_skills[:3])} through projects or experience bullets."
        })

    # Weak projects
    weak_projects = [
        p for p in project_analysis.get("projects_analyzed", [])
        if p.get("complexity_score", 0) < 5
    ]

    if weak_projects:
        roadmap.append({
            "priority": 2,
            "title": "Strengthen Projects",
            "impact": "+10 ATS score",
            "action": "Add deployment, APIs, dashboards, or production-level features to your projects."
        })

    # Low quantified metrics
    if impact.get("quantified_achievements", 0) < 5:
        roadmap.append({
            "priority": 3,
            "title": "Increase Quantified Impact",
            "impact": "+5 to +8 ATS score",
            "action": "Add measurable metrics such as accuracy, performance improvement, revenue impact, or automation savings."
        })

    # ATS formatting
    if ats_format.get("ats_format_score", 100) < 85:
        roadmap.append({
            "priority": 4,
            "title": "Improve ATS Formatting",
            "impact": "+5 ATS score",
            "action": "Use single-column layout, standard headings, and ATS-friendly formatting."
        })

    return roadmap