import React, { useState, useEffect } from "react";
import {
  Sliders, Sparkles, RefreshCw, Eye, BookOpen, User, CheckCircle2,
  AlertTriangle, ArrowRight, ShieldCheck, HelpCircle, Layers, FileText,
  Check, Volume2, Code2
} from "lucide-react";
import { adaptInstruction, fetchProgressionPreview } from "../services/api";
import ChildPreviewModal from "./ChildPreviewModal";

export default function AdaptiveInstructionView({
  tasks, learners, selectedTask: initialTask, selectedLearner: initialLearner
}) {
  const [selectedTaskId, setSelectedTaskId] = useState(initialTask?.id || (tasks[0]?.id || ""));
  const [selectedLearnerId, setSelectedLearnerId] = useState(initialLearner?.id || (learners[0]?.id || ""));
  const [activeAttemptNumber, setActiveAttemptNumber] = useState(1);
  const [viewMode, setViewMode] = useState("progression"); // "progression" or "single"
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [progressionData, setProgressionData] = useState(null);
  const [singleAdaptation, setSingleAdaptation] = useState(null);
  const [previewAdaptation, setPreviewAdaptation] = useState(null);
  const [showChildPreview, setShowChildPreview] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);

  // Sync initial selections if updated from parent
  useEffect(() => {
    if (initialTask && initialTask.id !== selectedTaskId) {
      setSelectedTaskId(initialTask.id);
    }
  }, [initialTask]);

  useEffect(() => {
    if (initialLearner && initialLearner.id !== selectedLearnerId) {
      setSelectedLearnerId(initialLearner.id);
    }
  }, [initialLearner]);

  const activeTask = tasks.find(t => t.id === selectedTaskId) || tasks[0];
  const activeLearner = learners.find(l => l.id === selectedLearnerId) || learners[0];

  // Load progression preview (Attempts 1, 2, 3 side-by-side)
  const loadProgression = async () => {
    if (!selectedTaskId || !selectedLearnerId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProgressionPreview(selectedTaskId, selectedLearnerId);
      setProgressionData(data);
      // Also fetch active single adaptation
      const single = await adaptInstruction({
        taskId: selectedTaskId,
        learnerId: selectedLearnerId,
        attemptNumber: activeAttemptNumber,
        generationMode: "rule"
      });
      setSingleAdaptation(single);
    } catch (err) {
      setError(err.message || "Failed to load instruction adaptation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedTaskId && selectedLearnerId) {
      loadProgression();
    }
  }, [selectedTaskId, selectedLearnerId, activeAttemptNumber]);

  const handleOpenChildPreview = (adaptationPayload) => {
    setPreviewAdaptation(adaptationPayload);
    setShowChildPreview(true);
  };

  // Helper to format human-readable reason codes
  const formatReasonCode = (code) => {
    if (code.startsWith("base_risk_")) return `Risk: ${code.replace("base_risk_", "").toUpperCase()}`;
    if (code.startsWith("low_vocabulary_score_")) return `Low Vocab (${code.split("_").pop()})`;
    if (code.startsWith("low_grammar_score_")) return `Low Grammar (${code.split("_").pop()})`;
    if (code.startsWith("english_level_")) return `English: ${code.replace("english_level_", "").toUpperCase()}`;
    if (code === "attempt_1_initial_instruction") return "Attempt 1 Baseline";
    if (code === "attempt_2_retry_escalation") return "Attempt 2 (+1 Tier)";
    if (code === "attempt_3_maximum_support") return "Attempt 3 (Max Support)";
    if (code.startsWith("vocabulary_replaced_")) return `Lexical: ${code.replace("vocabulary_replaced_", "").replace("_with_", " → ")}`;
    if (code.startsWith("task_template_")) return `Template: ${code.replace("task_template_", "")}`;
    return code.replace(/_/g, " ");
  };

  return (
    <div className="adaptive-instruction-view">
      {/* Section Header */}
      <div className="section-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.65rem", marginBottom: "0.25rem" }}>
            <span className="chip" style={{ background: "rgba(99, 102, 241, 0.2)", color: "#818cf8", border: "1px solid rgba(99, 102, 241, 0.4)" }}>
              Sprint 3 Delivery
            </span>
            <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>100% Offline Rule Engine • Ages 4–8</span>
          </div>
          <h1 className="section-title">Personalization & Rule-Based Generation</h1>
          <p className="section-subtitle">
            Inspect deterministic support determination (Mild/Moderate/Strong), single-action step splitting, age-graded vocabulary replacements, and progressive scaffolding across Attempts 1, 2, and 3.
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <div className="nav-tabs">
            <button
              className={`nav-tab ${viewMode === "progression" ? "active" : ""}`}
              onClick={() => setViewMode("progression")}
            >
              <Layers size={15} />
              <span>3-Attempt Progression</span>
            </button>
            <button
              className={`nav-tab ${viewMode === "single" ? "active" : ""}`}
              onClick={() => setViewMode("single")}
            >
              <FileText size={15} />
              <span>Single Attempt Inspector</span>
            </button>
          </div>

          <button
            onClick={loadProgression}
            disabled={loading}
            className="btn btn-secondary btn-sm"
          >
            <RefreshCw size={15} className={loading ? "spin" : ""} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Control Selector Bar */}
      <div className="card card-glass" style={{ marginBottom: "1.75rem" }}>
        <div className="grid-3" style={{ gap: "1.25rem", alignItems: "end" }}>
          
          {/* Select Task */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Active Task (1 of 10)</label>
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

          {/* Select Learner */}
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Learner Profile (1 of 5)</label>
            <select
              className="form-select"
              value={selectedLearnerId}
              onChange={(e) => setSelectedLearnerId(e.target.value)}
            >
              {learners.map(l => (
                <option key={l.id} value={l.id}>
                  {l.learner_code} (Age {l.age}, {l.risk_support_level} risk, {l.english_level})
                </option>
              ))}
            </select>
          </div>

          {/* Context Summary & Attempt Selection */}
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            {viewMode === "single" && (
              <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
                <label className="form-label">Target Attempt</label>
                <div style={{ display: "flex", gap: "0.35rem" }}>
                  {[1, 2, 3].map(num => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setActiveAttemptNumber(num)}
                      className="btn btn-secondary btn-sm"
                      style={{
                        flex: 1,
                        background: activeAttemptNumber === num ? "var(--accent-primary)" : "rgba(255,255,255,0.04)",
                        color: activeAttemptNumber === num ? "#ffffff" : "var(--text-secondary)",
                        fontWeight: activeAttemptNumber === num ? 700 : 500
                      }}
                    >
                      Attempt {num}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeLearner && (
              <div style={{
                background: "rgba(0,0,0,0.3)",
                padding: "8px 14px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-color)",
                display: "flex",
                gap: "1rem",
                alignItems: "center",
                flex: viewMode === "progression" ? 1 : "initial"
              }}>
                <div>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>RISK / LEVEL</span>
                  <span className={`chip chip-${activeLearner.risk_support_level}`} style={{ fontSize: "0.72rem", padding: "2px 8px" }}>
                    {activeLearner.risk_support_level} • {activeLearner.english_level}
                  </span>
                </div>
                <div>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>SCORES</span>
                  <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#ffffff" }}>
                    V: {activeLearner.vocabulary_score} | G: {activeLearner.grammar_score}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          background: "rgba(239, 68, 68, 0.15)",
          border: "1px solid rgba(239, 68, 68, 0.3)",
          color: "#fca5a5",
          padding: "0.85rem 1.25rem",
          borderRadius: "var(--radius-md)",
          marginBottom: "1.5rem"
        }}>
          {error}
        </div>
      )}

      {/* VIEW 1: 3-Attempt Progression (Side-by-Side) */}
      {viewMode === "progression" && progressionData && (
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Sparkles size={18} color="#818cf8" />
              <span>Scaffolding Progression: {activeTask?.title}</span>
            </h2>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              Target length $\le$ 8–10 words (Hard limit 12 words)
            </span>
          </div>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: "1.25rem",
            marginBottom: "2rem"
          }}>
            {progressionData.progression.map((item) => (
              <div
                key={item.attempt_number}
                className="card card-glass"
                style={{
                  border: item.attempt_number === 1
                    ? "1px solid rgba(56, 189, 248, 0.3)"
                    : item.attempt_number === 2
                    ? "1px solid rgba(99, 102, 241, 0.3)"
                    : "1px solid rgba(236, 72, 153, 0.3)",
                  boxShadow: item.attempt_number === 1 ? "0 4px 20px rgba(56, 189, 248, 0.08)" : "none",
                  display: "flex",
                  flexDirection: "column"
                }}
              >
                {/* Card Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{
                      background: item.attempt_number === 1 ? "rgba(56, 189, 248, 0.2)" : item.attempt_number === 2 ? "rgba(99, 102, 241, 0.2)" : "rgba(236, 72, 153, 0.2)",
                      color: item.attempt_number === 1 ? "#38bdf8" : item.attempt_number === 2 ? "#a5b4fc" : "#f472b6",
                      fontWeight: 800,
                      fontSize: "0.85rem",
                      padding: "3px 10px",
                      borderRadius: "var(--radius-full)"
                    }}>
                      Attempt {item.attempt_number}
                    </span>
                    <span className={`chip chip-${item.support_level}`} style={{ fontSize: "0.72rem" }}>
                      {item.support_level}
                    </span>
                  </div>

                  <span style={{
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    color: item.word_count <= 10 ? "#34d399" : item.word_count <= 12 ? "#fbbf24" : "#f87171",
                    background: item.word_count <= 10 ? "rgba(16, 185, 129, 0.12)" : "rgba(245, 158, 11, 0.12)",
                    padding: "2px 8px",
                    borderRadius: "4px"
                  }}>
                    {item.word_count} words {item.word_count <= 10 ? "(Target OK)" : "(<=12 OK)"}
                  </span>
                </div>

                {/* Adapted Instruction */}
                <div style={{
                  background: "rgba(15, 23, 42, 0.75)",
                  padding: "1.15rem",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--border-color)",
                  marginBottom: "1rem",
                  minHeight: "85px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center"
                }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "0.25rem" }}>
                    Child-Facing Instruction:
                  </span>
                  <p style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.4 }}>
                    "{item.child_instruction}"
                  </p>
                </div>

                {/* Encouraging Message */}
                <div style={{ marginBottom: "1rem" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "0.2rem" }}>
                    Supportive Message:
                  </span>
                  <p style={{ fontSize: "0.88rem", color: "#cbd5e1" }}>
                    💬 <em>"{item.supportive_message}"</em>
                  </p>
                </div>

                {/* Modality & Visual Cues */}
                <div style={{ marginBottom: "1rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>Answer Modality:</span>
                    <span style={{ fontSize: "0.75rem", color: "#38bdf8", fontWeight: 600 }}>{item.answer_format}</span>
                  </div>
                  {item.visual_cues && item.visual_cues.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.25rem" }}>
                      {item.visual_cues.map((c, i) => (
                        <span key={i} style={{ fontSize: "0.72rem", background: "rgba(99, 102, 241, 0.15)", color: "#c7d2fe", padding: "2px 6px", borderRadius: "4px" }}>
                          🖼️ {c.replace(/_/g, " ")}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Reason Codes Chips */}
                <div style={{ marginTop: "auto", paddingTop: "0.75rem", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "0.35rem" }}>
                    Explainable Reason Codes:
                  </span>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                    {item.reason_codes?.map((code, idx) => (
                      <span
                        key={idx}
                        style={{
                          fontSize: "0.7rem",
                          background: "rgba(255, 255, 255, 0.05)",
                          color: "var(--text-secondary)",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          border: "1px solid rgba(255, 255, 255, 0.08)"
                        }}
                      >
                        {formatReasonCode(code)}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Child Preview Button */}
                <div style={{ marginTop: "1rem" }}>
                  <button
                    onClick={() => handleOpenChildPreview({
                      target_attempt_number: item.attempt_number,
                      support_level: item.support_level,
                      child_instruction: item.child_instruction,
                      supportive_message: item.supportive_message,
                      answer_format: item.answer_format,
                      visual_cues: item.visual_cues
                    })}
                    className="btn btn-secondary btn-sm"
                    style={{ width: "100%", fontSize: "0.78rem" }}
                  >
                    <Eye size={13} />
                    <span>Preview in Child Screen</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Adult Escalation Policy Banner */}
          <div style={{
            background: "rgba(245, 158, 11, 0.08)",
            border: "1px solid rgba(245, 158, 11, 0.25)",
            borderRadius: "var(--radius-md)",
            padding: "1rem 1.25rem",
            marginBottom: "2rem",
            display: "flex",
            alignItems: "center",
            gap: "1rem"
          }}>
            <ShieldCheck size={24} color="#fbbf24" />
            <div>
              <h4 style={{ fontSize: "0.92rem", fontWeight: 700, color: "#fde68a", marginBottom: "0.2rem" }}>
                3-Attempt Bounded Safety Policy & Non-Punitive Escalation
              </h4>
              <p style={{ fontSize: "0.82rem", color: "#e2e8f0" }}>
                If Attempt 3 is completed unsuccessfully, the system halts automated retries and presents a non-punitive helper prompt: <em>"Let's ask your teacher or helper to look together!"</em>. No child is kept in a continuous failure loop.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: Single Attempt Deep-Dive */}
      {viewMode === "single" && singleAdaptation && (
        <div className="card card-glass" style={{ marginBottom: "2rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <span className={`chip chip-${singleAdaptation.support_level}`}>
                {singleAdaptation.support_level} Support
              </span>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff" }}>
                Attempt {singleAdaptation.attempt_number} Detailed Adaptation
              </h2>
            </div>

            <button
              onClick={() => handleOpenChildPreview({
                target_attempt_number: singleAdaptation.attempt_number,
                support_level: singleAdaptation.support_level,
                child_instruction: singleAdaptation.child_instruction,
                supportive_message: singleAdaptation.supportive_message,
                answer_format: singleAdaptation.answer_format,
                visual_cues: singleAdaptation.visual_cues
              })}
              className="btn btn-primary btn-sm"
              style={{ background: "linear-gradient(135deg, #f97316 0%, #ea580c 100%)" }}
            >
              <Eye size={15} />
              <span>Launch Child Preview Screen</span>
            </button>
          </div>

          {/* Child Instruction Box */}
          <div style={{
            background: "rgba(15, 23, 42, 0.8)",
            padding: "1.5rem",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-color)",
            marginBottom: "1.5rem"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.75rem", color: "#818cf8", fontWeight: 700, textTransform: "uppercase" }}>
                Active Child Instruction Prompt
              </span>
              <span style={{
                fontSize: "0.75rem",
                fontWeight: 700,
                color: singleAdaptation.word_count <= 10 ? "#34d399" : "#fbbf24",
                background: singleAdaptation.word_count <= 10 ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
                padding: "2px 8px",
                borderRadius: "var(--radius-full)"
              }}>
                {singleAdaptation.word_count} Words (Target &le; 10, Max 12)
              </span>
            </div>

            <p style={{ fontSize: "1.4rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.4 }}>
              "{singleAdaptation.child_instruction}"
            </p>

            <p style={{ fontSize: "0.95rem", color: "#cbd5e1", marginTop: "0.5rem" }}>
              💬 {singleAdaptation.supportive_message}
            </p>
          </div>

          {/* Diagnostic Details Grid */}
          <div className="grid-2" style={{ gap: "1.25rem", marginBottom: "1.5rem" }}>
            
            {/* Left: Vocabulary Substitutions */}
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "1.25rem", borderRadius: "var(--radius-md)" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.75rem" }}>
                Vocabulary Scaffolding & Replacement
              </h3>
              {singleAdaptation.vocabulary_support && singleAdaptation.vocabulary_support.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {singleAdaptation.vocabulary_support.map((v, i) => (
                    <div key={i} style={{ background: "rgba(255,255,255,0.03)", padding: "8px 12px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-color)" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ color: "#f472b6", fontWeight: 700, fontSize: "0.85rem" }}>
                          {v.original_word} → {v.word}
                        </span>
                        <span style={{ fontSize: "0.75rem", color: "#34d399" }}>Child-friendly</span>
                      </div>
                      <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "0.2rem" }}>
                        Meaning: {v.simple_meaning}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
                  No difficult words detected in this instruction. All vocabulary matches developmental expectations for age {activeLearner?.age}.
                </p>
              )}
            </div>

            {/* Right: Modality & Visual Cues */}
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "1.25rem", borderRadius: "var(--radius-md)" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.75rem" }}>
                Interaction Format & Scaffolding Cues
              </h3>
              <div style={{ marginBottom: "0.75rem" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "0.25rem" }}>
                  INTERACTION FORMAT:
                </span>
                <span className="chip chip-type" style={{ fontSize: "0.8rem" }}>
                  {singleAdaptation.answer_format}
                </span>
              </div>

              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "0.25rem" }}>
                  ASSIGNED VISUAL CUES:
                </span>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {singleAdaptation.visual_cues && singleAdaptation.visual_cues.length > 0 ? (
                    singleAdaptation.visual_cues.map((cue, idx) => (
                      <span key={idx} style={{ fontSize: "0.78rem", background: "rgba(99, 102, 241, 0.15)", color: "#c7d2fe", padding: "3px 8px", borderRadius: "4px" }}>
                        🖼️ {cue.replace(/_/g, " ")}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Standard visual presentation</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Reason Codes Table */}
          <div style={{ marginTop: "1rem" }}>
            <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.5rem" }}>
              Explainable Decision Trace (Reason Codes)
            </h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
              {singleAdaptation.reason_codes?.map((code, idx) => (
                <div
                  key={idx}
                  style={{
                    background: "rgba(15, 23, 42, 0.9)",
                    border: "1px solid var(--border-color)",
                    padding: "6px 12px",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.8rem"
                  }}
                >
                  <span style={{ color: "#38bdf8", fontWeight: 700 }}>{formatReasonCode(code)}</span>
                  <span style={{ color: "var(--text-muted)", fontSize: "0.72rem", display: "block", fontFamily: "monospace" }}>
                    {code}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Child Preview Modal */}
      {showChildPreview && previewAdaptation && (
        <ChildPreviewModal
          adaptation={previewAdaptation}
          onClose={() => setShowChildPreview(false)}
        />
      )}
    </div>
  );
}
