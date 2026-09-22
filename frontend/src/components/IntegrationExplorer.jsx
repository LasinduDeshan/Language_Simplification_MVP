import React, { useState, useEffect } from "react";
import {
  Cpu, Layers, Box, Activity, CheckCircle2, AlertTriangle,
  Copy, Check, RefreshCw, Zap, ShieldCheck, Database,
  ArrowRight, Radio, Compass, Eye, Sparkles
} from "lucide-react";
import {
  fetchGeneratorComparison, fetchComp1Output, fetchComp4Output,
  fetchAROutput, fetchIntegrationEvents, createExperiment,
  generateInitialAdaptation
} from "../services/api";

export default function IntegrationExplorer({
  tasks = [],
  learners = [],
  selectedTask,
  setSelectedTask,
  selectedLearner,
  setSelectedLearner
}) {
  const [currentTaskId, setCurrentTaskId] = useState(selectedTask?.id || (tasks[0]?.id || ""));
  const [currentLearnerId, setCurrentLearnerId] = useState(selectedLearner?.id || (learners[0]?.id || ""));
  const [attemptNumber, setAttemptNumber] = useState(1);

  // Comparison State
  const [comparisonData, setComparisonData] = useState(null);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);

  // Subsystem Payloads State
  const [activeSubsystem, setActiveSubsystem] = useState("comp1"); // comp1, comp3_ar, comp4
  const [simulatedExpId, setSimulatedExpId] = useState(null);
  const [comp1Payload, setComp1Payload] = useState(null);
  const [arPayload, setArPayload] = useState(null);
  const [comp4Payload, setComp4Payload] = useState(null);
  const [integrationEvents, setIntegrationEvents] = useState([]);
  const [loadingPayloads, setLoadingPayloads] = useState(false);

  // Sync props if changed externally
  useEffect(() => {
    if (selectedTask?.id) setCurrentTaskId(selectedTask.id);
  }, [selectedTask]);

  useEffect(() => {
    if (selectedLearner?.id) setCurrentLearnerId(selectedLearner.id);
  }, [selectedLearner]);

  // Load Comparison on mount or task/learner/attempt change
  useEffect(() => {
    if (currentTaskId && currentLearnerId) {
      loadComparison();
      ensureExperimentPayloads();
    }
  }, [currentTaskId, currentLearnerId, attemptNumber]);

  async function loadComparison() {
    setLoadingComparison(true);
    try {
      const data = await fetchGeneratorComparison(currentTaskId, currentLearnerId, attemptNumber);
      setComparisonData(data);
    } catch (err) {
      console.error("Failed to load generator comparison:", err);
    } finally {
      setLoadingComparison(false);
    }
  }

  async function ensureExperimentPayloads() {
    setLoadingPayloads(true);
    try {
      // 1. Create a simulated experiment run for the current task/learner with hybrid mode
      const exp = await createExperiment(currentLearnerId, currentTaskId, "hybrid");
      setSimulatedExpId(exp.id);

      // 2. Generate initial adaptation
      await generateInitialAdaptation(exp.id);

      // 3. Fetch all 3 external component payloads
      const [c1, ar, c4, evts] = await Promise.all([
        fetchComp1Output(exp.id).catch(() => null),
        fetchAROutput(exp.id).catch(() => null),
        fetchComp4Output(exp.id).catch(() => null),
        fetchIntegrationEvents(exp.id).catch(() => [])
      ]);

      setComp1Payload(c1);
      setArPayload(ar);
      setComp4Payload(c4);
      setIntegrationEvents(evts || []);
    } catch (err) {
      console.error("Error creating/fetching integration payloads:", err);
    } finally {
      setLoadingPayloads(false);
    }
  }

  function handleCopyJson(data, key) {
    if (!data) return;
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  }

  const activeTask = tasks.find(t => t.id === currentTaskId) || tasks[0];
  const activeLearner = learners.find(l => l.id === currentLearnerId) || learners[0];

  return (
    <div className="tab-content" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Top Banner */}
      <div className="card" style={{ background: "linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.12) 100%)", border: "1px solid rgba(99, 102, 241, 0.25)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.35rem" }}>
              <div style={{ padding: "6px", borderRadius: "8px", background: "var(--primary)", color: "white" }}>
                <Cpu size={20} />
              </div>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 700, margin: 0 }}>
                LLM Generation & External Integration Studio
              </h2>
              <span className="badge badge-purple" style={{ fontSize: "0.75rem" }}>Sprint 5 Ready</span>
            </div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", maxWidth: "800px", margin: 0 }}>
              Live side-by-side benchmarking of <strong>Rule-based</strong>, <strong>Simulated/Live LLM</strong>, and <strong>Hybrid verified-safe</strong> generators. Inspect integration payloads dispatched to Component 1 (Task Delivery), Component 3 (AR Subsystem), and Component 4 (Learner Modeling).
            </p>
          </div>

          <button
            className="btn btn-primary"
            style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}
            onClick={loadComparison}
            disabled={loadingComparison}
          >
            <RefreshCw size={15} className={loadingComparison ? "spin" : ""} />
            <span>{loadingComparison ? "Benchmarking..." : "Re-Benchmark Generators"}</span>
          </button>
        </div>

        {/* Controls Toolbar */}
        <div style={{ display: "flex", gap: "1rem", marginTop: "1.25rem", flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem", minWidth: "220px" }}>
            <label style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-secondary)" }}>
              SELECT APPLICATION TASK (10)
            </label>
            <select
              className="form-select"
              value={currentTaskId}
              onChange={(e) => {
                setCurrentTaskId(e.target.value);
                const t = tasks.find(item => item.id === e.target.value);
                if (t && setSelectedTask) setSelectedTask(t);
              }}
            >
              {tasks.map(t => (
                <option key={t.id} value={t.id}>
                  {t.task_code} - {t.title}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem", minWidth: "200px" }}>
            <label style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-secondary)" }}>
              TARGET LEARNER (5 PROFILES)
            </label>
            <select
              className="form-select"
              value={currentLearnerId}
              onChange={(e) => {
                setCurrentLearnerId(e.target.value);
                const l = learners.find(item => item.id === e.target.value);
                if (l && setSelectedLearner) setSelectedLearner(l);
              }}
            >
              {learners.map(l => (
                <option key={l.id} value={l.id}>
                  {l.learner_code} (Age {l.age}, {l.risk_support_level} risk)
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <label style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-secondary)" }}>
              ATTEMPT NUMBER (SCAFFOLD ESCALATION)
            </label>
            <div style={{ display: "flex", gap: "0.35rem" }}>
              {[1, 2, 3].map(num => (
                <button
                  key={num}
                  className={`btn ${attemptNumber === num ? "btn-primary" : "btn-outline"}`}
                  style={{ padding: "5px 14px", fontSize: "0.8rem" }}
                  onClick={() => setAttemptNumber(num)}
                >
                  Attempt {num}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 1: SIDE-BY-SIDE GENERATOR BENCHMARK */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Sparkles size={18} style={{ color: "var(--primary)" }} />
            <h3 style={{ fontSize: "1.05rem", fontWeight: 700, margin: 0 }}>
              Triple-Generator Head-to-Head Comparison
            </h3>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              (Target: ≤ 8–10 words, Max: 12 words)
            </span>
          </div>
          {comparisonData && (
            <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.8rem" }}>
              <span className="badge badge-blue">Support: {comparisonData.support_level?.toUpperCase()}</span>
              <span className="badge badge-purple">Attempt {comparisonData.target_attempt_number}</span>
            </div>
          )}
        </div>

        {loadingComparison ? (
          <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
            <RefreshCw size={28} className="spin" style={{ color: "var(--primary)", margin: "0 auto 1rem" }} />
            <p style={{ color: "var(--text-secondary)", margin: 0 }}>Evaluating Rule, LLM, and Hybrid Generators...</p>
          </div>
        ) : comparisonData?.comparison ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.25rem" }}>
            {/* 1. Rule Generator Card */}
            <GeneratorCard
              title="Deterministic Rule Engine"
              subtitle="100% Offline & Template Driven"
              tag="Baseline Rule"
              tagColor="blue"
              data={comparisonData.comparison.rule}
              isTarget={false}
            />

            {/* 2. LLM Generator Card */}
            <GeneratorCard
              title="LLM Generator Engine"
              subtitle="Gemini 1.5 Flash / GPT-4o-mini"
              tag="Generative LLM"
              tagColor="purple"
              data={comparisonData.comparison.llm}
              isTarget={false}
            />

            {/* 3. Hybrid Generator Card (Target) */}
            <GeneratorCard
              title="Hybrid Engine (Target)"
              subtitle="LLM-First with Validator Fallback"
              tag="Recommended"
              tagColor="green"
              data={comparisonData.comparison.hybrid}
              isTarget={true}
            />
          </div>
        ) : null}
      </div>

      {/* SECTION 2: EXTERNAL SUBSYSTEMS PAYLOAD INSPECTOR & AR VISUALIZER */}
      <div className="card" style={{ marginTop: "0.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)", paddingBottom: "1rem", marginBottom: "1.25rem", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Layers size={18} style={{ color: "var(--primary)" }} />
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, margin: 0 }}>
                External Subsystem Integration Payloads
              </h3>
            </div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem", margin: "0.25rem 0 0" }}>
              Simulated payloads dispatched across Component 1 (Delivery), Component 3 (AR), and Component 4 (Analytics).
            </p>
          </div>

          {/* Subsystem Navigation Tabs */}
          <div style={{ display: "flex", gap: "0.4rem", background: "var(--bg-card)", padding: "4px", borderRadius: "8px", border: "1px solid var(--border)" }}>
            <button
              className={`btn ${activeSubsystem === "comp1" ? "btn-primary" : "btn-outline"}`}
              style={{ padding: "6px 12px", fontSize: "0.78rem" }}
              onClick={() => setActiveSubsystem("comp1")}
            >
              Component 1 (Delivery)
            </button>
            <button
              className={`btn ${activeSubsystem === "comp3_ar" ? "btn-primary" : "btn-outline"}`}
              style={{ padding: "6px 12px", fontSize: "0.78rem" }}
              onClick={() => setActiveSubsystem("comp3_ar")}
            >
              Component 3 (AR Preview)
            </button>
            <button
              className={`btn ${activeSubsystem === "comp4" ? "btn-primary" : "btn-outline"}`}
              style={{ padding: "6px 12px", fontSize: "0.78rem" }}
              onClick={() => setActiveSubsystem("comp4")}
            >
              Component 4 (Analytics)
            </button>
          </div>
        </div>

        {loadingPayloads ? (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <RefreshCw size={24} className="spin" style={{ color: "var(--primary)", margin: "0 auto 0.5rem" }} />
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>Synchronizing integration payloads...</p>
          </div>
        ) : (
          <div>
            {/* Component 1 View */}
            {activeSubsystem === "comp1" && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                    <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                      TASK DELIVERY SUB-SYSTEM JSON
                    </span>
                    <button
                      className="btn btn-outline"
                      style={{ padding: "3px 8px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "0.3rem" }}
                      onClick={() => handleCopyJson(comp1Payload, "comp1")}
                    >
                      {copiedKey === "comp1" ? <Check size={12} style={{ color: "var(--success)" }} /> : <Copy size={12} />}
                      <span>{copiedKey === "comp1" ? "Copied!" : "Copy JSON"}</span>
                    </button>
                  </div>
                  <pre className="code-block" style={{ maxHeight: "320px", overflow: "auto", fontSize: "0.78rem" }}>
                    {JSON.stringify(comp1Payload, null, 2)}
                  </pre>
                </div>

                <div>
                  <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: "0.5rem" }}>
                    CHILD SIMULATED DELIVERY SCREEN
                  </span>
                  <div className="card" style={{ background: "rgba(15, 23, 42, 0.7)", border: "2px dashed var(--primary)", borderRadius: "12px", padding: "1.5rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                      <span className="badge badge-blue">Attempt {comp1Payload?.attempt_number || 1}</span>
                      <span className="badge badge-green" style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                        <ShieldCheck size={12} /> Anti-Leakage Verified
                      </span>
                    </div>

                    <div style={{ textAlign: "center", padding: "1.5rem 1rem", background: "rgba(99, 102, 241, 0.08)", borderRadius: "10px", marginBottom: "1rem" }}>
                      <p style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", margin: "0 0 0.5rem" }}>
                        "{comp1Payload?.child_instruction}"
                      </p>
                      {comp1Payload?.supportive_message && (
                        <p style={{ fontSize: "0.85rem", color: "var(--primary)", fontStyle: "italic", margin: 0 }}>
                          ✨ {comp1Payload.supportive_message}
                        </p>
                      )}
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "var(--text-muted)" }}>
                      <span>Input Format: <strong>{comp1Payload?.answer_format}</strong></span>
                      <span>Visual Cues: <strong>{(comp1Payload?.cues || []).join(", ") || "None"}</strong></span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Component 3 AR View */}
            {activeSubsystem === "comp3_ar" && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                    <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                      AR SUBSYSTEM PAYLOAD SCHEMA
                    </span>
                    <button
                      className="btn btn-outline"
                      style={{ padding: "3px 8px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "0.3rem" }}
                      onClick={() => handleCopyJson(arPayload, "ar")}
                    >
                      {copiedKey === "ar" ? <Check size={12} style={{ color: "var(--success)" }} /> : <Copy size={12} />}
                      <span>{copiedKey === "ar" ? "Copied!" : "Copy JSON"}</span>
                    </button>
                  </div>
                  <pre className="code-block" style={{ maxHeight: "320px", overflow: "auto", fontSize: "0.78rem" }}>
                    {JSON.stringify(arPayload, null, 2)}
                  </pre>
                </div>

                <div>
                  <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: "0.5rem" }}>
                    INTERACTIVE AR 3D TABLETOP VISUALIZER
                  </span>
                  <div className="card" style={{ background: "#0a0e1a", border: "1px solid rgba(99, 102, 241, 0.4)", borderRadius: "12px", padding: "1.25rem", position: "relative", minHeight: "320px", overflow: "hidden" }}>
                    {/* Simulated 3D Grid Overlay */}
                    <div style={{
                      position: "absolute",
                      top: 0, left: 0, right: 0, bottom: 0,
                      backgroundImage: "radial-gradient(rgba(99, 102, 241, 0.15) 1px, transparent 1px)",
                      backgroundSize: "20px 20px",
                      opacity: 0.8
                    }} />

                    <div style={{ position: "relative", zIndex: 2 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                        <span className="badge badge-purple" style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
                          <Compass size={12} /> Anchor: {arPayload?.spatial_anchors?.workspace_plane || "tabletop"}
                        </span>
                        <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                          Center: [0, 0, -0.5m]
                        </span>
                      </div>

                      {/* AR Audio Cue Prompt */}
                      <div style={{ background: "rgba(168, 85, 247, 0.15)", border: "1px solid rgba(168, 85, 247, 0.3)", borderRadius: "8px", padding: "0.75rem", marginBottom: "1.5rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.75rem", color: "#c084fc", fontWeight: 600, marginBottom: "0.2rem" }}>
                          <Radio size={12} className="spin" /> SPATIAL AUDIO DIRECTIVE:
                        </div>
                        <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "white" }}>
                          "{arPayload?.audio_text || arPayload?.child_instruction}"
                        </div>
                      </div>

                      {/* Interactive 3D Objects */}
                      <div style={{ display: "flex", justifyContent: "center", gap: "1.5rem", flexWrap: "wrap", padding: "1rem 0" }}>
                        {(arPayload?.object_labels || ["item_a", "item_b"]).map((label, idx) => {
                          const isHighlighted = (arPayload?.highlight_targets || []).some(t => t.toLowerCase().includes(label.toLowerCase()) || idx === 0);
                          return (
                            <div
                              key={label}
                              style={{
                                padding: "1rem 1.25rem",
                                borderRadius: "10px",
                                background: isHighlighted ? "rgba(99, 102, 241, 0.25)" : "rgba(30, 41, 59, 0.6)",
                                border: isHighlighted ? "2px solid #818cf8" : "1px solid rgba(255, 255, 255, 0.1)",
                                boxShadow: isHighlighted ? "0 0 16px rgba(99, 102, 241, 0.4)" : "none",
                                textAlign: "center",
                                minWidth: "110px",
                                transform: isHighlighted ? "scale(1.05)" : "scale(1)",
                                transition: "all 0.3s ease"
                              }}
                            >
                              <Box size={24} style={{ color: isHighlighted ? "#818cf8" : "#94a3b8", margin: "0 auto 0.4rem" }} />
                              <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "white", textTransform: "capitalize" }}>
                                {label.replace(/_/g, " ")}
                              </div>
                              <span style={{ fontSize: "0.68rem", color: isHighlighted ? "#a5b4fc" : "#64748b" }}>
                                {isHighlighted ? "PULSING CUE" : "SPATIAL ANCHOR"}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Component 4 View */}
            {activeSubsystem === "comp4" && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                    <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)" }}>
                      LEARNER MODELING / ANALYTICS JSON
                    </span>
                    <button
                      className="btn btn-outline"
                      style={{ padding: "3px 8px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "0.3rem" }}
                      onClick={() => handleCopyJson(comp4Payload, "comp4")}
                    >
                      {copiedKey === "comp4" ? <Check size={12} style={{ color: "var(--success)" }} /> : <Copy size={12} />}
                      <span>{copiedKey === "comp4" ? "Copied!" : "Copy JSON"}</span>
                    </button>
                  </div>
                  <pre className="code-block" style={{ maxHeight: "320px", overflow: "auto", fontSize: "0.78rem" }}>
                    {JSON.stringify(comp4Payload, null, 2)}
                  </pre>
                </div>

                <div>
                  <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: "0.5rem" }}>
                    ANALYTICS SUMMARY CARD
                  </span>
                  <div className="card" style={{ background: "rgba(15, 23, 42, 0.7)", borderRadius: "12px", padding: "1.5rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                      <span className="badge badge-purple">Learner: {comp4Payload?.learner_id}</span>
                      <span className="badge badge-blue">Recommendation: {comp4Payload?.next_recommendation}</span>
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                      <div className="card" style={{ background: "rgba(30, 41, 59, 0.5)", padding: "0.75rem", textAlign: "center" }}>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>OBSERVED PATTERNS</div>
                        <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--text-primary)", marginTop: "0.2rem" }}>
                          {comp4Payload?.observed_patterns?.length || 0}
                        </div>
                      </div>
                      <div className="card" style={{ background: "rgba(30, 41, 59, 0.5)", padding: "0.75rem", textAlign: "center" }}>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>PROCESSING LATENCY</div>
                        <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--success)", marginTop: "0.2rem" }}>
                          {comp4Payload?.processing_time_ms || 45}ms
                        </div>
                      </div>
                    </div>

                    <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                      <p style={{ margin: "0 0 0.5rem", fontWeight: 600 }}>Clinician Diagnostic Summary:</p>
                      <p style={{ margin: 0, fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        Patterns identified through offline spaCy grammar analysis and vocabulary drop-off detection. Codes are child-hidden and strictly available to researchers and speech pathologists.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* SECTION 3: INTEGRATION EVENTS STREAM */}
      <div className="card">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
          <Database size={18} style={{ color: "var(--primary)" }} />
          <h3 style={{ fontSize: "1.05rem", fontWeight: 700, margin: 0 }}>
            Chronological Integration Event Stream ({integrationEvents.length} Events)
          </h3>
        </div>

        {integrationEvents.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", margin: 0 }}>
            No integration events recorded yet for this session. Events are automatically recorded when payloads are dispatched.
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {integrationEvents.map((ev, index) => (
              <div
                key={ev.id || index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.75rem 1rem",
                  background: "rgba(30, 41, 59, 0.4)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  fontSize: "0.82rem"
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span className={`badge ${ev.target_component === "component_1" ? "badge-blue" : ev.target_component === "component_3_ar" ? "badge-purple" : "badge-green"}`}>
                    {ev.target_component}
                  </span>
                  <strong style={{ color: "var(--text-primary)" }}>{ev.event_type}</strong>
                  <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
                    Status: <strong style={{ color: "var(--success)" }}>{ev.delivery_status}</strong>
                  </span>
                </div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
                  {ev.created_at ? new Date(ev.created_at).toLocaleTimeString() : "Just now"}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function GeneratorCard({ title, subtitle, tag, tagColor, data, isTarget }) {
  if (!data) return null;

  const isApproved = data.validation_status === "approved";
  const wordCount = data.word_count || 0;
  const wordCountValid = wordCount <= 12;

  return (
    <div
      className="card"
      style={{
        border: isTarget ? "2px solid #818cf8" : "1px solid var(--border)",
        boxShadow: isTarget ? "0 0 20px rgba(99, 102, 241, 0.18)" : "none",
        background: isTarget ? "linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)" : "rgba(30, 41, 59, 0.4)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between"
      }}
    >
      <div>
        {/* Card Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <h4 style={{ fontSize: "0.95rem", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
                {title}
              </h4>
            </div>
            <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{subtitle}</span>
          </div>
          <span className={`badge badge-${tagColor}`}>{tag}</span>
        </div>

        {/* Metrics Row */}
        <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap", fontSize: "0.75rem" }}>
          <div style={{ background: "rgba(15, 23, 42, 0.5)", padding: "4px 8px", borderRadius: "6px", border: "1px solid var(--border)" }}>
            Latency: <strong style={{ color: "var(--success)" }}>{data.latency_ms}ms</strong>
          </div>
          <div style={{ background: "rgba(15, 23, 42, 0.5)", padding: "4px 8px", borderRadius: "6px", border: "1px solid var(--border)" }}>
            Cost: <strong style={{ color: "#38bdf8" }}>${(data.estimated_cost || 0).toFixed(4)}</strong>
          </div>
          <div style={{ background: "rgba(15, 23, 42, 0.5)", padding: "4px 8px", borderRadius: "6px", border: "1px solid var(--border)" }}>
            Words: <strong style={{ color: wordCountValid ? "var(--success)" : "var(--danger)" }}>{wordCount}w</strong>
          </div>
        </div>

        {/* Child Instruction Box */}
        <div style={{
          background: isTarget ? "rgba(99, 102, 241, 0.12)" : "rgba(15, 23, 42, 0.6)",
          borderLeft: isTarget ? "4px solid #818cf8" : "4px solid var(--border)",
          borderRadius: "0 8px 8px 0",
          padding: "1rem",
          marginBottom: "1rem"
        }}>
          <span style={{ fontSize: "0.7rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>
            Generated Instruction:
          </span>
          <p style={{ fontSize: "1.05rem", fontWeight: 700, color: "white", margin: "0.25rem 0 0" }}>
            "{data.instruction}"
          </p>
          {data.supportive_message && (
            <p style={{ fontSize: "0.78rem", color: "#a5b4fc", fontStyle: "italic", margin: "0.35rem 0 0" }}>
              ✨ {data.supportive_message}
            </p>
          )}
        </div>

        {/* Visual Cues & Format */}
        <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
          <div style={{ marginBottom: "0.25rem" }}>Format: <strong>{data.answer_format}</strong></div>
          <div>Cues: <strong>{(data.visual_cues || []).join(", ") || "None"}</strong></div>
        </div>
      </div>

      {/* Card Footer: Validation Status */}
      <div style={{ borderTop: "1px solid var(--border)", paddingTop: "0.75rem", marginTop: "0.75rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.78rem" }}>
          {isApproved ? (
            <>
              <CheckCircle2 size={15} style={{ color: "var(--success)" }} />
              <span style={{ color: "var(--success)", fontWeight: 600 }}>Validation Approved</span>
            </>
          ) : (
            <>
              <AlertTriangle size={15} style={{ color: "var(--danger)" }} />
              <span style={{ color: "var(--danger)", fontWeight: 600 }}>Rejected (Fallback Active)</span>
            </>
          )}
        </div>
        <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
          {data.model_name || data.provider}
        </span>
      </div>
    </div>
  );
}
