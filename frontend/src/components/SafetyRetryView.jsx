import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  ArrowRight,
  Sparkles,
  HeartHandshake,
  UserCheck,
  Brain,
  FileCheck,
  Zap,
  Activity,
  Award
} from "lucide-react";
import {
  validateOutput,
  createExperiment,
  generateInitialAdaptation,
  recordAttempt,
  fetchRetryState
} from "../services/api";

export default function SafetyRetryView({ tasks, learners, selectedTask, selectedLearner }) {
  const [activeTask, setActiveTask] = useState(selectedTask || (tasks && tasks[0]) || null);
  const [activeLearner, setActiveLearner] = useState(selectedLearner || (learners && learners[0]) || null);

  // -------------------------------------------------------------
  // Sandbox State
  // -------------------------------------------------------------
  const [sandboxInstruction, setSandboxInstruction] = useState("Put your crayons in the box.");
  const [sandboxSupportive, setSandboxSupportive] = useState("You can do it!");
  const [sandboxSupportLevel, setSandboxSupportLevel] = useState("moderate");
  const [sandboxAttemptNum, setSandboxAttemptNum] = useState(1);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  // -------------------------------------------------------------
  // Simulator State (3-Attempt State Machine)
  // -------------------------------------------------------------
  const [simExperimentId, setSimExperimentId] = useState(null);
  const [simState, setSimState] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const [childTranscriptInput, setChildTranscriptInput] = useState("");
  const [simSpeechConfidence, setSimSpeechConfidence] = useState(0.9);

  // Benchmark Presets for Sandbox
  const PRESETS = [
    {
      label: "✅ Compliant Child Adaptation",
      instruction: "Put your crayons in the box.",
      supportive: "You can do it!",
      supportLevel: "moderate",
      attempt: 1,
      type: "compliant"
    },
    {
      label: "❌ Direct Solution Leak",
      instruction: "The answer is crayons in box and paper in bin.",
      supportive: "Do not get it wrong!",
      supportLevel: "mild",
      attempt: 1,
      type: "leak_direct"
    },
    {
      label: "❌ Relation Binding Leak",
      instruction: "Put the fish in the water right now.",
      supportive: "Good try!",
      supportLevel: "moderate",
      attempt: 1,
      type: "leak_relation"
    },
    {
      label: "✅ Candidate Choice Contrast (Scaffolding)",
      instruction: "Look at fish. Choose: water or tree?",
      supportive: "Take your time!",
      supportLevel: "strong",
      attempt: 3,
      type: "scaffolding"
    },
    {
      label: "❌ Harsh Punitive Language",
      instruction: "That was wrong and you failed the task.",
      supportive: "Try harder next time.",
      supportLevel: "mild",
      attempt: 2,
      type: "punitive"
    },
    {
      label: "❌ Clinical Jargon Leak",
      instruction: "Because of your DLD risk score, place the ball.",
      supportive: "This tests expressive language.",
      supportLevel: "strong",
      attempt: 1,
      type: "clinical"
    },
    {
      label: "❌ Exceeds 12 Words",
      instruction: "Before you can play outside with your friends you have to put all crayons into the box.",
      supportive: "Let's do it!",
      supportLevel: "mild",
      attempt: 1,
      type: "length"
    }
  ];

  useEffect(() => {
    if (selectedTask) setActiveTask(selectedTask);
  }, [selectedTask]);

  useEffect(() => {
    if (selectedLearner) setActiveLearner(selectedLearner);
  }, [selectedLearner]);

  // Run validation when Sandbox parameters change or on demand
  const handleValidateSandbox = async (overrideInst = null, overrideSupp = null, overrideLvl = null, overrideAtt = null) => {
    if (!activeTask) return;
    setValidating(true);
    try {
      const res = await validateOutput({
        taskId: activeTask.id,
        childInstruction: overrideInst !== null ? overrideInst : sandboxInstruction,
        supportiveMessage: overrideSupp !== null ? overrideSupp : sandboxSupportive,
        targetAttemptNumber: overrideAtt !== null ? overrideAtt : sandboxAttemptNum,
        supportLevel: overrideLvl !== null ? overrideLvl : sandboxSupportLevel,
        learnerId: activeLearner ? activeLearner.id : null
      });
      setValidationResult(res);
    } catch (err) {
      console.error("Validation error:", err);
    } finally {
      setValidating(false);
    }
  };

  // Trigger initial validation
  useEffect(() => {
    handleValidateSandbox();
  }, [activeTask]);

  const loadPreset = (preset) => {
    setSandboxInstruction(preset.instruction);
    setSandboxSupportive(preset.supportive);
    setSandboxSupportLevel(preset.supportLevel);
    setSandboxAttemptNum(preset.attempt);
    handleValidateSandbox(preset.instruction, preset.supportive, preset.supportLevel, preset.attempt);
  };

  // -------------------------------------------------------------
  // Simulator Handlers
  // -------------------------------------------------------------
  const handleStartSimulation = async () => {
    if (!activeTask || !activeLearner) return;
    setSimLoading(true);
    try {
      const exp = await createExperiment(activeLearner.id, activeTask.id, "rule");
      await generateInitialAdaptation(exp.id);
      const state = await fetchRetryState(exp.id);
      setSimExperimentId(exp.id);
      setSimState(state);
      setChildTranscriptInput("");
    } catch (err) {
      console.error("Simulation start failed:", err);
    } finally {
      setSimLoading(false);
    }
  };

  const handleSimulateResponse = async (transcriptText, confidence = 0.9) => {
    if (!simExperimentId || !simState) return;
    const currentAdaptation = simState.adaptations[simState.adaptations.length - 1];
    if (!currentAdaptation) return;

    setSimLoading(true);
    try {
      await recordAttempt(simExperimentId, {
        adaptation_id: currentAdaptation.id,
        speech_transcript: transcriptText,
        speech_confidence: confidence,
        response_time_ms: 6000,
        completion_status: "completed"
      });

      const updatedState = await fetchRetryState(simExperimentId);
      setSimState(updatedState);
      setChildTranscriptInput("");
    } catch (err) {
      console.error("Simulation step failed:", err);
    } finally {
      setSimLoading(false);
    }
  };

  const currentSimAttemptNum = simState ? (simState.attempts_count + 1) : 1;
  const currentSimAdaptation = simState && simState.adaptations.length > 0
    ? simState.adaptations[simState.adaptations.length - 1]
    : null;

  return (
    <div className="tab-content" style={{ animation: "fadeIn 0.3s ease" }}>
      {/* Top Banner */}
      <div className="card" style={{ marginBottom: "1.5rem", background: "linear-gradient(135deg, rgba(37,99,235,0.08) 0%, rgba(147,51,234,0.08) 100%)", borderColor: "rgba(59,130,246,0.3)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <div style={{ padding: "8px", borderRadius: "10px", background: "rgba(59,130,246,0.2)", color: "#60a5fa" }}>
                <ShieldCheck size={26} />
              </div>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 700, margin: 0 }}>Safety, Validation & Retry Engine</h2>
                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", margin: "4px 0 0 0" }}>
                  Sprint 4 Architecture • Relation-Aware Answer Leakage Gates • Multi-Sequence Audit • 3-Attempt Adult Escalation
                </p>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>ACTIVE TASK:</label>
              <select
                className="form-select"
                style={{ padding: "6px 12px", fontSize: "0.85rem", minWidth: "220px" }}
                value={activeTask?.id || ""}
                onChange={(e) => {
                  const t = tasks.find((item) => item.id === e.target.value);
                  if (t) setActiveTask(t);
                }}
              >
                {tasks && tasks.map((t) => (
                  <option key={t.id} value={t.id}>{t.task_code}: {t.title}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>ACTIVE LEARNER:</label>
              <select
                className="form-select"
                style={{ padding: "6px 12px", fontSize: "0.85rem", minWidth: "200px" }}
                value={activeLearner?.id || ""}
                onChange={(e) => {
                  const l = learners.find((item) => item.id === e.target.value);
                  if (l) setActiveLearner(l);
                }}
              >
                {learners && learners.map((l) => (
                  <option key={l.id} value={l.id}>{l.learner_code} ({l.risk_support_level} risk, age {l.age})</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        {/* ========================================================= */}
        {/* SECTION 1: LIVE SAFETY & LEAKAGE SANDBOX                  */}
        {/* ========================================================= */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Brain size={20} color="var(--primary)" />
              <h3 style={{ fontSize: "1.05rem", fontWeight: 600, margin: 0 }}>Safety & Leakage Sandbox</h3>
            </div>
            <span style={{ fontSize: "0.75rem", padding: "3px 8px", borderRadius: "12px", background: "rgba(59,130,246,0.15)", color: "#60a5fa" }}>
              Live Validator
            </span>
          </div>

          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "0.8rem" }}>
            Quickly test candidate instructions against protected answer relations, sentence length, and developmental safety gates.
          </p>

          {/* Preset Buttons */}
          <div style={{ marginBottom: "1.2rem" }}>
            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 600, display: "block", marginBottom: "6px" }}>
              LOAD RESEARCH BENCHMARK PRESET:
            </span>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => loadPreset(p)}
                  style={{
                    padding: "4px 9px",
                    fontSize: "0.74rem",
                    borderRadius: "6px",
                    border: "1px solid var(--border-color)",
                    background: "rgba(255,255,255,0.03)",
                    color: "var(--text-primary)",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                  onMouseOver={(e) => e.target.style.background = "rgba(255,255,255,0.08)"}
                  onMouseOut={(e) => e.target.style.background = "rgba(255,255,255,0.03)"}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Form Controls */}
          <div style={{ marginBottom: "1rem" }}>
            <label style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
              CANDIDATE CHILD INSTRUCTION:
            </label>
            <textarea
              className="form-control"
              style={{ width: "100%", minHeight: "75px", fontSize: "0.95rem", lineHeight: 1.4, padding: "8px 12px" }}
              value={sandboxInstruction}
              onChange={(e) => setSandboxInstruction(e.target.value)}
              placeholder="Enter instruction to validate..."
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem", marginBottom: "1.2rem" }}>
            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                SUPPORTIVE MESSAGE:
              </label>
              <input
                className="form-control"
                style={{ width: "100%", padding: "6px 10px", fontSize: "0.85rem" }}
                value={sandboxSupportive}
                onChange={(e) => setSandboxSupportive(e.target.value)}
                placeholder="e.g. You can do it!"
              />
            </div>

            <div>
              <label style={{ fontSize: "0.75rem", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
                SUPPORT LEVEL:
              </label>
              <select
                className="form-select"
                style={{ width: "100%", padding: "6px 10px", fontSize: "0.85rem" }}
                value={sandboxSupportLevel}
                onChange={(e) => setSandboxSupportLevel(e.target.value)}
              >
                <option value="mild">Mild Support</option>
                <option value="moderate">Moderate Support</option>
                <option value="strong">Strong Support</option>
              </select>
            </div>
          </div>

          <button
            className="btn btn-primary"
            style={{ width: "100%", padding: "8px", fontWeight: 600, fontSize: "0.9rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}
            onClick={() => handleValidateSandbox()}
            disabled={validating}
          >
            {validating ? <RefreshCw size={16} className="spin" /> : <ShieldCheck size={16} />}
            <span>Validate Candidate Output</span>
          </button>

          {/* Validation Result Inspection Card */}
          {validationResult && (
            <div style={{ marginTop: "1.5rem", padding: "1rem", borderRadius: "10px", background: "rgba(0,0,0,0.25)", border: `1px solid ${validationResult.status === "approved" ? "rgba(34,197,94,0.4)" : "rgba(239,68,68,0.4)"}` }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.8rem" }}>
                <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)" }}>VALIDATION STATUS:</span>
                <span style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.3rem",
                  padding: "4px 10px",
                  borderRadius: "14px",
                  fontSize: "0.82rem",
                  fontWeight: 700,
                  background: validationResult.status === "approved" ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)",
                  color: validationResult.status === "approved" ? "#4ade80" : "#f87171"
                }}>
                  {validationResult.status === "approved" ? <CheckCircle2 size={15} /> : <XCircle size={15} />}
                  {validationResult.status.toUpperCase()}
                </span>
              </div>

              {/* Grid of Gates */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.6rem", fontSize: "0.78rem", marginBottom: "0.8rem" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "6px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Answer Leakage:</span>
                  <span style={{ color: validationResult.answer_leakage ? "#f87171" : "#4ade80", fontWeight: 700 }}>
                    {validationResult.answer_leakage ? "DETECTED (Fail)" : "None (Pass)"}
                  </span>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "6px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Length (≤ 12 words):</span>
                  <span style={{ color: validationResult.sentence_length_valid ? "#4ade80" : "#f87171", fontWeight: 700 }}>
                    {validationResult.maximum_words_in_sentence} words {validationResult.sentence_length_valid ? "(Pass)" : "(Too Long)"}
                  </span>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "6px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Child Safety & Tone:</span>
                  <span style={{ color: validationResult.safety_valid ? "#4ade80" : "#f87171", fontWeight: 700 }}>
                    {validationResult.safety_valid ? "Safe (Pass)" : "Violations (Fail)"}
                  </span>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "6px 8px", background: "rgba(255,255,255,0.03)", borderRadius: "6px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Meaning Preserved:</span>
                  <span style={{ color: "#60a5fa", fontWeight: 700 }}>
                    {(validationResult.semantic_score * 100).toFixed(0)}% score
                  </span>
                </div>
              </div>

              {/* Failure Reasons list if any */}
              {validationResult.failure_reasons && validationResult.failure_reasons.length > 0 && (
                <div style={{ marginTop: "0.6rem", padding: "8px", borderRadius: "6px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)" }}>
                  <span style={{ fontSize: "0.72rem", fontWeight: 700, color: "#f87171", display: "block", marginBottom: "4px" }}>
                    DETECTED FAILURE REASONS:
                  </span>
                  <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.75rem", color: "#fca5a5" }}>
                    {validationResult.failure_reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ========================================================= */}
        {/* SECTION 2: INTERACTIVE 3-ATTEMPT STATE MACHINE SIMULATOR  */}
        {/* ========================================================= */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Activity size={20} color="#a855f7" />
              <h3 style={{ fontSize: "1.05rem", fontWeight: 600, margin: 0 }}>3-Attempt Retry Simulator</h3>
            </div>

            <button
              className="btn btn-secondary"
              style={{ fontSize: "0.78rem", padding: "4px 10px", display: "flex", alignItems: "center", gap: "0.4rem" }}
              onClick={handleStartSimulation}
              disabled={simLoading}
            >
              <RefreshCw size={13} className={simLoading ? "spin" : ""} />
              <span>{simExperimentId ? "Restart Simulation" : "Start Simulation"}</span>
            </button>
          </div>

          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
            Simulate the full retry escalation loop: Attempt 1 $\to$ Attempt 2 $\to$ Attempt 3 $\to$ Non-punitive adult escalation.
          </p>

          {/* State Machine Step Progress Bar */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", margin: "1.2rem 0", padding: "10px 14px", borderRadius: "10px", background: "rgba(0,0,0,0.3)" }}>
            {/* Step 1 */}
            <div style={{ textAlign: "center", flex: 1, opacity: currentSimAttemptNum >= 1 ? 1 : 0.4 }}>
              <div style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: currentSimAttemptNum === 1 ? "#3b82f6" : (currentSimAttemptNum > 1 ? "#22c55e" : "#475569"),
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 4px auto",
                fontWeight: 700,
                fontSize: "0.8rem",
                boxShadow: currentSimAttemptNum === 1 ? "0 0 10px rgba(59,130,246,0.6)" : "none"
              }}>
                1
              </div>
              <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontWeight: 600 }}>Attempt 1</span>
            </div>

            <ArrowRight size={14} color="var(--text-muted)" />

            {/* Step 2 */}
            <div style={{ textAlign: "center", flex: 1, opacity: currentSimAttemptNum >= 2 ? 1 : 0.4 }}>
              <div style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: currentSimAttemptNum === 2 ? "#3b82f6" : (currentSimAttemptNum > 2 ? "#22c55e" : "#475569"),
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 4px auto",
                fontWeight: 700,
                fontSize: "0.8rem",
                boxShadow: currentSimAttemptNum === 2 ? "0 0 10px rgba(59,130,246,0.6)" : "none"
              }}>
                2
              </div>
              <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontWeight: 600 }}>Attempt 2 (Split)</span>
            </div>

            <ArrowRight size={14} color="var(--text-muted)" />

            {/* Step 3 */}
            <div style={{ textAlign: "center", flex: 1, opacity: currentSimAttemptNum >= 3 ? 1 : 0.4 }}>
              <div style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: currentSimAttemptNum === 3 ? "#3b82f6" : (currentSimAttemptNum > 3 ? "#22c55e" : "#475569"),
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 4px auto",
                fontWeight: 700,
                fontSize: "0.8rem",
                boxShadow: currentSimAttemptNum === 3 ? "0 0 10px rgba(59,130,246,0.6)" : "none"
              }}>
                3
              </div>
              <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontWeight: 600 }}>Attempt 3 (Choice)</span>
            </div>

            <ArrowRight size={14} color="var(--text-muted)" />

            {/* Step Escalation */}
            <div style={{ textAlign: "center", flex: 1, opacity: simState?.status === "escalated" ? 1 : 0.4 }}>
              <div style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: simState?.status === "escalated" ? "#f59e0b" : "#475569",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 4px auto",
                fontWeight: 700,
                fontSize: "0.8rem",
                boxShadow: simState?.status === "escalated" ? "0 0 10px rgba(245,158,11,0.6)" : "none"
              }}>
                <HeartHandshake size={14} />
              </div>
              <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontWeight: 600 }}>Adult Support</span>
            </div>
          </div>

          {!simState ? (
            <div style={{ textAlign: "center", padding: "2.5rem 1rem", border: "1px dashed var(--border-color)", borderRadius: "10px" }}>
              <Zap size={32} color="var(--text-muted)" style={{ marginBottom: "0.5rem" }} />
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", margin: 0 }}>
                Click "Start Simulation" to initialize the 3-attempt state machine with {activeLearner?.learner_code}.
              </p>
            </div>
          ) : (
            <div>
              {/* If completed with success */}
              {simState.status === "completed" && (
                <div style={{ padding: "1.2rem", borderRadius: "10px", background: "rgba(34,197,94,0.15)", border: "1px solid rgba(34,197,94,0.4)", textAlign: "center", marginBottom: "1rem" }}>
                  <Award size={36} color="#4ade80" style={{ margin: "0 auto 8px auto" }} />
                  <h4 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#4ade80", margin: "0 0 4px 0" }}>Scenario Completed Successfully!</h4>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", margin: 0 }}>
                    Learner successfully completed the concept on Attempt {simState.attempts_count}. Component 4 progress event dispatched.
                  </p>
                </div>
              )}

              {/* If escalated to adult support */}
              {simState.status === "escalated" && simState.escalation_info && (
                <div style={{ marginBottom: "1rem" }}>
                  {/* Child reassurance view */}
                  <div style={{ padding: "1.2rem", borderRadius: "10px", background: "linear-gradient(135deg, rgba(245,158,11,0.15), rgba(234,88,12,0.15))", border: "1px solid rgba(245,158,11,0.4)", textAlign: "center", marginBottom: "1rem" }}>
                    <HeartHandshake size={36} color="#fbbf24" style={{ margin: "0 auto 8px auto" }} />
                    <h4 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fbbf24", margin: "0 0 6px 0" }}>
                      {simState.escalation_info.child_message}
                    </h4>
                    <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", margin: 0 }}>
                      Non-punitive support boundary: Zero error buzzers shown to child. Warm cooperative invitation.
                    </p>
                  </div>

                  {/* Clinician / Researcher Diagnostic Card */}
                  <div style={{ padding: "1rem", borderRadius: "8px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-color)", fontSize: "0.8rem" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#60a5fa", display: "block", marginBottom: "4px" }}>
                      RESEARCHER & CLINICIAN DIAGNOSTIC SUMMARY:
                    </span>
                    <p style={{ color: "var(--text-secondary)", margin: "0 0 8px 0", lineHeight: 1.4 }}>
                      {simState.escalation_info.researcher_summary}
                    </p>
                    <div style={{ display: "flex", gap: "1rem", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                      <span>Attempts: <strong>3</strong></span>
                      <span>Outcome: <strong style={{ color: "#fbbf24" }}>adult_support</strong></span>
                    </div>
                  </div>
                </div>
              )}

              {/* Active Adaptation Card (if still active) */}
              {simState.status === "active" && currentSimAdaptation && (
                <div style={{ padding: "1rem", borderRadius: "10px", background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-color)", marginBottom: "1rem" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.6rem" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#60a5fa" }}>
                      ATTEMPT {currentSimAdaptation.target_attempt_number} ACTIVE INSTRUCTION
                    </span>
                    <span style={{
                      fontSize: "0.72rem",
                      padding: "2px 8px",
                      borderRadius: "10px",
                      background: currentSimAdaptation.support_level === "strong" ? "rgba(239,68,68,0.2)" : (currentSimAdaptation.support_level === "moderate" ? "rgba(245,158,11,0.2)" : "rgba(34,197,94,0.2)"),
                      color: currentSimAdaptation.support_level === "strong" ? "#f87171" : (currentSimAdaptation.support_level === "moderate" ? "#fbbf24" : "#4ade80"),
                      fontWeight: 700
                    }}>
                      {currentSimAdaptation.support_level.toUpperCase()} SUPPORT
                    </span>
                  </div>

                  <div style={{ fontSize: "1.05rem", fontWeight: 600, color: "#fff", marginBottom: "0.5rem" }}>
                    "{currentSimAdaptation.child_instruction}"
                  </div>

                  {currentSimAdaptation.supportive_message && (
                    <div style={{ fontSize: "0.82rem", color: "#a78bfa", fontStyle: "italic", marginBottom: "0.8rem" }}>
                      Supportive prompt: "{currentSimAdaptation.supportive_message}"
                    </div>
                  )}

                  {/* Visual Cues & Format */}
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    <span style={{ background: "rgba(255,255,255,0.06)", padding: "2px 7px", borderRadius: "4px" }}>
                      Format: {currentSimAdaptation.answer_format}
                    </span>
                    {currentSimAdaptation.visual_cues && currentSimAdaptation.visual_cues.map((c, i) => (
                      <span key={i} style={{ background: "rgba(59,130,246,0.15)", color: "#93c5fd", padding: "2px 7px", borderRadius: "4px" }}>
                        Cue: {c}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Simulation Inputs (if active) */}
              {simState.status === "active" && (
                <div>
                  <span style={{ fontSize: "0.74rem", fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                    SIMULATE CHILD ATTEMPT RESPONSE:
                  </span>

                  <div style={{ display: "flex", gap: "6px", marginBottom: "0.8rem" }}>
                    <button
                      className="btn btn-secondary"
                      style={{ flex: 1, fontSize: "0.75rem", padding: "6px" }}
                      onClick={() => handleSimulateResponse("Fish live in water.", 0.95)}
                      disabled={simLoading}
                    >
                      🎯 Correct Response
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ flex: 1, fontSize: "0.75rem", padding: "6px" }}
                      onClick={() => handleSimulateResponse("Fish live in a tree.", 0.9)}
                      disabled={simLoading}
                    >
                      ⚠️ Incorrect Concept
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ flex: 1, fontSize: "0.75rem", padding: "6px" }}
                      onClick={() => handleSimulateResponse("I don't know.", 0.85)}
                      disabled={simLoading}
                    >
                      ❓ Unclear / Dropoff
                    </button>
                  </div>

                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <input
                      className="form-control"
                      style={{ flex: 1, padding: "6px 10px", fontSize: "0.85rem" }}
                      placeholder="Or type custom simulated transcript..."
                      value={childTranscriptInput}
                      onChange={(e) => setChildTranscriptInput(e.target.value)}
                    />
                    <button
                      className="btn btn-primary"
                      style={{ fontSize: "0.8rem", padding: "6px 12px" }}
                      disabled={!childTranscriptInput.trim() || simLoading}
                      onClick={() => handleSimulateResponse(childTranscriptInput, simSpeechConfidence)}
                    >
                      Submit
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
