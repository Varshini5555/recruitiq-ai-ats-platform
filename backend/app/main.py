from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.parser import (
    extract_text_from_pdf,
    parse_resume_llm,
)

from app.scorer import (
    get_jd,
    load_jd,
    calculate_overall_ats_score,
    compute_skill_score,
    generate_recruiter_flags,
    compute_project_score,
    compute_job_match_score,
    compute_impact_score,
    compute_ats_format_score,
    load_custom_jd,
    compute_grammar_score,
    compute_data_science_specific_score,
    generate_resume_roadmap

)

import traceback

app = FastAPI()

# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================
# ROOT ROUTE
# =========================================

@app.get("/")
async def root():
    return {
        "message": "ATS Resume Analyzer Backend Running"
    }

# =========================================
# MAIN ANALYSIS ROUTE
# =========================================

@app.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...),

    jd_mode: str = Form("system"),

    role: str = Form(None),

    level: str = Form("fresher"),

    jd_text: str = Form(None),
):

    # =====================================
    # FILE VALIDATION
    # =====================================

    if not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files allowed"
        }

    try:

        # =====================================
        # INPUT CLEANING
        # =====================================

        jd_mode = jd_mode.lower()

        role = role.lower() if role else None

        level = level.lower()

        jd_text = jd_text.strip() if jd_text else None

        # =====================================
        # LOAD JD
        # =====================================

        if jd_text:

            structured_jd = load_custom_jd(jd_text)

        else:

            structured_jd = load_jd(role)

        if not structured_jd:

            raise ValueError(
                "Failed to load JD"
            )

        # =====================================
        # EXTRACT RESUME TEXT
        # =====================================

        resume_text = extract_text_from_pdf(file.file)

        # =====================================
        # PARSE RESUME
        # =====================================

        parsed_resume = parse_resume_llm(
            resume_text
        )

        # =====================================
        # GET JD INFO
        # =====================================

        if jd_mode == "custom":

            jd = get_jd(jd_text=jd_text)

            jd_source = "custom"

        else:

            jd = get_jd(role=role)

            jd_source = "system"

        # =====================================
        # SKILL SCORE
        # =====================================

        skill_score = compute_skill_score(
            parsed_resume,
            structured_jd,
        )

        # =====================================
        # PROJECT SCORE
        # =====================================

        project_score = compute_project_score(
            parsed_resume,
            structured_jd,
            candidate_level=level,
        )

        # =====================================
        # IMPACT SCORE
        # =====================================

        impact_score = compute_impact_score(
            resume_data=parsed_resume,
            jd=structured_jd,
            skill_analysis=skill_score,
            project_analysis=project_score,
            candidate_level=level,
        )

        # =====================================
        # ATS FORMAT SCORE
        # =====================================

        ats_format_score = compute_ats_format_score(
            resume_data=parsed_resume,
            candidate_level=level,
        )

        # =====================================
        # GRAMMAR SCORE
        # =====================================

        grammar_score = compute_grammar_score(
            resume_data=parsed_resume
        )

        # =====================================
        # DS / ML SCORE
        # =====================================

        data_science_specific = (
            compute_data_science_specific_score(
                resume_data=parsed_resume,
                jd=structured_jd,
                candidate_level=level,
            )
        )

        # =====================================
        # JD MATCH SCORE
        # =====================================

        jd_match_score = compute_job_match_score(
            parsed_resume,
            structured_jd,
            skill_score,
            project_score,
            impact_score,
            level,
        )

        # =====================================
        # RECRUITER REVIEW
        # =====================================

        recruiter_flags = generate_recruiter_flags(
            resume_data=parsed_resume,
            jd=structured_jd,
            skill_analysis=skill_score,
            project_analysis=project_score,
            impact_analysis=impact_score,
            ats_format_score=ats_format_score,
            grammar_score=grammar_score,
            data_science_specific=data_science_specific,
            job_match=jd_match_score,
            candidate_level=level,
        )

        # =====================================
        # OVERALL ATS SCORE
        # =====================================

        overall_ats_score = (
            calculate_overall_ats_score(
                skill_analysis=skill_score,
                project_analysis=project_score,
                impact_analysis=impact_score,
                ats_format_score=ats_format_score,
                grammar_score=grammar_score,
                data_science_specific=data_science_specific,
                jd_match_score=jd_match_score,
                recruiter_flags=recruiter_flags,
            )
        )

        analysis = {
      "Overall ATS score": overall_ats_score,
       "skill_analysis": skill_score,
       "project_analysis": project_score,
       "impact_analysis": impact_score,
       "ats_format_score": ats_format_score,
      "grammar_score": grammar_score,
       "jd_match_score": jd_match_score,
}

        resume_roadmap = generate_resume_roadmap(analysis)

        # =====================================
        # FINAL RESPONSE
        # =====================================

        return {

            "filename": file.filename,

            "jd_source": jd_source,

            "jd_role": jd.get(
                "role",
                "Not specified"
            ),

            "Overall ATS score": overall_ats_score,

            "skill_analysis": skill_score,

            "project_analysis": project_score,

            "impact_analysis": impact_score,

            "ats_format_score": ats_format_score,

            "grammar_score": grammar_score,

            "data_science_specific": data_science_specific,

            "jd_match_score": jd_match_score,

            "recruiter_flags": recruiter_flags,

            "suggested_improvements": resume_roadmap
        }

    except Exception as e:

        print(traceback.format_exc())

        return {
            "error": str(e)
        }
