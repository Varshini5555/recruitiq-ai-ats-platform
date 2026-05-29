export interface AnalysisData {
  jd_source: string;
  jd_role: string;

  "Overall ATS score": {
    overall_ats_score: number;
    overall_rating: string;
    hiring_probability: string;

    score_breakdown: {
      ats_format: number;
      grammar: number;
      skills: number;
      projects: number;
      impact: number;
      jd_match: number;
      ds_ml_maturity: number;
      resume_credibility: number;
      recruiter_penalty: number;
      credibility_bonus: number;
    };

    top_strengths: string[];
    top_weaknesses: string[];
  };

  skill_analysis: any;
  project_analysis: any;
  impact_analysis: any;
  ats_format_score: any;
  grammar_score: any;
  data_science_specific: any;
  jd_match_score: any;
  recruiter_flags: any;
}