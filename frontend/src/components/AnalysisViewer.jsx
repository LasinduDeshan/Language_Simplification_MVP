import React, { useState, useEffect } from "react";
import {
  Activity, CheckCircle2, XCircle, AlertTriangle, ShieldCheck,
  ShieldAlert, Sparkles, RefreshCw, Volume2, BookOpen, User,
  Layers, ArrowRight, HelpCircle, Code2, AlertCircle, EyeOff,
  Check, FileText, Cpu
} from "lucide-react";
import { analyzeResponse, fetchGrammarTestCases } from "../services/api";

export default function AnalysisViewer({ tasks, learners, selectedTask: initialTask }) {
  const [selectedTaskId, setSelectedTaskId] = useState(initialTask?.id || (tasks[0]?.id || ""));
  const [learnerAge, setLearnerAge] = useState(6);
  const [speechTranscript, setSpeechTranscript] = useState("Fish live water.");
  const [speechConfidence, setSpeechConfidence] = useState(0.92);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [grammarPresets, setGrammarPresets] = useState([]);
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [showRawJson, setShowRawJson] = useState(false);

  // Sync initial task if updated from parent
  useEffect(() => {
    if (initialTask && initialTask.id !== selectedTaskId) {
      setSelectedTaskId(initialTask.id);
    }
  }, [initialTask]);

  // Load benchmark grammar test cases on mount
  useEffect(() => {
    async function loadPresets() {
      try {
        const presets = await fetchGrammarTestCases();
        setGrammarPresets(presets);
      } catch (err) {
        console.warn("Could not load grammar presets:", err);
      }
    }
    loadPresets();
  }, []);

  const activeTask = tasks.find(t => t.id === selectedTaskId) || tasks[0];

  // Load a test case preset
  const handleApplyPreset = (presetId) => {
    setSelectedPresetId(presetId);
    const preset = grammarPresets.find(p => p.test_id === presetId);
    if (!preset) return;

    // Find task corresponding to task_code
    const matchingTask = tasks.find(t => t.task_code === preset.task_code);
    if (matchingTask) {
      setSelectedTaskId(matchingTask.id);
    }
    setSpeechTranscript(preset.speech_transcript);
    setSpeechConfidence(preset.speech_confidence);
  };

  // Run diagnostic analysis
  const handleRunAnalysis = async () => {
    if (!selectedTaskId || !speechTranscript.trim()) {
      setError("Please select a task and enter a speech transcript to analyze.");
      return;
    }

    setAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeResponse({
        taskId: selectedTaskId,
        speechTranscript: speechTranscript.trim(),
        speechConfidence: parseFloat(speechConfidence),
        learnerAge: parseInt(learnerAge, 10)
      });
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message || "Diagnostic analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  // Run on mount with default settings
  useEffect(() => {
    if (tasks.length > 0 && selectedTaskId) {
      handleRunAnalysis();
    }
  }, [selectedTaskId]);

  return (
    <div className="analysis-viewer">
      {/* Section Header */}
      <div className="section-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.65rem", marginBottom: "0.25rem" }}>
            <span className="chip" style={{ background: "rgba(99, 102, 241, 0.2)", color: "#818cf8", border: "1px solid rgba(99, 102, 241, 0.4)" }}>
              Sprint 2 Delivery
            </span>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Ages 4–8 • spaCy NLP Pipeline</span>
          </div>
          <h1 className="section-title">English Response & Grammar Diagnostics</h1>
          <p className="section-subtitle">
            Inspect multi-tier answer evaluation, grammar error pattern extraction with acoustic gating (&lt;0.70), and age-graded vocabulary analysis.
          </p>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={analyzing}
          className="btn btn-primary"
          style={{ minWidth: "160px" }}
        >
          <RefreshCw size={16} className={analyzing ? "spin" : ""} />
          <span>{analyzing ? "Analyzing..." : "Run Analysis"}</span>
        </button>
      </div>

      {/* Safety Separation Banner */}
      <div style={{
        background: "rgba(99, 102, 241, 0.08)",
        border: "1px solid rgba(99, 102, 241, 0.25)",
        borderRadius: "var(--radius-md)",
        padding: "1rem 1.25rem",
        marginBottom: "1.75rem",
        display: "flex",
        alignItems: "flex-start",
        gap: "1rem"
      }}>
        <div style={{
          background: "rgba(99, 102, 241, 0.2)",
          padding: "8px",
          borderRadius: "var(--radius-sm)",
          color: "#a5b4fc",
          marginTop: "2px"
        }}>
          <EyeOff size={20} />
        </div>
        <div style={{ flex: 1 }}>
          <h4 style={{ fontSize: "0.92rem", fontWeight: 700, color: "#e0e7ff", marginBottom: "0.2rem" }}>
            Mandatory Separation of Diagnostic Observations (Child vs. Researcher)
          </h4>
          <p style={{ fontSize: "0.82rem", color: "#cbd5e1", lineHeight: 1.5 }}>
            Grammar error tags (e.g., <code>missing_preposition</code>, <code>subject_verb_agreement</code>, <code>omitted_copula</code>) have <strong><code>child_visible = False</code></strong>. 
            They are logged for researchers, clinicians, and Component 4 progress analytics. <strong>The child learner never sees technical error labels or scores</strong>, only natural supportive prompts and adult recasting.
          </p>
        </div>
      </div>

      {/* Main Sandbox Grid */}
      <div className="grid-2" style={{ marginBottom: "2rem", alignItems: "start" }}>
        
        {/* Left Column: Sandbox Controls */}
        <div className="card card-glass">
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Cpu size={18} color="#818cf8" />
            <span>1. Diagnostic Input Sandbox</span>
          </h2>

          {/* Quick Preset Picker */}
          {grammarPresets.length > 0 && (
            <div className="form-group" style={{ marginBottom: "1.25rem" }}>
              <label className="form-label" style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Benchmark Test Case Presets (Seed Cases)</span>
                <span style={{ fontSize: "0.7rem", color: "#818cf8" }}>8 Preloaded</span>
              </label>
              <select
                className="form-select"
                value={selectedPresetId}
                onChange={(e) => handleApplyPreset(e.target.value)}
                style={{ fontSize: "0.85rem", background: "rgba(15, 23, 42, 0.85)" }}
              >
                <option value="">-- Choose a standard test case preset --</option>
                {grammarPresets.map(p => (
                  <option key={p.test_id} value={p.test_id}>
                    {p.test_id}: {p.description} (Conf: {p.speech_confidence})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Task Selector */}
          <div className="form-group">
            <label className="form-label">Target Task</label>
            <select
              className="form-select"
              value={selectedTaskId}
              onChange={(e) => setSelectedTaskId(e.target.value)}
            >
              {tasks.map(t => (
                <option key={t.id} value={t.id}>
                  {t.task_code}: {t.title} ({t.task_type})
                </option>
              ))}
            </select>
          </div>

          {/* Learner Age Selector */}
          <div className="form-group">
            <label className="form-label" style={{ display: "flex", justifyContent: "space-between" }}>
              <span>Learner Age ({learnerAge} Years Old)</span>
              <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Target range: 4–8</span>
            </label>
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.25rem" }}>
              {[4, 5, 6, 7, 8].map(age => (
                <button
                  key={age}
                  type="button"
                  onClick={() => setLearnerAge(age)}
                  className="btn btn-secondary"
                  style={{
                    flex: 1,
                    padding: "6px",
                    fontSize: "0.85rem",
                    borderColor: learnerAge === age ? "var(--accent-primary)" : "var(--border-color)",
                    background: learnerAge === age ? "rgba(99, 102, 241, 0.25)" : "rgba(255, 255, 255, 0.04)",
                    color: learnerAge === age ? "#ffffff" : "var(--text-secondary)",
                    fontWeight: learnerAge === age ? 700 : 500
                  }}
                >
                  Age {age}
                </button>
              ))}
            </div>
          </div>

          {/* Speech Transcript Input */}
          <div className="form-group">
            <label className="form-label" style={{ display: "flex", justifyContent: "space-between" }}>
              <span>Simulated Speech Transcript (Component 1)</span>
              <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                {speechTranscript.split(/\s+/).filter(Boolean).length} words
              </span>
            </label>
            <textarea
              className="form-textarea"
              rows={3}
              value={speechTranscript}
              onChange={(e) => setSpeechTranscript(e.target.value)}
              placeholder='e.g. "Fish live water." or "She kick the ball."'
              style={{ fontSize: "0.95rem", lineHeight: 1.4 }}
            />
          </div>

          {/* Speech Confidence Slider */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <label className="form-label" style={{ margin: 0 }}>
                Speech Confidence: <strong>{Number(speechConfidence).toFixed(2)}</strong>
              </label>
              <span style={{
                fontSize: "0.72rem",
                fontWeight: 700,
                color: speechConfidence >= 0.70 ? "#34d399" : "#fbbf24",
                background: speechConfidence >= 0.70 ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
                padding: "2px 8px",
                borderRadius: "var(--radius-full)"
              }}>
                {speechConfidence >= 0.70 ? ">= 0.70 (Acoustically Acceptable)" : "< 0.70 (Unconfirmed Mode)"}
              </span>
            </div>
            <input
              type="range"
              min="0.4"
              max="1.0"
              step="0.02"
              value={speechConfidence}
              onChange={(e) => setSpeechConfidence(parseFloat(e.target.value))}
              style={{ width: "100%", marginTop: "0.6rem", accentColor: speechConfidence >= 0.70 ? "#10b981" : "#f59e0b" }}
            />
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.35rem" }}>
              Confidence below 0.70 automatically forces <code>confirmed = False</code> so acoustic transcription artifacts are not misdiagnosed as language difficulties.
            </p>
          </div>
        </div>

        {/* Right Column: Active Task Context */}
        <div className="card card-glass">
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <BookOpen size={18} color="#38bdf8" />
            <span>2. Task Ground Truth & Evaluation Rules</span>
          </h2>

          {activeTask ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <span className="chip chip-type">{activeTask.task_code}</span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  Age Range: {activeTask.minimum_age}–{activeTask.maximum_age} yrs
                </span>
              </div>

              <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.4rem" }}>
                {activeTask.title}
              </h3>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
                <strong>Objective:</strong> {activeTask.learning_objective}
              </p>

              <div style={{ background: "rgba(0,0,0,0.3)", padding: "0.85rem", borderRadius: "var(--radius-sm)", marginBottom: "0.85rem" }}>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "0.25rem" }}>
                  Original Instruction Prompt:
                </span>
                <p style={{ fontSize: "0.88rem", color: "#e2e8f0", fontStyle: "italic" }}>
                  "{activeTask.original_instruction}"
                </p>
              </div>

              {/* Acceptable Answers */}
              <div style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.2)", padding: "0.85rem", borderRadius: "var(--radius-sm)", marginBottom: "0.85rem" }}>
                <span style={{ fontSize: "0.72rem", color: "#34d399", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: "0.25rem" }}>
                  Semantic Target Answers (Acceptable):
                </span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                  {activeTask.acceptable_answers?.map((ans, i) => (
                    <span key={i} style={{ fontSize: "0.8rem", background: "rgba(16, 185, 129, 0.15)", color: "#a7f3d0", padding: "2px 8px", borderRadius: "4px", fontWeight: 600 }}>
                      ✓ {ans}
                    </span>
                  ))}
                </div>
              </div>

              {/* Protected answers / Leakage rules */}
              {activeTask.protected_answers?.restricted_solution_phrases && (
                <div style={{ background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239, 68, 68, 0.2)", padding: "0.85rem", borderRadius: "var(--radius-sm)" }}>
                  <span style={{ fontSize: "0.72rem", color: "#f87171", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: "0.25rem" }}>
                    Restricted Solutions (Answer Leakage Check):
                  </span>
                  <p style={{ fontSize: "0.8rem", color: "#cbd5e1" }}>
                    {activeTask.protected_answers.restricted_solution_phrases.join(", ")}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: "var(--text-muted)" }}>No task selected.</p>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div style={{
          background: "rgba(239, 68, 68, 0.15)",
          border: "1px solid rgba(239, 68, 68, 0.3)",
          color: "#fca5a5",
          padding: "0.85rem 1.25rem",
          borderRadius: "var(--radius-md)",
          marginBottom: "1.5rem",
          display: "flex",
          alignItems: "center",
          gap: "0.75rem"
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Diagnostic Results Section */}
      {analysisResult && (
        <div className="card card-glass" style={{ marginBottom: "2rem", border: "1px solid rgba(99, 102, 241, 0.3)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#ffffff" }}>
                3. Diagnostic Pipeline Evaluation Output
              </h2>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Analysis executed across Semantic Concept Evaluator, spaCy Dependency Engine, and Lexical Difficulty Grader.
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
              <button
                onClick={() => setShowRawJson(!showRawJson)}
                className="btn btn-secondary btn-sm"
              >
                <Code2 size={14} />
                <span>{showRawJson ? "Hide Raw JSON" : "Inspect Raw JSON"}</span>
              </button>
            </div>
          </div>

          {/* Primary Cards: Concept Match + Speech Gating */}
          <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
            
            {/* Concept Correctness Card */}
            <div style={{
              background: "rgba(0,0,0,0.3)",
              border: `1px solid ${
                analysisResult.concept_result === "correct" ? "rgba(16, 185, 129, 0.4)" :
                analysisResult.concept_result === "partial" ? "rgba(245, 158, 11, 0.4)" : "rgba(239, 68, 68, 0.4)"
              }`,
              borderRadius: "var(--radius-md)",
              padding: "1.25rem"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                  Concept / Semantic Evaluation
                </span>
                <span style={{
                  padding: "4px 12px",
                  borderRadius: "var(--radius-full)",
                  fontSize: "0.8rem",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  background: analysisResult.concept_result === "correct" ? "rgba(16, 185, 129, 0.2)" :
                    analysisResult.concept_result === "partial" ? "rgba(245, 158, 11, 0.2)" : "rgba(239, 68, 68, 0.2)",
                  color: analysisResult.concept_result === "correct" ? "#34d399" :
                    analysisResult.concept_result === "partial" ? "#fbbf24" : "#f87171",
                  border: `1px solid ${
                    analysisResult.concept_result === "correct" ? "rgba(16, 185, 129, 0.5)" :
                    analysisResult.concept_result === "partial" ? "rgba(245, 158, 11, 0.5)" : "rgba(239, 68, 68, 0.5)"
                  }`
                }}>
                  {analysisResult.concept_result}
                </span>
              </div>

              <div style={{ marginBottom: "0.75rem" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Analyzed Transcript:</span>
                <p style={{ fontSize: "1.05rem", fontWeight: 700, color: "#ffffff", marginTop: "0.15rem" }}>
                  "{speechTranscript}"
                </p>
              </div>

              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Matched Semantic Concepts:</span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.25rem" }}>
                  {analysisResult.concept_matches && analysisResult.concept_matches.length > 0 ? (
                    analysisResult.concept_matches.map((c, i) => (
                      <span key={i} style={{ fontSize: "0.78rem", background: "rgba(99, 102, 241, 0.2)", color: "#c7d2fe", padding: "2px 8px", borderRadius: "4px" }}>
                        {c}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontStyle: "italic" }}>No concepts matched</span>
                  )}
                </div>
              </div>
            </div>

            {/* Speech Acoustic Reliability Gating Card */}
            <div style={{
              background: "rgba(0,0,0,0.3)",
              border: `1px solid ${analysisResult.speech_confidence_acceptable ? "rgba(16, 185, 129, 0.4)" : "rgba(245, 158, 11, 0.4)"}`,
              borderRadius: "var(--radius-md)",
              padding: "1.25rem"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
                  Acoustic Gating Status
                </span>
                <span style={{
                  padding: "4px 12px",
                  borderRadius: "var(--radius-full)",
                  fontSize: "0.8rem",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  background: analysisResult.speech_confidence_acceptable ? "rgba(16, 185, 129, 0.2)" : "rgba(245, 158, 11, 0.2)",
                  color: analysisResult.speech_confidence_acceptable ? "#34d399" : "#fbbf24",
                  border: `1px solid ${analysisResult.speech_confidence_acceptable ? "rgba(16, 185, 129, 0.5)" : "rgba(245, 158, 11, 0.5)"}`
                }}>
                  {analysisResult.speech_confidence_acceptable ? "Gating Passed" : "Low Confidence (&lt; 0.70)"}
                </span>
              </div>

              <div style={{ marginBottom: "0.75rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem" }}>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Acoustic Confidence Metric:</span>
                  <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff" }}>
                    {(speechConfidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ height: "8px", background: "rgba(255,255,255,0.1)", borderRadius: "999px", overflow: "hidden" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${speechConfidence * 100}%`,
                      background: speechConfidence >= 0.70 ? "linear-gradient(90deg, #10b981, #34d399)" : "linear-gradient(90deg, #f59e0b, #fbbf24)",
                      borderRadius: "999px"
                    }}
                  />
                </div>
              </div>

              <p style={{ fontSize: "0.8rem", color: analysisResult.speech_confidence_acceptable ? "#a7f3d0" : "#fef08a", lineHeight: 1.4 }}>
                {analysisResult.speech_confidence_acceptable
                  ? "✓ Confidence is sufficiently high to confirm grammatical observations for clinical tracking."
                  : "⚠️ Speech confidence is below 0.70. Grammar observations are retained for analysis but marked confirmed = False to prevent treating audio distortion as a child language deficit."}
              </p>
            </div>
          </div>

          {/* Detailed Observations Table */}
          <div style={{ marginTop: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Activity size={17} color="#818cf8" />
                <span>Extracted Language Observations ({analysisResult.observations?.length || 0})</span>
              </h3>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Targeting: Grammar/Syntax, Lexical Age-Grading, Comprehension Dropoff
              </span>
            </div>

            {analysisResult.observations && analysisResult.observations.length > 0 ? (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                      <th style={{ padding: "8px 12px" }}>Observation Code</th>
                      <th style={{ padding: "8px 12px" }}>Category</th>
                      <th style={{ padding: "8px 12px" }}>Evidence Snippet</th>
                      <th style={{ padding: "8px 12px" }}>Confidence</th>
                      <th style={{ padding: "8px 12px" }}>Confirmed?</th>
                      <th style={{ padding: "8px 12px" }}>Clinical Adult Recast / Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysisResult.observations.map((obs, idx) => (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: "1px solid rgba(255,255,255,0.04)",
                          background: idx % 2 === 0 ? "rgba(255,255,255,0.01)" : "transparent"
                        }}
                      >
                        <td style={{ padding: "10px 12px" }}>
                          <span style={{
                            fontFamily: "monospace",
                            fontWeight: 700,
                            color: "#818cf8",
                            background: "rgba(99, 102, 241, 0.15)",
                            padding: "3px 8px",
                            borderRadius: "4px"
                          }}>
                            {obs.observation_code}
                          </span>
                        </td>
                        <td style={{ padding: "10px 12px" }}>
                          <span className={`chip chip-${obs.category === "grammar_syntax" ? "mild" : "moderate"}`} style={{ fontSize: "0.7rem" }}>
                            {obs.category}
                          </span>
                        </td>
                        <td style={{ padding: "10px 12px", color: "#f8fafc", fontStyle: "italic" }}>
                          "{obs.evidence}"
                        </td>
                        <td style={{ padding: "10px 12px" }}>
                          <span style={{ fontWeight: 600, color: "#cbd5e1" }}>
                            {(obs.confidence * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td style={{ padding: "10px 12px" }}>
                          {obs.confirmed ? (
                            <span style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                              background: "rgba(16, 185, 129, 0.15)",
                              color: "#34d399",
                              padding: "2px 8px",
                              borderRadius: "var(--radius-full)",
                              fontSize: "0.75rem",
                              fontWeight: 700
                            }}>
                              <Check size={12} /> Confirmed
                            </span>
                          ) : (
                            <span style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                              background: "rgba(245, 158, 11, 0.15)",
                              color: "#fbbf24",
                              padding: "2px 8px",
                              borderRadius: "var(--radius-full)",
                              fontSize: "0.75rem",
                              fontWeight: 700
                            }}>
                              <AlertTriangle size={12} /> Unconfirmed (&lt;0.70)
                            </span>
                          )}
                        </td>
                        <td style={{ padding: "10px 12px", color: "#94a3b8" }}>
                          {(obs.suggested_model || obs.suggested_modeled_phrasing) ? (
                            <span style={{ color: "#a5b4fc" }}>
                              {obs.suggested_model || `Adult model: "${obs.suggested_modeled_phrasing}"`}
                            </span>
                          ) : (obs.simple_alternative || obs.simpler_alternatives) ? (
                            <span style={{ color: "#fbcfe8" }}>
                              Simpler: <strong>"{obs.simple_alternative || (Array.isArray(obs.simpler_alternatives) ? obs.simpler_alternatives.join(', ') : obs.simpler_alternatives)}"</strong>
                              {obs.simple_definition ? ` (${obs.simple_definition})` : ""}
                            </span>
                          ) : (
                            <span style={{ color: "var(--text-muted)" }}>Logged for pattern tracker</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{
                background: "rgba(16, 185, 129, 0.08)",
                border: "1px solid rgba(16, 185, 129, 0.2)",
                padding: "1.25rem",
                borderRadius: "var(--radius-md)",
                textAlign: "center"
              }}>
                <CheckCircle2 size={24} color="#34d399" style={{ margin: "0 auto 0.5rem" }} />
                <p style={{ color: "#a7f3d0", fontWeight: 600, fontSize: "0.95rem" }}>
                  No grammatical or lexical difficulties detected.
                </p>
                <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", marginTop: "0.25rem" }}>
                  Sentence structure and vocabulary align with typical developmental expectations for age {learnerAge}.
                </p>
              </div>
            )}
          </div>

          {/* Raw JSON Accordion */}
          {showRawJson && (
            <div style={{ marginTop: "1.5rem" }}>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "0.5rem" }}>
                Raw JSON API Payload (/api/analyze-response):
              </span>
              <pre style={{
                background: "#030712",
                padding: "1rem",
                borderRadius: "var(--radius-md)",
                color: "#a7f3d0",
                fontSize: "0.8rem",
                overflowX: "auto",
                maxHeight: "300px",
                border: "1px solid var(--border-color)"
              }}>
                {JSON.stringify(analysisResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
