import React, { useState, useEffect } from "react";
import {
  Play, RefreshCw, Sparkles, AlertTriangle, CheckCircle2, ArrowRight,
  Eye, Code2, Volume2, ShieldAlert, Activity, Check, Clock
} from "lucide-react";
import {
  createExperiment, generateInitialAdaptation, recordAttempt,
  fetchExperimentHistory, fetchComp1Output, fetchComp4Output, fetchAROutput
} from "../services/api";
import ChildPreviewModal from "./ChildPreviewModal";

export default function ScenarioDashboard({
  tasks, learners, scenarios, selectedTask, setSelectedTask,
  selectedLearner, setSelectedLearner, generationMode
}) {
  const [selectedScenario, setSelectedScenario] = useState("");
  const [activeExperiment, setActiveExperiment] = useState(null);
  const [currentAdaptation, setCurrentAdaptation] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Simulated Child Response Controls
  const [simTranscript, setSimTranscript] = useState("Fish live water.");
  const [simConfidence, setSimConfidence] = useState(0.92);
  const [showChildPreview, setShowChildPreview] = useState(false);
  const [activePayloadTab, setActivePayloadTab] = useState("comp1");
  const [payloads, setPayloads] = useState({ comp1: null, comp4: null, ar: null });

  // Handle Scenario preset selection
  const handleScenarioSelect = (scenarioCode) => {
    setSelectedScenario(scenarioCode);
    const scen = scenarios.find(s => s.scenario_code === scenarioCode);
    if (scen) {
      const l = learners.find(lrn => lrn.learner_code === scen.learner.learner_code);
      const t = tasks.find(tsk => tsk.task_code === scen.task_code);
      if (l) setSelectedLearner(l);
      if (t) setSelectedTask(t);
      if (scen.simulated_component_1?.speech_transcript) {
        setSimTranscript(scen.simulated_component_1.speech_transcript);
      }
      if (scen.simulated_component_1?.speech_confidence) {
        setSimConfidence(scen.simulated_component_1.speech_confidence);
      }
    }
  };

  // 1. Start Experiment & Generate Initial Adaptation
  const handleStartExperiment = async () => {
    if (!selectedLearner || !selectedTask) {
      setError("Please select both a learner profile and a task.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Step A: Create Experiment Run
      const exp = await createExperiment(selectedLearner.id, selectedTask.id, generationMode);
      setActiveExperiment(exp);

      // Step B: Generate Initial Adaptation (BEFORE Attempt 1)
      const adapt = await generateInitialAdaptation(exp.id);
      setCurrentAdaptation(adapt);

      // Refresh history & payloads
      const hist = await fetchExperimentHistory(exp.id);
      setHistory(hist);
      loadPayloads(exp.id);
    } catch (err) {
      setError(err.message || "Failed to start experiment");
    } finally {
      setLoading(false);
    }
  };

  // 2. Record Child Attempt
  const handleRecordAttempt = async () => {
    if (!activeExperiment || !currentAdaptation) return;

    setLoading(true);
    setError(null);
    try {
      const res = await recordAttempt(activeExperiment.id, {
        adaptation_id: currentAdaptation.id,
        speech_transcript: simTranscript,
        speech_confidence: parseFloat(simConfidence),
        response_time_ms: 8500,
        completion_status: "completed"
      });

      // Update current adaptation to next_adaptation if generated
      if (res.next_adaptation) {
        setCurrentAdaptation(res.next_adaptation);
      }

      // Update experiment status
      setActiveExperiment(prev => ({
        ...prev,
        status: res.experiment_status,
        final_outcome: res.final_outcome
      }));

      // Refresh history & payloads
      const hist = await fetchExperimentHistory(activeExperiment.id);
      setHistory(hist);
      loadPayloads(activeExperiment.id);
    } catch (err) {
      setError(err.message || "Failed to record attempt");
    } finally {
      setLoading(false);
    }
  };

  // Load Component 1, 4, AR payloads
  const loadPayloads = async (expId) => {
    try {
      const [c1, c4, ar] = await Promise.all([
        fetchComp1Output(expId).catch(() => null),
        fetchComp4Output(expId).catch(() => null),
        fetchAROutput(expId).catch(() => null)
      ]);
      setPayloads({ comp1: c1, comp4: c4, ar: ar });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <div className="section-header">
        <div>
          <h1 className="section-title">Scenario Dashboard & Adaptive Pipeline</h1>
          <p className="section-subtitle">
            Execute the complete adaptive loop: Select learner & task $\to$ Generate Initial Adaptation $\to$ Simulate responses $\to$ Progressive retries & adult escalation.
          </p>
        </div>

        {currentAdaptation && (
          <button
            onClick={() => setShowChildPreview(true)}
            className="btn btn-primary"
            style={{ background: "linear-gradient(135deg, #f97316 0%, #ea580c 100%)", boxShadow: "0 4px 14px rgba(249, 115, 22, 0.4)" }}
          >
            <Eye size={18} />
            <span>Open Child Preview Screen</span>
          </button>
        )}
      </div>

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
          gap: "0.5rem"
        }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Grid: Scenario Configuration & Control */}
      <div className="grid-2" style={{ marginBottom: "2rem" }}>
        {/* Left Column: Preset Scenarios & Learner Profile */}
        <div className="card card-glass">
          <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff", marginBottom: "1rem" }}>
            1. Select Test Scenario or Learner
          </h2>

          <div className="form-group">
            <label className="form-label">Preconfigured End-to-End Scenarios ({scenarios.length})</label>
            <select
              className="form-select"
              value={selectedScenario}
              onChange={(e) => handleScenarioSelect(e.target.value)}
            >
              <option value="">-- Choose from 20 Scenarios --</option>
              {scenarios.map(s => (
                <option key={s.scenario_code} value={s.scenario_code}>
                  {s.scenario_code}: {s.title}
                </option>
              ))}
            </select>
          </div>

          <div className="grid-2" style={{ gap: "1rem" }}>
            <div className="form-group">
              <label className="form-label">Learner Profile</label>
              <select
                className="form-select"
                value={selectedLearner?.id || ""}
                onChange={(e) => setSelectedLearner(learners.find(l => l.id === e.target.value))}
              >
                {learners.map(l => (
                  <option key={l.id} value={l.id}>
                    {l.learner_code} (Age {l.age}, {l.risk_support_level} risk)
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Preloaded Task</label>
              <select
                className="form-select"
                value={selectedTask?.id || ""}
                onChange={(e) => setSelectedTask(tasks.find(t => t.id === e.target.value))}
              >
                {tasks.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.task_code}: {t.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {selectedLearner && (
            <div style={{
              background: "rgba(0,0,0,0.25)",
              padding: "0.85rem",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.85rem",
              marginTop: "0.5rem"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <span style={{ color: "var(--text-muted)" }}>Risk Support Level:</span>
                <span className={`chip chip-${selectedLearner.risk_support_level}`}>{selectedLearner.risk_support_level}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <span style={{ color: "var(--text-muted)" }}>Vocab / Grammar:</span>
                <span style={{ color: "#ffffff" }}>{selectedLearner.vocabulary_score} / {selectedLearner.grammar_score}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Assessed English:</span>
                <span style={{ color: "#38bdf8", textTransform: "capitalize" }}>{selectedLearner.english_level}</span>
              </div>
            </div>
          )}

          <div style={{ marginTop: "1.25rem" }}>
            <button
              onClick={handleStartExperiment}
              disabled={loading}
              className="btn btn-primary"
              style={{ width: "100%" }}
            >
              <Play size={16} />
              <span>Initialize Experiment & Generate Initial Adaptation</span>
            </button>
          </div>
        </div>

        {/* Right Column: Task Objective & Protected Answers */}
        <div className="card card-glass">
          <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff", marginBottom: "1rem" }}>
            2. Active Task Inspection
          </h2>

          {selectedTask ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                <span className="chip chip-type">{selectedTask.task_type}</span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Ages: {selectedTask.minimum_age}–{selectedTask.maximum_age} yrs</span>
              </div>

              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.5rem" }}>
                {selectedTask.title}
              </h3>

              <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", marginBottom: "0.85rem" }}>
                <strong>Objective:</strong> {selectedTask.learning_objective}
              </p>

              <div style={{ background: "rgba(0,0,0,0.25)", padding: "0.75rem", borderRadius: "var(--radius-sm)", marginBottom: "0.85rem" }}>
                <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>Original Instruction:</span>
                <p style={{ fontSize: "0.88rem", color: "#e2e8f0", fontStyle: "italic" }}>
                  "{selectedTask.original_instruction}"
                </p>
              </div>

              {selectedTask.protected_answers && (
                <div style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.2)", padding: "0.75rem", borderRadius: "var(--radius-sm)" }}>
                  <span style={{ fontSize: "0.72rem", color: "#34d399", fontWeight: 700, textTransform: "uppercase" }}>Relation-Aware Answer Leakage Rule:</span>
                  <p style={{ fontSize: "0.82rem", color: "#cbd5e1", marginTop: "0.2rem" }}>
                    Restricted solutions: {selectedTask.protected_answers.restricted_solution_phrases?.join(", ") || "None"}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: "var(--text-muted)" }}>Select a task to view details.</p>
          )}
        </div>
      </div>

      {/* Active Adaptation & Response Simulator Panel */}
      {currentAdaptation && (
        <div className="card card-glass" style={{ marginBottom: "2rem", border: "1px solid rgba(99, 102, 241, 0.35)", boxShadow: "var(--shadow-glow)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <span className={`chip chip-${currentAdaptation.support_level}`}>
                {currentAdaptation.support_level} Support
              </span>
              <span style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff" }}>
                Target Attempt: {currentAdaptation.target_attempt_number} of 3
              </span>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Method: {currentAdaptation.generation_method}
              </span>
            </div>

            {activeExperiment?.status === "escalated" ? (
              <span style={{
                background: "rgba(239, 68, 68, 0.2)",
                color: "#f87171",
                border: "1px solid rgba(239, 68, 68, 0.4)",
                padding: "4px 12px",
                borderRadius: "999px",
                fontWeight: 700,
                fontSize: "0.8rem",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem"
              }}>
                <ShieldAlert size={14} />
                Adult Assistance Requested
              </span>
            ) : activeExperiment?.status === "completed" ? (
              <span style={{
                background: "rgba(16, 185, 129, 0.2)",
                color: "#34d399",
                border: "1px solid rgba(16, 185, 129, 0.4)",
                padding: "4px 12px",
                borderRadius: "999px",
                fontWeight: 700,
                fontSize: "0.8rem",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem"
              }}>
                <CheckCircle2 size={14} />
                Task Completed Successfully
              </span>
            ) : (
              <span style={{ fontSize: "0.8rem", color: "#38bdf8", fontWeight: 600 }}>
                In Progress (Attempt {currentAdaptation.target_attempt_number})
              </span>
            )}
          </div>

          {/* Generated Child Instruction Display */}
          <div style={{
            background: "rgba(15, 23, 42, 0.8)",
            padding: "1.5rem",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-color)",
            marginBottom: "1.5rem"
          }}>
            <span style={{ fontSize: "0.75rem", color: "#818cf8", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: "0.5rem" }}>
              Current Child-Friendly Instruction (Presented to Learner)
            </span>
            <p style={{ fontSize: "1.35rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.4 }}>
              "{currentAdaptation.child_instruction}"
            </p>
            {currentAdaptation.supportive_message && (
              <p style={{ fontSize: "0.95rem", color: "#a5b4fc", marginTop: "0.5rem" }}>
                💬 {currentAdaptation.supportive_message}
              </p>
            )}

            {currentAdaptation.visual_cues && currentAdaptation.visual_cues.length > 0 && (
              <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>VISUAL CUES:</span>
                {currentAdaptation.visual_cues.map((c, i) => (
                  <span key={i} style={{ fontSize: "0.75rem", background: "rgba(99, 102, 241, 0.15)", color: "#c7d2fe", padding: "2px 8px", borderRadius: "4px" }}>
                    🖼️ {c.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Response Simulator Controls */}
          {activeExperiment?.status === "active" && (
            <div style={{ background: "rgba(0,0,0,0.2)", padding: "1.25rem", borderRadius: "var(--radius-md)" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.75rem" }}>
                Simulate Child Speech Response for Attempt {currentAdaptation.target_attempt_number}
              </h3>

              <div className="grid-2" style={{ gap: "1rem" }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Speech Transcript (Simulated Component 1)</label>
                  <input
                    type="text"
                    className="form-input"
                    value={simTranscript}
                    onChange={(e) => setSimTranscript(e.target.value)}
                    placeholder='e.g., "Fish live water." or "I put crayons."'
                  />
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Speech Confidence ({simConfidence})</label>
                  <input
                    type="range"
                    min="0.4"
                    max="1.0"
                    step="0.02"
                    value={simConfidence}
                    onChange={(e) => setSimConfidence(e.target.value)}
                    style={{ marginTop: "0.5rem", accentColor: "var(--accent-primary)" }}
                  />
                  <span style={{ fontSize: "0.7rem", color: simConfidence < 0.70 ? "#f87171" : "#34d399" }}>
                    {simConfidence < 0.70 ? "Below 0.70 (Grammar errors remain unconfirmed)" : "Confidence acceptable"}
                  </span>
                </div>
              </div>

              <div style={{ marginTop: "1rem", display: "flex", gap: "0.75rem" }}>
                <button
                  onClick={handleRecordAttempt}
                  disabled={loading}
                  className="btn btn-primary"
                >
                  <RefreshCw size={16} className={loading ? "spin" : ""} />
                  <span>Submit Attempt Response & Evaluate Next Step</span>
                </button>
              </div>
            </div>
          )}

          {activeExperiment?.status === "escalated" && (
            <div style={{
              background: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              padding: "1.25rem",
              borderRadius: "var(--radius-md)",
              color: "#fecaca"
            }}>
              <h3 style={{ fontWeight: 700, fontSize: "1.1rem", marginBottom: "0.25rem" }}>
                Maximum Attempts Reached (3 of 3)
              </h3>
              <p style={{ fontSize: "0.95rem" }}>
                The progressive retry controller has paused automatic retries. Non-punitive adult escalation message displayed:
                <em> "Let's ask your teacher or helper to look together!"</em>
              </p>
            </div>
          )}
        </div>
      )}

      {/* Attempt Diagnostic History Timeline */}
      {history?.attempts && history.attempts.length > 0 && (
        <div className="card card-glass" style={{ marginBottom: "2rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Activity size={18} color="#38bdf8" />
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff" }}>
                Attempt Diagnostic History ({history.attempts.length} of 3)
              </h2>
            </div>
            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
              Acoustic Gating & Diagnostic Separation Verified
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {history.attempts.map((att) => (
              <div
                key={att.id}
                style={{
                  background: "rgba(15, 23, 42, 0.6)",
                  border: `1px solid ${
                    att.concept_result === "correct" ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"
                  }`,
                  borderRadius: "var(--radius-md)",
                  padding: "1.25rem"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{
                      background: "rgba(99, 102, 241, 0.2)",
                      color: "#818cf8",
                      fontWeight: 700,
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontSize: "0.8rem"
                    }}>
                      Attempt {att.attempt_number}
                    </span>
                    <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                      Response Time: {(att.response_time_ms / 1000).toFixed(1)}s
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{
                      padding: "3px 10px",
                      borderRadius: "var(--radius-full)",
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      textTransform: "uppercase",
                      background: att.concept_result === "correct" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                      color: att.concept_result === "correct" ? "#34d399" : "#f87171",
                      border: `1px solid ${att.concept_result === "correct" ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`
                    }}>
                      Concept: {att.concept_result}
                    </span>

                    {att.speech_confidence !== null && (
                      <span style={{
                        padding: "3px 8px",
                        borderRadius: "var(--radius-full)",
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        background: att.speech_confidence >= 0.70 ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)",
                        color: att.speech_confidence >= 0.70 ? "#a7f3d0" : "#fde047"
                      }}>
                        Acoustic Conf: {(att.speech_confidence * 100).toFixed(0)}%
                        {att.speech_confidence < 0.70 ? " (Unconfirmed)" : ""}
                      </span>
                    )}
                  </div>
                </div>

                <div style={{ marginBottom: "0.6rem" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>Instruction Shown:</span>
                  <p style={{ fontSize: "0.9rem", color: "#cbd5e1", fontStyle: "italic" }}>
                    "{att.instruction_shown}"
                  </p>
                </div>

                <div style={{ marginBottom: "0.75rem" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>Child Response:</span>
                  <p style={{ fontSize: "1rem", fontWeight: 600, color: "#ffffff" }}>
                    "{att.speech_transcript || "(No speech transcript)"}"
                  </p>
                </div>

                {/* Extracted Language Observations */}
                {att.observations && att.observations.length > 0 && (
                  <div style={{
                    background: "rgba(0,0,0,0.25)",
                    padding: "0.75rem",
                    borderRadius: "var(--radius-sm)",
                    marginTop: "0.5rem"
                  }}>
                    <span style={{ fontSize: "0.72rem", color: "#818cf8", fontWeight: 700, textTransform: "uppercase", display: "block", marginBottom: "0.4rem" }}>
                      Diagnostic Observations (Researcher Visible Only):
                    </span>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                      {att.observations.map((o) => (
                        <span
                          key={o.id}
                          style={{
                            fontSize: "0.75rem",
                            background: "rgba(99, 102, 241, 0.15)",
                            border: "1px solid rgba(99, 102, 241, 0.3)",
                            color: "#c7d2fe",
                            padding: "2px 8px",
                            borderRadius: "4px"
                          }}
                        >
                          <strong>{o.observation_code}</strong>: "{o.evidence}" {o.confirmed ? "✓" : "(unconfirmed)"}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Integration Payloads Viewer */}
      {activeExperiment && (
        <div className="card card-glass">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Code2 size={18} color="#818cf8" />
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff" }}>
                Live Integration Payloads (Components 1, 4 & AR)
              </h2>
            </div>

            <div className="nav-tabs">
              <button
                className={`nav-tab ${activePayloadTab === "comp1" ? "active" : ""}`}
                onClick={() => setActivePayloadTab("comp1")}
              >
                Component 1 (Delivery)
              </button>
              <button
                className={`nav-tab ${activePayloadTab === "comp4" ? "active" : ""}`}
                onClick={() => setActivePayloadTab("comp4")}
              >
                Component 4 (Analytics)
              </button>
              <button
                className={`nav-tab ${activePayloadTab === "ar" ? "active" : ""}`}
                onClick={() => setActivePayloadTab("ar")}
              >
                Component 3 (AR Ready)
              </button>
            </div>
          </div>

          <pre style={{
            background: "#030712",
            padding: "1.25rem",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-color)",
            color: "#a7f3d0",
            fontFamily: "monospace",
            fontSize: "0.85rem",
            overflowX: "auto",
            maxHeight: "300px"
          }}>
            {JSON.stringify(payloads[activePayloadTab] || { message: "Generating payload..." }, null, 2)}
          </pre>
        </div>
      )}

      {/* Child Preview Modal */}
      {showChildPreview && currentAdaptation && (
        <ChildPreviewModal
          adaptation={currentAdaptation}
          onClose={() => setShowChildPreview(false)}
        />
      )}
    </div>
  );
}
