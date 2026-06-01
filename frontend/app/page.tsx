"use client";

import React, { useState } from "react";
import {
  Upload,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Briefcase,
  BrainCircuit,
  ShieldCheck,
  BadgeCheck,
  Award,
} from "lucide-react";

import ScoreBadge from "@/components/ScoreBadge";
import SectionCard from "@/components/SectionCard";
import StatusPill from "@/components/StatusPill";

import { analyzeResume } from "@/services/api";

export default function ATSResumeAnalyzer() {
  const [resume, setResume] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [role, setRole] = useState("");
  const [level, setLevel] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any | null>(null);

  const handleAnalyze = async () => {
    if (!resume || !role || !level) {
      alert("Please upload a resume and select your target role + level");
      return;
    }

    setLoading(true);
    try {
      const data = await analyzeResume(
        resume,
        role,
        level,
        jdText.trim() ? jdText.trim() : undefined
      );
      setAnalysis(data);
    } catch (error) {
      console.error(error);
      alert("Failed to analyze resume payload");
    } finally {
      setLoading(false);
    }
  };

  // ========================================================
  // ROOT DATA FIXES: MULTI-KEY FALLBACK EXTRACTOR (NO DRIFT)
  // ========================================================
  const targetAtsBlock =
    analysis?.["Overall ATS score"] ||
    analysis?.["overall_ats_score"] ||
    analysis?.["Overall_ATS_score"] ||
    analysis?.["ats_score"] ||
    analysis;

  const rawScoreValue =
    targetAtsBlock?.overall_ats_score ??
    targetAtsBlock?.overallScore ??
    targetAtsBlock?.score ??
    analysis?.overall_ats_score ?? 0;

  // CHANGE 3: Use Math.round() everywhere — standard rounding (≥.5 rounds up)
  const overallScore = Math.round(Number(rawScoreValue));

  const breakdownWeights =
    targetAtsBlock?.score_breakdown ||
    analysis?.score_breakdown ||
    {};

  const credibilityIndexVal = analysis?.skill_analysis?.resume_credibility_index ?? 0;

  const dsReadinessScore = breakdownWeights?.ds_ml_maturity
    ? Math.round(Number(breakdownWeights.ds_ml_maturity))
    : 0;

  const getRecruiterVerdict = (score: number) => {
    if (score >= 85) return { text: "Strong Hire", color: "bg-green-600 text-white" };
    if (score >= 70) return { text: "Consider/Interview", color: "bg-blue-600 text-white" };
    if (score >= 50) return { text: "Needs Improvement", color: "bg-amber-500 text-white" };
    return { text: "Not Recommended Yet", color: "bg-red-600 text-white" };
  };
  const verdict = getRecruiterVerdict(overallScore);

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* DASHBOARD HERO HEADER */}
        <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 rounded-3xl p-8 text-white shadow-xl border border-slate-700/50">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20">
                <BrainCircuit className="w-12 h-12 text-indigo-400" />
              </div>
              <div>
                {/* CHANGE 1: increased heading size */}
                <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
                  AI Resume Reviewer & Matcher
                </h1>
                <p className="text-slate-400 mt-1 text-base md:text-lg">
                  Instant recruiter intelligence, skill verification, and metric alignment reports
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* INPUT SETUP CONTROL PANEL */}
        {/* CHANGE 2: SectionCard titles use text-indigo-400 — passed via titleClassName prop if supported,
            otherwise override inline. Since SectionCard renders the title internally, we rely on
            the title prop; the color change below is applied to all inline section headings we control directly. */}
        <SectionCard title="Upload & Target Setup">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="border-2 border-dashed border-slate-200 hover:border-indigo-400 rounded-2xl p-6 bg-slate-50/50 transition-all group flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Upload className="text-slate-400 group-hover:text-indigo-500 transition-colors" />
                  {/* CHANGE 1 & 2: larger text, indigo color */}
                  <h3 className="font-semibold text-base text-indigo-900">Resume Upload (Required)</h3>
                </div>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setResume(e.target.files?.[0] || null)}
                  className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-slate-900 file:text-white hover:file:bg-slate-800 cursor-pointer"
                />
              </div>
              {resume && (
                <div className="mt-4 p-4 bg-white border border-slate-100 rounded-xl space-y-1.5 text-sm text-slate-600 shadow-sm">
                  <p><strong>File Name:</strong> {resume.name}</p>
                  <p><strong>File Size:</strong> {Math.round(resume.size / 1024)} KB</p>
                  <div className="flex items-center gap-1.5 text-emerald-600 font-medium pt-1">
                    <CheckCircle2 className="w-4 h-4" /> Ready for parsing validation
                  </div>
                </div>
              )}
            </div>

            <div className="border border-slate-200 rounded-2xl p-6 bg-slate-50/50 flex flex-col justify-between">
              <div className="w-full">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Briefcase className="text-slate-400" />
                    {/* CHANGE 1 & 2 */}
                    <h3 className="font-semibold text-base text-indigo-900">Job Description Profile (Optional)</h3>
                  </div>
                  <div>
                    {jdText.trim() ? (
                      <StatusPill text="Custom JD Detected" type="green" />
                    ) : (
                      <StatusPill text="Using System JD" type="blue" />
                    )}
                  </div>
                </div>
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste the job requirements, duties, or full job description text here..."
                  className="w-full h-32 border border-slate-200 rounded-xl p-3 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none shadow-inner"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div>
              {/* CHANGE 1: bumped label size */}
              <label className="block text-base font-semibold text-indigo-900 mb-2">Specialization</label>
              <select
                className="w-full border border-slate-200 rounded-xl p-3 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="">Select Target Domain</option>
                <option value="ai_engineer">AI Engineer / GenAI Engineer</option>
                <option value="ml_engineer">ML Engineer</option>
                <option value="data_scientist">Data Scientist</option>
                <option value="data_engineer">Data Engineer</option>
                <option value="data_analyst">Data Analyst</option>
              </select>
            </div>

            <div>
              <label className="block text-base font-semibold text-indigo-900 mb-2">Seniority</label>
              <select
                className="w-full border border-slate-200 rounded-xl p-3 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                value={level}
                onChange={(e) => setLevel(e.target.value)}
              >
                <option value="">Select Band Grade</option>
                <option value="fresher">Fresher (0 - 2 Years)</option>
                <option value="mid">Mid-Level (3 - 4 Years)</option>
                <option value="senior">Senior Executive (5+ Years)</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-6 w-full md:w-auto bg-slate-900 hover:bg-slate-800 text-white font-semibold px-8 py-3.5 rounded-xl text-base transition-all shadow-md active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? "Processing the resume..." : "Analyze Profile"}
          </button>
        </SectionCard>

        {/* RESULTS REPORT CONTAINER */}
        {analysis && (
          <>
            {/* ROW 1: SCORE BADGE & STRATEGIC ROADMAP */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1 bg-white border border-slate-200 rounded-2xl p-6 flex flex-col justify-center items-center text-center shadow-sm relative overflow-hidden">
                <span className="absolute top-4 right-4 text-xs uppercase font-bold tracking-wider text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">OVERALL ATS Score</span>
                <ScoreBadge score={overallScore} />
                <div className="mt-4 space-y-1">
                  {/* CHANGE 1 & 2 */}
                  <h2 className="text-2xl font-bold text-indigo-900">{targetAtsBlock?.overall_rating ?? "Evaluated Match"}</h2>
                  <p className="text-slate-500 font-medium text-base">{targetAtsBlock?.hiring_probability}</p>
                </div>
              </div>

              <div className="lg:col-span-2 bg-slate-900 text-white border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-sm relative overflow-hidden">
                <div>
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                    {/* CHANGE 1 & 2 */}
                    <h3 className="font-bold text-xl text-indigo-400 flex items-center gap-2">
                      🚀 Fastest Paths to Increase Your Score
                    </h3>
                    <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2.5 py-0.5 rounded-lg font-semibold border border-indigo-500/30">
                      Action Steps
                    </span>
                  </div>

                  <div className="space-y-3 max-h-56 overflow-y-auto pr-1">
                    {analysis?.suggested_improvements?.map((item: any, idx: number) => (
                      <div key={idx} className="flex items-start gap-3 bg-slate-800/40 p-2.5 rounded-xl border border-slate-800/60 hover:border-slate-700 transition-colors">
                        <span className="text-emerald-400 font-bold shrink-0 bg-emerald-500/10 px-2 py-0.5 rounded text-xs min-w-[90px] text-center">
                          {item.impact}
                        </span>
                        <div>
                          {/* CHANGE 1 */}
                          <h5 className="text-sm font-bold text-slate-200">{item.title}</h5>
                          <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{item.action}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="text-xs text-slate-500 italic pt-4 border-t border-slate-800/60 mt-4">
                  *Addressing these structural context gaps helps pass the high-weight filters recruiters configure on inbound boards.
                </div>
              </div>
            </div>

            {/* CLASSIFICATION SUMMARY */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between border-b pb-3 mb-4">
                {/* CHANGE 1 & 2 */}
                <h3 className="font-bold text-indigo-900 text-xl">Classification Insights</h3>
                <span className={`px-3 py-1 rounded-xl text-sm font-bold ${verdict.color}`}>
                  Verdict: {verdict.text}
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  {/* CHANGE 1 */}
                  <p className="text-xs font-bold text-slate-400 uppercase">Target Role Focus</p>
                  <p className="text-base font-semibold text-slate-700 mt-1 truncate">{analysis.jd_role}</p>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p className="text-xs font-bold text-slate-400 uppercase">Profile Credibility</p>
                  {/* CHANGE 3: Math.round instead of toFixed(0) */}
                  <p className="text-base font-semibold text-slate-700 mt-1">{Math.round(credibilityIndexVal * 100)}% Match</p>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p className="text-xs font-bold text-slate-400 uppercase">Source Vector</p>
                  <p className="text-base font-semibold text-slate-700 mt-1 capitalize">{analysis.jd_source} Option</p>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p className="text-xs font-bold text-slate-400 uppercase">Quantified Bullets</p>
                  <p className="text-base font-semibold text-slate-700 mt-1">{analysis?.impact_analysis?.quantified_achievements ?? 0} Detected</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-4 border-t border-slate-100">
                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-emerald-600 flex items-center gap-1 mb-1.5">
                    <CheckCircle2 className="w-4 h-4" /> Core Structural Strengths
                  </h4>
                  <p className="text-sm text-slate-500 line-clamp-2">{targetAtsBlock?.top_strengths?.[0] || "Valid layout metrics detected"}</p>
                </div>
                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-amber-600 flex items-center gap-1 mb-1.5">
                    <AlertTriangle className="w-4 h-4" /> High-Priority Deficiencies
                  </h4>
                  <p className="text-sm text-slate-500 line-clamp-2">{targetAtsBlock?.top_weaknesses?.[0] || "Profile modifications suggested"}</p>
                </div>
              </div>
            </div>

            {/* WEIGHT SCORE BREAKDOWN TABLE */}
            <SectionCard title="Score Breakdown">
              <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50/70 border-b border-slate-200 text-xs font-bold text-slate-400 uppercase">
                      {/* CHANGE 1 */}
                      <th className="p-4 text-sm">Engine Criteria Metric</th>
                      <th className="p-4 text-center text-sm">Calculated Input</th>
                      <th className="p-4 text-center text-sm">System Weight Allocation</th>
                      <th className="p-4 text-right text-sm">Net Contribution</th>
                    </tr>
                  </thead>
                  <tbody className="text-base text-slate-600 divide-y divide-slate-100">
                    {[
                      { name: "ATS Blueprint Layout Alignment", key: "ats_format", w: "10%" },
                      { name: "Syntactical & Grammar Accuracy Quality", key: "grammar", w: "5%" },
                      { name: "Core Skill Requirements Vector Match", key: "skills", w: "25%" },
                      { name: "Technical Portfolio Pipeline Verification", key: "projects", w: "20%" },
                      { name: "Quantified Metrics & Business Performance", key: "impact", w: "15%" },
                      { name: "Job Description Overlap Density Match", key: "jd_match", w: "15%" },
                      { name: "Applied Data Engineering Readiness Maturity", key: "ds_ml_maturity", w: "10%" },
                    ].map((row) => {
                      const rawInput = Number(breakdownWeights[row.key] ?? 0);
                      // CHANGE 3: Math.round for both columns
                      const netContribution = (rawInput * parseFloat(row.w)) / 100;
                      return (
                        <tr key={row.key} className="hover:bg-slate-50/50 transition-all">
                          <td className="p-4 font-medium text-slate-800">{row.name}</td>
                          <td className="p-4 text-center font-semibold">{Math.round(rawInput)}%</td>
                          <td className="p-4 text-center text-slate-400 text-sm">{row.w}</td>
                          <td className="p-4 text-right font-bold text-slate-900">
                            {Math.round(netContribution)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </SectionCard>

            {/* SKILL CORRELATION COMPONENT */}
            <SectionCard title="Skill Match Analysis">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm text-center">
                  <p className="text-sm font-bold uppercase tracking-wider text-slate-400">Skill Density Index</p>
                  {/* CHANGE 3: Math.round */}
                  <p className="text-3xl font-black text-slate-800 mt-1">{Math.round(analysis?.skill_analysis?.overall_fit_score ?? 0)}%</p>
                </div>
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm text-center">
                  <p className="text-sm font-bold uppercase tracking-wider text-slate-400">Credibility Index</p>
                  <p className="text-3xl font-black text-slate-800 mt-1">{Math.round(credibilityIndexVal)}</p>
                </div>
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm text-center">
                  <p className="text-sm font-bold uppercase tracking-wider text-slate-400">Pillar Matrix Coverage</p>
                  <p className="text-base font-semibold text-slate-600 mt-2">
                    <span className="text-emerald-600 font-bold">{(analysis?.skill_analysis?.found_requirements?.length ?? 0)} Full</span> •
                    <span className="text-amber-500 font-bold"> {(analysis?.skill_analysis?.partial_requirements?.length ?? 0)} Partial</span> •
                    <span className="text-red-500 font-bold"> {(analysis?.skill_analysis?.missing_skills?.length ?? 0)} Missing</span>
                  </p>
                </div>
              </div>

              {/* CHANGE 1 */}
              <div className="text-xs text-slate-500 bg-slate-100/70 p-2.5 rounded-xl border border-slate-200/50 mb-6">
                💡 <strong>What is the Credibility Index?</strong> This aggregates how strongly your declared skills match your active experience verification context.
              </div>

              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2.5">Fully Verified Requirements</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis?.skill_analysis?.found_requirements?.map((s: any, idx: number) => (
                      <span key={idx} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-100 text-sm font-medium shadow-sm">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        {s.skill} <span className="text-xs opacity-60">({s.priority})</span>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-100">
                  <div>
                    <h4 className="text-sm font-bold text-amber-600 uppercase tracking-wider mb-2">Mentioned But Weak Context Evidence</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis?.skill_analysis?.partial_requirements?.map((s: any, idx: number) => (
                        <span key={idx} className="px-2.5 py-1 rounded-lg bg-amber-50/50 text-amber-700 border border-amber-100 text-sm font-medium">
                          {s.skill} <span className="text-xs opacity-60">({s.priority})</span>
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Static Keyword Blocks Only</h4>
                    <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-1 border border-slate-50 rounded-lg">
                      {analysis?.skill_analysis?.depth_analysis?.["Low Evidence (Skill List Only)"]?.map((s: string, idx: number) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-sm capitalize">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <h4 className="text-sm font-bold text-red-500 uppercase tracking-wider mb-2">Missing Priority Vacancies</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis?.skill_analysis?.missing_skills?.map((s: string, idx: number) => (
                      <span key={idx} className="px-2.5 py-1 rounded-lg bg-red-50 text-red-600 border border-red-100 text-sm font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </SectionCard>

            {/* TECHNICAL PORTFOLIO EVALUATION */}
            <SectionCard title="Technical Portfolio Evaluation">
              <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 text-white p-4 rounded-xl mb-6 shadow-sm">
                <div>
                  <p className="text-xs uppercase font-bold text-slate-400 tracking-wider">Project Score</p>
                  {/* CHANGE 3: Math.round */}
                  <p className="text-3xl font-black text-indigo-400 mt-0.5">{Math.round(analysis?.project_analysis?.project_score ?? 0)} <span className="text-sm text-slate-400 font-normal">Baseline Index</span></p>
                </div>
                <div className="h-8 w-px bg-slate-700 hidden md:block"></div>
                <div>
                  <p className="text-xs uppercase font-bold text-slate-400 tracking-wider">Diversity Rating</p>
                  <p className="text-xl font-bold mt-0.5">{Math.round(analysis?.project_analysis?.project_diversity_score ?? 0)}</p>
                </div>
                <div className="h-8 w-px bg-slate-700 hidden md:block"></div>
                <div>
                  <p className="text-xs uppercase font-bold text-slate-400 tracking-wider">Advanced Indicators</p>
                  <p className="text-xl font-bold mt-0.5">{Math.round(analysis?.project_analysis?.advanced_project_score ?? 0)} Detected</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {analysis?.project_analysis?.projects_analyzed?.map((proj: any, idx: number) => {
                  const isTutorial = proj.tutorial_penalty > 0;
                  return (
                    <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between shadow-sm relative hover:shadow-md transition-all">
                      <div>
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="font-bold text-slate-800 text-base md:text-lg line-clamp-2 leading-snug">{proj.project_title}</h4>
                          <span className={`text-xs uppercase font-bold px-2 py-0.5 rounded shrink-0 ${
                            proj.evidence_level === "High" ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-600"
                          }`}>{proj.evidence_level} Evidence</span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 my-3 p-2 bg-slate-50 rounded-lg text-center text-sm">
                          <div>
                            <span className="block text-xs text-slate-400 uppercase font-medium">Relevance</span>
                            {/* CHANGE 3 */}
                            <span className="font-bold text-slate-700">{Math.round(proj.relevance_score)}/10</span>
                          </div>
                          <div>
                            <span className="block text-xs text-slate-400 uppercase font-medium">Complexity</span>
                            <span className="font-bold text-slate-700">{Math.round(proj.complexity_score)}</span>
                          </div>
                          <div>
                            <span className="block text-xs text-slate-400 uppercase font-medium">Impact</span>
                            <span className="font-bold text-slate-700">{Math.round(proj.impact_score)}</span>
                          </div>
                        </div>

                        <div className="my-3">
                          {isTutorial ? (
                            <div className="flex items-start gap-1.5 text-xs text-amber-700 bg-amber-50 p-2 rounded-lg border border-amber-100/60">
                              <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                              <p>Structural blueprint tracks standard academic tutorial formats.</p>
                            </div>
                          ) : (
                            <div className="flex items-start gap-1.5 text-xs text-emerald-700 bg-emerald-50/60 p-2 rounded-lg border border-emerald-100/40">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                              <p>Project acts as practical production implementation mapping.</p>
                            </div>
                          )}
                        </div>

                        <div className="space-y-2 pt-2">
                          <div className="flex flex-wrap gap-1">
                            {proj.matched_skills?.map((sk: string, sIdx: number) => (
                              <span key={sIdx} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded capitalize">{sk}</span>
                            ))}
                            {proj.advanced_signals?.map((sig: string, sIdx: number) => (
                              <span key={sIdx} className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded font-medium capitalize">{sig}</span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500 space-y-1 bg-slate-50/50 p-2 rounded-lg">
                        <span className="font-bold text-slate-600 block">Required Context Enhancements:</span>
                        <ul className="list-disc pl-3.5 space-y-0.5 text-slate-500">
                          {proj.impact_score === 0 && <li>Append missing quantified monetization indicators.</li>}
                          {proj.matched_skills?.length < 3 && <li>Detail supporting infrastructure architectures inside layout structures.</li>}
                        </ul>
                      </div>
                    </div>
                  );
                })}
              </div>
            </SectionCard>

            {/* BULLET IMPACT PROCESSING SCENARIOS */}
            <SectionCard title="Performance Metrics & Action Impact">
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm">
                  <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Impact Score</span>
                  {/* CHANGE 3 */}
                  <span className="text-2xl font-black text-slate-800 mt-0.5 block">{Math.round(analysis?.impact_analysis?.overall_impact_score ?? 0)}%</span>
                </div>
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm">
                  <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Quality Band</span>
                  <span className="text-base font-bold text-emerald-600 mt-1 block capitalize">{analysis?.impact_analysis?.impact_quality}</span>
                </div>
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm">
                  <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Ownership Verbs</span>
                  <span className="text-2xl font-black text-slate-800 mt-0.5 block">{Math.round(analysis?.impact_analysis?.ownership_signals ?? 0)}</span>
                </div>
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm">
                  <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Scale Indicators</span>
                  <span className="text-2xl font-black text-slate-800 mt-0.5 block">{Math.round(analysis?.impact_analysis?.scale_indicators ?? 0)}</span>
                </div>
                <div className="bg-white p-4 border border-slate-100 rounded-xl shadow-sm col-span-2 md:col-span-1">
                  <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Quantified Metrics</span>
                  <span className="text-2xl font-black text-indigo-600 mt-0.5 block">{analysis?.impact_analysis?.quantified_achievements} Found</span>
                </div>
              </div>

              {analysis?.impact_analysis?.strongest_impact_bullet && (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-white mb-6 shadow-sm relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform">
                    <Award className="w-24 h-24 text-white" />
                  </div>
                  <span className="inline-flex items-center gap-1 text-xs uppercase font-extrabold tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-md mb-2">
                    🏆 Peak Performance Action Statement
                  </span>
                  <p className="text-sm italic font-medium leading-relaxed text-slate-200">
                    "{analysis?.impact_analysis?.strongest_impact_bullet}"
                  </p>
                </div>
              )}

              <div className="space-y-4">
                {analysis?.impact_analysis?.bullet_analysis?.map((blt: any, idx: number) => {
                  let config = { border: "border-l-4 border-l-emerald-500", label: "High Impact Bullet", note: "Strong ownership + scale indicators verified." };
                  if (blt.evidence_level === "Medium") config = { border: "border-l-4 border-l-amber-400", label: "Medium Impact Bullet", note: "Consider adding downstream metrics to strengthen context values." };
                  if (blt.evidence_level === "Low") config = { border: "border-l-4 border-l-slate-300", label: "Low Impact Bullet", note: "Requires correction using active verbs and performance metrics parameters." };

                  return (
                    <div key={idx} className={`bg-white p-4 border border-slate-200 rounded-xl shadow-sm ${config.border} flex flex-col md:flex-row justify-between items-start md:items-center gap-4`}>
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{config.label}</span>
                          <span className="text-xs font-medium text-slate-400 capitalize">Source Node: {blt.source}</span>
                        </div>
                        <p className="text-sm font-medium text-slate-700 leading-relaxed">"{blt.bullet}"</p>
                        <p className="text-xs text-slate-400 italic font-medium pt-0.5">{config.note}</p>
                      </div>

                      <div className="flex flex-wrap md:flex-col items-end gap-1 shrink-0 text-right">
                        {/* CHANGE 3 */}
                        <span className="text-sm font-bold text-slate-900 bg-slate-50 border border-slate-100 px-2.5 py-1 rounded-md">Score: {Math.round(blt.bullet_impact_score ?? 0)}</span>
                        {blt.metrics_found?.map((m: string, mIdx: number) => (
                          <span key={mIdx} className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">Metric: {m}</span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </SectionCard>

            {/* APPLIED DATA ENGINEERING READINESS SUMMARY */}
            <SectionCard title="Applied Engineering Readiness Profile">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1 bg-slate-900 text-white rounded-2xl p-6 flex flex-col justify-center items-center text-center border border-slate-800 shadow-inner">
                  <p className="text-sm uppercase font-bold tracking-widest text-slate-400">Capability Readiness Index</p>
                  <p className="text-5xl font-black text-indigo-400 mt-2">{dsReadinessScore} <span className="text-sm font-normal text-slate-400">/ 100</span></p>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
                    <div className="bg-indigo-400 h-full rounded-full" style={{ width: `${dsReadinessScore}%` }}></div>
                  </div>
                </div>

                <div className="lg:col-span-2 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { title: "Modeling Core Rigor", score: Math.round((analysis?.data_science_specific?.project_maturity ?? 0) * 10), desc: "Evaluated from runtime complexity algorithms selection and parameter weights data structures." },
                      { title: "Production Deployment Readiness", score: Math.round((analysis?.data_science_specific?.production_readiness ?? 0) * 10), desc: "Evaluated across infrastructure hosting environments and API endpoint packaging footprint." },
                      { title: "Infrastructure & Pipeline Design", score: Math.round((analysis?.data_science_specific?.pipeline_thinking ?? 0) * 10), desc: "Evaluated from end-to-end task automation configurations." },
                      { title: "Statistical & Experimentation Depth", score: Math.round((analysis?.data_science_specific?.statistical_depth ?? 0) * 10), desc: "Evaluated from mathematical hypothesis verification rules and sample processing tracking." },
                      { title: "Problem Framing & Domain Thinking", score: Math.round((analysis?.data_science_specific?.problem_framing ?? 0) * 10), desc: "Evaluated across translating abstract guidelines into explicit logical architecture components." },
                    ].map((item, idx) => (
                      <div key={idx} className="bg-white p-3 border border-slate-200 rounded-xl shadow-sm space-y-1.5">
                        <div className="flex justify-between items-center text-sm">
                          <span className="font-bold text-slate-700">{item.title}</span>
                          <span className={`px-2 py-0.5 rounded font-bold ${item.score >= 70 ? 'text-emerald-600 bg-emerald-50' : 'text-amber-600 bg-amber-50'}`}>{item.score >= 75 ? 'Strong' : item.score >= 50 ? 'Moderate' : 'Developing'}</span>
                        </div>
                        <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${item.score >= 70 ? 'bg-emerald-500' : 'bg-amber-400'}`} style={{ width: `${item.score}%` }}></div>
                        </div>
                        <p className="text-xs text-slate-400 leading-snug line-clamp-2">{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </SectionCard>

            {/* PARSE & SYNTAX EVALUATORS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SectionCard title="ATS Layout Format Compliance">
                <div className="flex items-center justify-between mb-4 border-b pb-2">
                  <div>
                    <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Layout Score Index</span>
                    {/* CHANGE 3 */}
                    <span className="text-3xl font-black text-slate-800">{Math.round(analysis?.ats_format_score?.ats_format_score ?? 0)}%</span>
                  </div>
                  <span className="px-3 py-1 bg-slate-900 text-white font-bold text-sm rounded-xl uppercase tracking-wider">
                    Grade: {analysis?.ats_format_score?.ats_grade}
                  </span>
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {analysis?.ats_format_score?.strengths?.map((str: string, sIdx: number) => (
                    <div key={sIdx} className="flex items-center gap-2 text-sm text-slate-600">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /> {str}
                    </div>
                  ))}
                  {analysis?.ats_format_score?.issues_found?.length === 0 ? (
                    <div className="text-sm text-emerald-600 bg-emerald-50 p-2 rounded-lg font-medium">
                      ✓ Layout structural parameters show strict compatibility with parsed multi-column data screens.
                    </div>
                  ) : (
                    analysis?.ats_format_score?.issues_found?.map((iss: string, sIdx: number) => (
                      <div key={sIdx} className="flex items-center gap-2 text-sm text-red-600">
                        <XCircle className="w-4 h-4 text-red-500 shrink-0" /> {iss}
                      </div>
                    ))
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Grammar & Professional Syntax Quality">
                <div className="flex items-center justify-between mb-4 border-b pb-2">
                  <div>
                    <span className="block text-xs font-bold uppercase tracking-wider text-slate-400">Grammar Score Index</span>
                    {/* CHANGE 3 */}
                    <span className="text-3xl font-black text-slate-800">{Math.round(analysis?.grammar_score?.grammar_score ?? 0)}%</span>
                  </div>
                  <span className="px-3 py-1 bg-slate-100 text-slate-700 font-bold text-sm rounded-xl uppercase tracking-wider border border-slate-200">
                    Quality: {analysis?.grammar_score?.grammar_quality}
                  </span>
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {analysis?.grammar_score?.issues_found?.map((iss: string, sIdx: number) => (
                    <div key={sIdx} className="p-2 bg-red-50 border border-red-100 rounded-lg text-sm text-red-700 flex gap-1.5 items-start">
                      <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                      <p><strong>Syntax Flag:</strong> {iss}</p>
                    </div>
                  ))}
                </div>
              </SectionCard>
            </div>

            {/* JOB DESCRIPTION DENSITY OVERLAP */}
            <SectionCard title="Job Description Match">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-slate-900 text-white rounded-xl mb-4">
                <div>
                  <span className="block text-xs text-slate-400 uppercase tracking-wider font-bold">JD Fit Score</span>
                  {/* CHANGE 3 */}
                  <span className="text-3xl font-black text-indigo-400 mt-0.5 block">{Math.round(analysis?.jd_match_score?.match_score ?? 0)}%</span>
                </div>
                <div>
                  <span className="block text-xs text-slate-400 uppercase tracking-wider font-bold">Density Ranking</span>
                  <span className="text-base font-bold mt-1.5 block text-slate-200">{analysis?.jd_match_score?.match_quality}</span>
                </div>
                <div>
                  <span className="block text-xs text-slate-400 uppercase tracking-wider font-bold">Domain Core Score</span>
                  <span className="text-xl font-bold mt-1 block">{Math.round(analysis?.jd_match_score?.domain_match_score ?? 0)}/100</span>
                </div>
                <div>
                  <span className="block text-xs text-slate-400 uppercase tracking-wider font-bold">Experience Seniority Band</span>
                  <span className="text-base font-bold mt-1.5 block text-slate-200">{analysis?.jd_match_score?.experience_strength}</span>
                </div>
              </div>

              {analysis?.jd_match_score?.missing_skills?.length > 0 && (
                <div className="mt-4 space-y-2">
                  <span className="text-sm font-bold uppercase tracking-wider text-red-600 block">Identified Structural Content Gaps:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis?.jd_match_score?.missing_skills?.map((sk: string, idx: number) => (
                      <span key={idx} className="text-sm px-2.5 py-0.5 bg-red-50 text-red-700 border border-red-100 rounded-md font-medium">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </SectionCard>

            {/* RECRUITER CONSOLE INTERFACES */}
            <SectionCard title="Recruiter Evaluation Console">
              <div className="space-y-6">
                <div>
                  <span className="text-sm font-bold uppercase tracking-wider text-amber-700 flex items-center gap-1.5 mb-3">
                    <AlertTriangle className="w-4 h-4 text-amber-500" /> Hiring Panel Context Risks ({analysis?.recruiter_flags?.recruiter_flags?.length || 0})
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {analysis?.recruiter_flags?.recruiter_flags?.map((flg: string, idx: number) => (
                      <div key={idx} className="p-3 bg-amber-50/60 border border-amber-100 text-sm text-slate-700 rounded-xl leading-relaxed">
                        • {flg}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  <span className="text-sm font-bold uppercase tracking-wider text-emerald-700 flex items-center gap-1.5 mb-3">
                    <BadgeCheck className="w-4 h-4 text-emerald-500" /> Verified Market Assets ({analysis?.recruiter_flags?.recruiter_strengths?.length || 0})
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {analysis?.recruiter_flags?.recruiter_strengths?.map((str: string, idx: number) => (
                      <div key={idx} className="p-3 bg-emerald-50/40 border border-emerald-100/60 text-sm text-slate-700 rounded-xl leading-relaxed">
                        ✓ {str}
                      </div>
                    ))}
                  </div>
                </div>

                {analysis?.recruiter_flags?.recruiter_recommendation && (
                  <div className="pt-4 border-t border-slate-100 bg-slate-900 text-white rounded-2xl p-5 mt-4 border border-slate-800 shadow-lg relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:rotate-12 transition-transform">
                      <ShieldCheck className="w-20 h-20 text-white" />
                    </div>
                    <span className="inline-flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-widest bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2.5 py-1 rounded-md mb-3">
                      Hiring Panel Summary Verdict
                    </span>
                    <p className="text-sm md:text-base font-medium leading-relaxed text-slate-300">
                      "{analysis?.recruiter_flags?.recruiter_recommendation}"
                    </p>
                  </div>
                )}
              </div>
            </SectionCard>
          </>
        )}
      </div>
    </div>
  );
}