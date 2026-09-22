import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles, Play, RotateCcw, Volume2, CheckCircle2, AlertCircle,
  HelpCircle, ArrowRight, UserCheck, ShieldCheck, Heart, Eye,
  ChevronDown, ChevronUp, Layers, Check, Compass, Timer, Pause,
  FileCheck, ThumbsUp, AlertTriangle, RefreshCw, Award, BookOpen,
  MessageSquare, User
} from "lucide-react";
import {
  fetchActivities, fetchLearners, createActivitySession,
  createAttemptInstruction, recordAttemptResponse, confirmAttemptResponse,
  analyseAttempt, reviewAttempt, transitionAttempt, fetchChildSafeView,
  fetchActivitySessionHistory
} from "../services/api";
import ChildPreviewModal from "./ChildPreviewModal";

export default function GuidedPlayground({
  tasks: initialTasks, learners: initialLearners, selectedTask: propSelectedTask,
  setSelectedTask: setPropSelectedTask, selectedLearner: propSelectedLearner,
  setSelectedLearner: setPropSelectedLearner, generationMode, viewMode, onLearnerUpdated
}) {
  // Activity Categories & Filters
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [activitiesList, setActivitiesList] = useState(initialTasks || []);
  const [learnersList, setLearnersList] = useState(initialLearners || []);

  const [activeLearner, setActiveLearner] = useState(propSelectedLearner || null);
  const [activeTask, setActiveTask] = useState(propSelectedTask || null);

  // Active Session & Attempt State
  const [currentSession, setCurrentSession] = useState(null);
  const [currentAttempt, setCurrentAttempt] = useState(null);
  const [childViewData, setChildViewData] = useState(null);
  const [sessionHistory, setSessionHistory] = useState(null);

  // Response Form State
  const [manualTranscript, setManualTranscript] = useState("");
  const [selectedOption, setSelectedOption] = useState("");
  const [completionStatus, setCompletionStatus] = useState("completed");
  const [assistanceLevel, setAssistanceLevel] = useState("independent");
  const [adultNotes, setAdultNotes] = useState("");

  // Timer State
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const timerRef = useRef(null);

  // Review & Override State
  const [showAdultReview, setShowAdultReview] = useState(false);
  const [overrideConcept, setOverrideConcept] = useState("correct");
  const [overrideTargetSkill, setOverrideTargetSkill] = useState("correct");
  const [overrideRetry, setOverrideRetry] = useState(false);
  const [overrideReason, setOverrideReason] = useState("");

  // UI Modals & Views
  const [showChildModal, setShowChildModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionOutcome, setSessionOutcome] = useState(null); // 'success' | 'adult_support_required' | null
  const [profileUpdateResult, setProfileUpdateResult] = useState(null);

  // Timer logic
  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setTimerSeconds(s => s + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isTimerRunning]);

  // Sync props when App.jsx loads them
  useEffect(() => {
    if (initialTasks && initialTasks.length > 0) {
      setActivitiesList(initialTasks);
      setActiveTask(prev => prev || initialTasks[0]);
    }
  }, [initialTasks]);

  useEffect(() => {
    if (initialLearners && initialLearners.length > 0) {
      setLearnersList(initialLearners);
      setActiveLearner(prev => {
        if (!prev) return initialLearners[0];
        const match = initialLearners.find(l => l.id === prev.id || l.learner_code === prev.learner_code);
        return match || initialLearners[0];
      });
    }
  }, [initialLearners]);

  // Load activities and learners directly from backend with auto-retry
  useEffect(() => {
    let isMounted = true;
    let timer = null;

    async function loadData() {
      try {
        const [acts, lrns] = await Promise.all([fetchActivities(), fetchLearners()]);
        if (!isMounted) return;

        if (acts && acts.length > 0) {
          setActivitiesList(acts);
          setActiveTask(prev => prev || acts[0]);
        }
        if (lrns && lrns.length > 0) {
          setLearnersList(lrns);
          setActiveLearner(prev => prev || lrns[0]);
        }
      } catch (err) {
        console.warn("Backend still starting or loading error in GuidedPlayground, retrying in 2.5s:", err);
        if (isMounted) {
          timer = setTimeout(loadData, 2500);
        }
      }
    }

    loadData();

    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
    };
  }, []);

  // Filter activities by category
  const filteredActivities = activitiesList.filter(act => {
    if (selectedCategory === "all") return true;
    return act.category === selectedCategory;
  });

  // Step 1: Start Activity Session
  const handleStartActivity = async () => {
    if (!activeLearner || !activeTask) {
      setError("Please select both a learner profile and an activity.");
      return;
    }
    setLoading(true);
    setError(null);
    setSessionOutcome(null);
    setProfileUpdateResult(null);
    setManualTranscript("");
    setSelectedOption("");
    setCompletionStatus("completed");
    setAssistanceLevel("independent");
    setAdultNotes("");
    setTimerSeconds(0);
    setIsTimerRunning(true);
    setShowAdultReview(false);

    try {
      // 1. Create Activity Session
      const session = await createActivitySession(activeLearner.id, activeTask.id, generationMode);

      // 2. Generate and store exact instruction in Attempt 1 BEFORE child sees it
      const attemptData = await createAttemptInstruction(session.id, generationMode);
      setCurrentSession(session);
      setCurrentAttempt(attemptData.attempt);
      setChildViewData(attemptData.child_view);

      // Refresh session history
      const hist = await fetchActivitySessionHistory(session.id);
      setSessionHistory(hist);
    } catch (err) {
      setError(err.message || "Failed to start learning activity.");
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Record Response
  const handleSaveResponse = async () => {
    if (!currentAttempt) return;
    setLoading(true);
    setError(null);
    setIsTimerRunning(false);

    try {
      const updated = await recordAttemptResponse(currentAttempt.id, {
        response_source: "adult_transcribed",
        manual_transcript: manualTranscript || (selectedOption ? String(selectedOption) : ""),
        selected_option: selectedOption || null,
        response_time_ms: timerSeconds * 1000,
        completion_status: completionStatus,
        assistance_level: assistanceLevel,
        adult_notes: adultNotes
      });
      setCurrentAttempt(updated);
    } catch (err) {
      setError(err.message || "Failed to save response.");
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Confirm Transcript
  const handleConfirmResponse = async () => {
    if (!currentAttempt) return;
    setLoading(true);
    setError(null);

    try {
      const confirmed = await confirmAttemptResponse(currentAttempt.id, true, manualTranscript);
      setCurrentAttempt(confirmed);

      // Automatically trigger analysis on confirmation
      const analRes = await analyseAttempt(currentAttempt.id);
      const hist = await fetchActivitySessionHistory(currentSession.id);
      setSessionHistory(hist);
      const latest = hist.attempts.find(a => a.id === currentAttempt.id);
      if (latest) setCurrentAttempt(latest);
    } catch (err) {
      setError(err.message || "Failed to confirm and analyse response.");
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Adult Override Review
  const handleSubmitReview = async () => {
    if (!currentAttempt) return;
    setLoading(true);
    setError(null);

    try {
      const reviewed = await reviewAttempt(currentAttempt.id, {
        final_concept_result: overrideConcept,
        final_target_skill_result: overrideTargetSkill,
        final_retry_required: overrideRetry,
        override_reason: overrideReason,
        reviewed_by_user_id: "authorized_adult",
        adult_notes: adultNotes
      });
      setCurrentAttempt(reviewed);
      setShowAdultReview(false);
    } catch (err) {
      setError(err.message || "Failed to save adult review.");
    } finally {
      setLoading(false);
    }
  };

  // Step 5: Transition to Next Step or Complete
  const handleProceedNext = async () => {
    if (!currentAttempt) return;
    setLoading(true);
    setError(null);

    try {
      const transRes = await transitionAttempt(currentAttempt.id);
      const hist = await fetchActivitySessionHistory(currentSession.id);
      setSessionHistory(hist);

      if (transRes.profile_update) {
        setProfileUpdateResult(transRes.profile_update);
        try {
          const freshLearners = await fetchLearners();
          if (freshLearners && freshLearners.length > 0) {
            setLearnersList(freshLearners);
            const updatedActive = freshLearners.find(l => l.id === activeLearner?.id || l.learner_code === activeLearner?.learner_code);
            if (updatedActive) {
              setActiveLearner(updatedActive);
              if (setPropSelectedLearner) setPropSelectedLearner(updatedActive);
            }
          }
          if (onLearnerUpdated) {
            await onLearnerUpdated();
          }
        } catch (lErr) {
          console.warn("Failed to refresh learners after profile update:", lErr);
        }
      }

      if (transRes.session_status === "completed" || transRes.session_status === "completed_with_adult_support") {
        setSessionOutcome("success");
      } else if (transRes.session_status === "adult_support_required") {
        setSessionOutcome("adult_support_required");
      } else if (transRes.next_action && transRes.next_action.startsWith("create_attempt")) {
        // Automatically create next attempt instruction
        const nextAtt = await createAttemptInstruction(currentSession.id, generationMode);
        setCurrentAttempt(nextAtt.attempt);
        setChildViewData(nextAtt.child_view);
        setManualTranscript("");
        setSelectedOption("");
        setTimerSeconds(0);
        setIsTimerRunning(true);
      }
    } catch (err) {
      setError(err.message || "Failed to transition attempt.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="guided-playground-container" style={{ maxWidth: "1200px", margin: "0 auto", padding: "1.5rem" }}>
      {/* Top Header */}
      <div style={{
        background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        borderRadius: "20px",
        padding: "1.75rem 2rem",
        color: "#ffffff",
        marginBottom: "2rem",
        boxShadow: "0 10px 25px -5px rgba(0,0,0,0.2)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "1rem"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
            <Sparkles color="#f97316" size={24} />
            <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800 }}>
              Manual-Input Adaptive Learning Runner
            </h1>
          </div>
          <p style={{ margin: 0, color: "#94a3b8", fontSize: "0.95rem" }}>
            Supervised English educational session with separate concept vs. target skill evaluation and progressive scaffolding.
          </p>
        </div>

        {currentAttempt && (
          <button
            onClick={() => setShowChildModal(true)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              background: "#f97316",
              color: "#ffffff",
              border: "none",
              padding: "0.75rem 1.5rem",
              borderRadius: "12px",
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: "0 4px 14px rgba(249, 115, 22, 0.4)"
            }}
          >
            <Eye size={20} />
            <span>Open Child Preview</span>
          </button>
        )}
      </div>

      {error && (
        <div style={{
          background: "#fef2f2",
          border: "1px solid #fecaca",
          color: "#b91c1c",
          padding: "1rem",
          borderRadius: "12px",
          marginBottom: "1.5rem",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem"
        }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Grid: Selection & Active Session */}
      <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: "1.5rem", alignItems: "start" }}>
        {/* Left Column: Learner Profile & Activity Catalog */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Learner Profile Selector */}
          <div className="card" style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "16px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "#1e293b" }}>
              <User size={18} color="#f97316" />
              <span>Learner Profile</span>
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {learnersList.map(lrn => {
                const isSelected = activeLearner?.id === lrn.id || activeLearner?.learner_code === lrn.learner_code;
                const riskColor = lrn.risk_support_level === "high" ? "#ef4444" : (lrn.risk_support_level === "moderate" ? "#f59e0b" : "#10b981");
                return (
                  <button
                    key={lrn.id || lrn.learner_code}
                    onClick={() => {
                      setActiveLearner(lrn);
                      if (setPropSelectedLearner) setPropSelectedLearner(lrn);
                    }}
                    disabled={!!currentSession && currentSession.status === "active"}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "0.75rem 1rem",
                      background: isSelected ? "#fff7ed" : "#f8fafc",
                      border: isSelected ? "2px solid #f97316" : "1px solid #e2e8f0",
                      borderRadius: "12px",
                      cursor: currentSession?.status === "active" ? "not-allowed" : "pointer",
                      textAlign: "left"
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700, color: "#1e293b" }}>{lrn.learner_code} (Age {lrn.age})</div>
                      <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                        Vocab: {lrn.vocabulary_score} | Gram: {lrn.grammar_score} | Comp: {lrn.comprehension_score}
                      </div>
                    </div>
                    <span style={{
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      padding: "0.2rem 0.6rem",
                      borderRadius: "9999px",
                      background: `${riskColor}15`,
                      color: riskColor
                    }}>
                      {lrn.risk_support_level}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Activity Category Browser */}
          <div className="card" style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "16px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "#1e293b" }}>
              <BookOpen size={18} color="#f97316" />
              <span>Activity Categories</span>
            </h3>

            {/* Category Pills */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "1rem" }}>
              {[
                { id: "all", label: "All (30)" },
                { id: "vocabulary", label: "Vocabulary" },
                { id: "grammar", label: "Grammar" },
                { id: "sentence_and_instruction", label: "Instructions" },
                { id: "comprehension", label: "Comprehension" }
              ].map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  style={{
                    padding: "0.35rem 0.75rem",
                    borderRadius: "8px",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    border: "none",
                    cursor: "pointer",
                    background: selectedCategory === cat.id ? "#f97316" : "#f1f5f9",
                    color: selectedCategory === cat.id ? "#ffffff" : "#475569"
                  }}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Activity List */}
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "320px", overflowY: "auto" }}>
              {filteredActivities.map(act => {
                const isSelected = activeTask?.id === act.id || activeTask?.task_code === act.task_code;
                return (
                  <button
                    key={act.id || act.task_code}
                    onClick={() => {
                      setActiveTask(act);
                      if (setPropSelectedTask) setPropSelectedTask(act);
                    }}
                    disabled={!!currentSession && currentSession.status === "active"}
                    style={{
                      padding: "0.6rem 0.8rem",
                      background: isSelected ? "#fff7ed" : "#ffffff",
                      border: isSelected ? "2px solid #f97316" : "1px solid #e2e8f0",
                      borderRadius: "10px",
                      cursor: currentSession?.status === "active" ? "not-allowed" : "pointer",
                      textAlign: "left"
                    }}
                  >
                    <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b" }}>{act.title}</div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      {act.task_code} • Ages {act.minimum_age}-{act.maximum_age}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Interactive Session Runner */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {!currentSession || !currentAttempt || sessionOutcome ? (
            /* Start New Activity Card */
            <div className="card" style={{
              background: "#ffffff",
              padding: "2rem",
              borderRadius: "20px",
              border: "1px solid #e2e8f0",
              boxShadow: "0 4px 12px rgba(0,0,0,0.03)",
              textAlign: "center"
            }}>
              {sessionOutcome === "success" ? (
                <div style={{ padding: "1.5rem 0" }}>
                  <Award size={64} color="#10b981" style={{ margin: "0 auto 1rem auto" }} />
                  <h2 style={{ color: "#065f46", margin: "0 0 0.5rem 0" }}>Activity Successfully Completed!</h2>
                  <p style={{ color: "#047857", maxWidth: "500px", margin: "0 auto 1.5rem auto" }}>
                    The child demonstrated target skill mastery across the structured adaptation workflow.
                  </p>
                </div>
              ) : sessionOutcome === "adult_support_required" ? (
                <div style={{
                  padding: "1.5rem",
                  background: "#fffbeb",
                  borderRadius: "16px",
                  border: "2px solid #fde68a",
                  marginBottom: "1.5rem"
                }}>
                  <AlertTriangle size={56} color="#d97706" style={{ margin: "0 auto 1rem auto" }} />
                  <h2 style={{ color: "#92400e", margin: "0 0 0.5rem 0" }}>Adult Support Required & Session Summary</h2>
                  <p style={{ color: "#b45309", maxWidth: "540px", margin: "0 auto" }}>
                    Three instructional attempts were completed without demonstrating independent target skill mastery.
                    Please review the stored session history and provide direct human educational scaffolding.
                  </p>
                </div>
              ) : null}

              {profileUpdateResult && (
                <div style={{
                  background: "#f0fdf4",
                  border: "2px solid #86efac",
                  borderRadius: "16px",
                  padding: "1.5rem",
                  marginBottom: "1.5rem",
                  textAlign: "left"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                      <div style={{
                        width: "36px",
                        height: "36px",
                        borderRadius: "50%",
                        background: "#dcfce7",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#15803d"
                      }}>
                        <RefreshCw size={20} />
                      </div>
                      <div>
                        <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 800, color: "#14532d" }}>
                          Learner Profile Dynamic Recalibration
                        </h3>
                        <div style={{ fontSize: "0.8rem", color: "#166534" }}>
                          Skill parameters updated for <strong>{profileUpdateResult.learner_code}</strong> based on performance
                        </div>
                      </div>
                    </div>

                    {profileUpdateResult.risk_changed ? (
                      <span style={{
                        background: "#fee2e2",
                        color: "#b91c1c",
                        border: "1px solid #f87171",
                        padding: "0.3rem 0.8rem",
                        borderRadius: "9999px",
                        fontSize: "0.8rem",
                        fontWeight: 800,
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.4rem"
                      }}>
                        <AlertTriangle size={14} /> Risk Level Shifted: {profileUpdateResult.before.risk_support_level} → {profileUpdateResult.after.risk_support_level}
                      </span>
                    ) : (
                      <span style={{
                        background: "#dcfce7",
                        color: "#15803d",
                        border: "1px solid #86efac",
                        padding: "0.3rem 0.8rem",
                        borderRadius: "9999px",
                        fontSize: "0.8rem",
                        fontWeight: 700
                      }}>
                        Support Tier: {profileUpdateResult.after.risk_support_level.toUpperCase()} (Maintained)
                      </span>
                    )}
                  </div>

                  {/* Metric Deltas Grid */}
                  <div style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
                    gap: "0.75rem",
                    marginBottom: "1rem"
                  }}>
                    {[
                      { label: "Vocabulary", before: profileUpdateResult.before.vocabulary_score, after: profileUpdateResult.after.vocabulary_score, delta: profileUpdateResult.deltas.vocabulary },
                      { label: "Grammar", before: profileUpdateResult.before.grammar_score, after: profileUpdateResult.after.grammar_score, delta: profileUpdateResult.deltas.grammar },
                      { label: "Comprehension", before: profileUpdateResult.before.comprehension_score, after: profileUpdateResult.after.comprehension_score, delta: profileUpdateResult.deltas.comprehension },
                      { label: "Instruction", before: profileUpdateResult.before.instruction_following_score, after: profileUpdateResult.after.instruction_following_score, delta: profileUpdateResult.deltas.instruction },
                    ].map(metric => {
                      const isPos = metric.delta > 0;
                      const isNeg = metric.delta < 0;
                      const deltaColor = isPos ? "#15803d" : (isNeg ? "#b91c1c" : "#64748b");
                      const deltaBg = isPos ? "#dcfce7" : (isNeg ? "#fee2e2" : "#f1f5f9");

                      return (
                        <div key={metric.label} style={{
                          background: "#ffffff",
                          padding: "0.8rem",
                          borderRadius: "12px",
                          border: "1px solid #e2e8f0"
                        }}>
                          <div style={{ fontSize: "0.72rem", color: "#64748b", fontWeight: 700, marginBottom: "0.25rem" }}>
                            {metric.label.toUpperCase()}
                          </div>
                          <div style={{ display: "flex", alignItems: "baseline", gap: "0.4rem", marginBottom: "0.25rem" }}>
                            <span style={{ fontSize: "1.15rem", fontWeight: 800, color: "#1e293b" }}>
                              {metric.after}
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "#94a3b8", textDecoration: "line-through" }}>
                              {metric.before}
                            </span>
                          </div>
                          <span style={{
                            fontSize: "0.75rem",
                            fontWeight: 800,
                            padding: "0.15rem 0.5rem",
                            borderRadius: "6px",
                            background: deltaBg,
                            color: deltaColor,
                            display: "inline-block"
                          }}>
                            {isPos ? `+${metric.delta}` : metric.delta} pts
                          </span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Composite and Reason Summary */}
                  <div style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    background: "#ffffff",
                    padding: "0.6rem 1rem",
                    borderRadius: "10px",
                    fontSize: "0.82rem",
                    color: "#334155",
                    border: "1px solid #e2e8f0",
                    flexWrap: "wrap",
                    gap: "0.5rem"
                  }}>
                    <span>
                      Composite Index (CLI): <strong>{profileUpdateResult.after.composite_language_index}/100</strong>
                      &nbsp;&bull;&nbsp;English Level: <strong style={{ textTransform: "capitalize" }}>{profileUpdateResult.after.english_level}</strong>
                    </span>
                    <span style={{ color: "#64748b", fontSize: "0.78rem" }}>
                      {profileUpdateResult.reason}
                    </span>
                  </div>
                </div>
              )}

              <div style={{
                background: "#f8fafc",
                borderRadius: "16px",
                padding: "1.5rem",
                marginBottom: "1.5rem",
                textAlign: "left",
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "1rem"
              }}>
                <div>
                  <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 700 }}>SELECTED LEARNER</span>
                  <div style={{ fontWeight: 800, fontSize: "1.1rem", color: "#1e293b" }}>
                    {activeLearner?.learner_code} (Age {activeLearner?.age})
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#475569" }}>
                    Risk Level: <strong>{activeLearner?.risk_support_level}</strong>
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 700 }}>SELECTED ACTIVITY</span>
                  <div style={{ fontWeight: 800, fontSize: "1.1rem", color: "#1e293b" }}>
                    {activeTask?.title}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#475569" }}>
                    Skill: <strong>{activeTask?.target_skill || activeTask?.subskill}</strong>
                  </div>
                </div>
              </div>

              <button
                onClick={handleStartActivity}
                disabled={loading || !activeLearner || !activeTask}
                style={{
                  background: "#f97316",
                  color: "#ffffff",
                  border: "none",
                  padding: "1rem 2.5rem",
                  borderRadius: "14px",
                  fontSize: "1.15rem",
                  fontWeight: 800,
                  cursor: loading ? "not-allowed" : "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.75rem",
                  boxShadow: "0 4px 14px rgba(249, 115, 22, 0.4)"
                }}
              >
                <Play size={22} fill="#ffffff" />
                <span>{loading ? "Starting..." : "Start Learning Session"}</span>
              </button>
            </div>
          ) : (
            /* Active Attempt Workspace */
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              {/* Step Banner & Scaffolding Strategy */}
              <div className="card" style={{
                background: "#ffffff",
                padding: "1.5rem",
                borderRadius: "20px",
                border: "2px solid #fed7aa",
                boxShadow: "0 4px 16px rgba(249, 115, 22, 0.08)"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <span style={{
                      background: "#f97316",
                      color: "#ffffff",
                      padding: "0.3rem 0.8rem",
                      borderRadius: "9999px",
                      fontWeight: 800,
                      fontSize: "0.85rem"
                    }}>
                      Attempt {currentAttempt?.attempt_number ?? 1} of 3
                    </span>
                    <span style={{
                      background: "#fff7ed",
                      color: "#c2410c",
                      padding: "0.3rem 0.8rem",
                      borderRadius: "9999px",
                      fontWeight: 700,
                      fontSize: "0.85rem",
                      border: "1px solid #fed7aa"
                    }}>
                      Support: {currentAttempt?.support_level || "mild"} ({currentAttempt?.adaptation_strategy || "default"})
                    </span>
                  </div>

                  {/* Timer Widget */}
                  <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    background: "#f1f5f9",
                    padding: "0.4rem 0.8rem",
                    borderRadius: "10px",
                    fontWeight: 700,
                    color: "#334155"
                  }}>
                    <Timer size={18} color="#f97316" />
                    <span>{timerSeconds}s</span>
                    <button
                      onClick={() => setIsTimerRunning(!isTimerRunning)}
                      style={{ background: "none", border: "none", cursor: "pointer", padding: "0 0.2rem" }}
                      title={isTimerRunning ? "Pause Timer" : "Start Timer"}
                    >
                      {isTimerRunning ? <Pause size={16} /> : <Play size={16} />}
                    </button>
                    <button
                      onClick={() => setTimerSeconds(0)}
                      style={{ background: "none", border: "none", cursor: "pointer", padding: "0 0.2rem" }}
                      title="Reset Timer"
                    >
                      <RotateCcw size={16} />
                    </button>
                  </div>
                </div>

                {/* Presented Child Instruction Card */}
                <div style={{
                  background: "#fffbeb",
                  borderRadius: "14px",
                  padding: "1.25rem",
                  border: "1px solid #fef3c7",
                  marginBottom: "1rem"
                }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#b45309", marginBottom: "0.25rem" }}>
                    INSTRUCTION PRESENTED TO CHILD:
                  </div>
                  <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#1e293b" }}>
                    "{currentAttempt?.presented_instruction || activeTask?.child_friendly_instruction || "Look at the picture and let's have fun!"}"
                  </div>
                </div>

                {/* Quick Child View Embed */}
                {childViewData && (
                  <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                    <button
                      onClick={() => setShowChildModal(true)}
                      style={{
                        background: "#fff7ed",
                        color: "#ea580c",
                        border: "1px solid #fed7aa",
                        padding: "0.5rem 1rem",
                        borderRadius: "10px",
                        fontWeight: 700,
                        fontSize: "0.85rem",
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.4rem"
                      }}
                    >
                      <Eye size={16} />
                      <span>Preview Child Modal View</span>
                    </button>
                    <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                      Target Skill: <strong>{currentAttempt?.target_skill || activeTask?.target_skill}</strong>
                    </span>
                  </div>
                )}
              </div>

              {/* Adult Response Form Card */}
              <div className="card" style={{
                background: "#ffffff",
                padding: "1.5rem",
                borderRadius: "20px",
                border: "1px solid #e2e8f0"
              }}>
                <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.15rem", fontWeight: 800, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <MessageSquare size={20} color="#f97316" />
                  <span>Adult Response Observation Form</span>
                </h3>

                {/* Manual Transcript Input */}
                <div style={{ marginBottom: "1.25rem" }}>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                    Child Spoken Transcript (Enter exact speech verbatim):
                  </label>
                  <textarea
                    rows={3}
                    value={manualTranscript}
                    onChange={e => setManualTranscript(e.target.value)}
                    placeholder="e.g. Fish live water."
                    style={{
                      width: "100%",
                      padding: "0.75rem",
                      borderRadius: "10px",
                      border: "1px solid #cbd5e1",
                      fontSize: "1rem",
                      fontFamily: "inherit",
                      resize: "vertical"
                    }}
                  />
                </div>

                {/* Multiple Choice Options (If task has options) */}
                {activeTask?.options && activeTask.options.length > 0 && (
                  <div style={{ marginBottom: "1.25rem" }}>
                    <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                      Selected Option (If multiple choice / picture selection):
                    </label>
                    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                      {activeTask.options.map((opt, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => {
                            setSelectedOption(opt);
                            if (!manualTranscript) setManualTranscript(opt);
                          }}
                          style={{
                            padding: "0.5rem 1rem",
                            borderRadius: "8px",
                            fontWeight: 700,
                            fontSize: "0.9rem",
                            border: selectedOption === opt ? "2px solid #f97316" : "1px solid #cbd5e1",
                            background: selectedOption === opt ? "#fff7ed" : "#f8fafc",
                            color: selectedOption === opt ? "#c2410c" : "#334155",
                            cursor: "pointer"
                          }}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Completion Status & Assistance Level */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.25rem" }}>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                      Completion Status:
                    </label>
                    <select
                      value={completionStatus}
                      onChange={e => setCompletionStatus(e.target.value)}
                      style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                    >
                      <option value="completed">Completed Answer</option>
                      <option value="no_response">No Response Provided</option>
                      <option value="asked_for_help">Child Asked for Help</option>
                      <option value="skipped">Skipped</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                      Assistance Level:
                    </label>
                    <select
                      value={assistanceLevel}
                      onChange={e => setAssistanceLevel(e.target.value)}
                      style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                    >
                      <option value="independent">Independent</option>
                      <option value="prompted">Prompted / Cue Given</option>
                      <option value="visually_supported">Visually Supported</option>
                      <option value="modelled">Adult Modelled Answer</option>
                      <option value="fully_assisted">Fully Assisted</option>
                    </select>
                  </div>
                </div>

                {/* Adult Notes */}
                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                    Adult Notes & Observations (Optional):
                  </label>
                  <input
                    type="text"
                    value={adultNotes}
                    onChange={e => setAdultNotes(e.target.value)}
                    placeholder="e.g. Child understood location conceptually but omitted preposition 'in'."
                    style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                  />
                </div>

                {/* Action Buttons */}
                <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
                  <button
                    onClick={handleSaveResponse}
                    disabled={loading}
                    style={{
                      background: "#f1f5f9",
                      color: "#334155",
                      border: "1px solid #cbd5e1",
                      padding: "0.65rem 1.25rem",
                      borderRadius: "10px",
                      fontWeight: 700,
                      cursor: "pointer"
                    }}
                  >
                    1. Save Response
                  </button>

                  <button
                    onClick={handleConfirmResponse}
                    disabled={loading || !manualTranscript}
                    style={{
                      background: currentAttempt?.adult_confirmed ? "#10b981" : "#f97316",
                      color: "#ffffff",
                      border: "none",
                      padding: "0.65rem 1.5rem",
                      borderRadius: "10px",
                      fontWeight: 700,
                      cursor: loading || !manualTranscript ? "not-allowed" : "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.4rem",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                    }}
                  >
                    <CheckCircle2 size={18} />
                    <span>{currentAttempt?.adult_confirmed ? "Confirmed & Analysed" : "2. Confirm Transcript & Analyse"}</span>
                  </button>
                </div>
              </div>

              {/* Analysis Result Breakdown */}
              {(currentAttempt?.attempt_status === "analysed" || (currentAttempt?.concept_result && currentAttempt?.concept_result !== "unclear")) ? (
                <div className="card" style={{
                  background: "#ffffff",
                  padding: "1.5rem",
                  borderRadius: "20px",
                  border: "1px solid #e2e8f0"
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                    <h3 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 800, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <FileCheck size={20} color="#10b981" />
                      <span>Separated Analysis Breakdown</span>
                    </h3>

                    <button
                      onClick={() => setShowAdultReview(!showAdultReview)}
                      style={{
                        background: "#f8fafc",
                        border: "1px solid #cbd5e1",
                        padding: "0.4rem 0.8rem",
                        borderRadius: "8px",
                        fontSize: "0.8rem",
                        fontWeight: 700,
                        color: "#475569",
                        cursor: "pointer"
                      }}
                    >
                      {showAdultReview ? "Close Review Override" : "Adult Review / Override"}
                    </button>
                  </div>

                  {/* Results Grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                    <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b" }}>CONCEPT RESULT</div>
                      <div style={{
                        fontSize: "1.2rem",
                        fontWeight: 800,
                        color: currentAttempt?.concept_result === "correct" ? "#10b981" : "#ef4444"
                      }}>
                        {currentAttempt?.final_concept_result || currentAttempt?.concept_result}
                      </div>
                    </div>

                    <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b" }}>TARGET SKILL RESULT</div>
                      <div style={{
                        fontSize: "1.2rem",
                        fontWeight: 800,
                        color: (currentAttempt?.final_target_skill_result || currentAttempt?.target_skill_result) === "correct" ? "#10b981" : "#ef4444"
                      }}>
                        {currentAttempt?.final_target_skill_result || currentAttempt?.target_skill_result}
                      </div>
                    </div>

                    <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b" }}>NEXT ACTION</div>
                      <div style={{ fontSize: "1.1rem", fontWeight: 800, color: (currentAttempt?.final_retry_required ?? currentAttempt?.retry_required) ? "#f59e0b" : "#10b981" }}>
                        {(currentAttempt?.final_retry_required ?? currentAttempt?.retry_required) ? "Retry Required" : "Target Achieved"}
                      </div>
                    </div>
                  </div>

                  {/* Observations */}
                  {currentAttempt?.grammar_observations && currentAttempt.grammar_observations.length > 0 && (
                    <div style={{ marginBottom: "1rem" }}>
                      <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#64748b" }}>OBSERVED GRAMMAR PATTERNS:</span>
                      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
                        {currentAttempt.grammar_observations.map((obs, idx) => (
                          <span key={idx} style={{ background: "#fef3c7", color: "#92400e", padding: "0.2rem 0.6rem", borderRadius: "6px", fontSize: "0.8rem", fontWeight: 700 }}>
                            {obs}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Adult Override Panel */}
                  {showAdultReview && (
                    <div style={{
                      background: "#f0fdf4",
                      border: "1px solid #bbf7d0",
                      borderRadius: "14px",
                      padding: "1.25rem",
                      marginBottom: "1rem"
                    }}>
                      <h4 style={{ margin: "0 0 0.75rem 0", color: "#166534" }}>Adult Override Decision</h4>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem", marginBottom: "0.75rem" }}>
                        <div>
                          <label style={{ fontSize: "0.75rem", fontWeight: 700 }}>Concept Result:</label>
                          <select value={overrideConcept} onChange={e => setOverrideConcept(e.target.value)} style={{ width: "100%", padding: "0.4rem" }}>
                            <option value="correct">Correct</option>
                            <option value="partial">Partial</option>
                            <option value="incorrect">Incorrect</option>
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: "0.75rem", fontWeight: 700 }}>Target Skill Result:</label>
                          <select value={overrideTargetSkill} onChange={e => setOverrideTargetSkill(e.target.value)} style={{ width: "100%", padding: "0.4rem" }}>
                            <option value="correct">Correct</option>
                            <option value="incorrect">Incorrect</option>
                            <option value="not_applicable">Not Applicable</option>
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: "0.75rem", fontWeight: 700 }}>Retry Required:</label>
                          <select value={overrideRetry ? "yes" : "no"} onChange={e => setOverrideRetry(e.target.value === "yes")} style={{ width: "100%", padding: "0.4rem" }}>
                            <option value="no">No (Target Achieved)</option>
                            <option value="yes">Yes (Retry Required)</option>
                          </select>
                        </div>
                      </div>

                      <input
                        type="text"
                        placeholder="Reason for adult override (recorded in audit history)..."
                        value={overrideReason}
                        onChange={e => setOverrideReason(e.target.value)}
                        style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #86efac", marginBottom: "0.75rem" }}
                      />

                      <button
                        onClick={handleSubmitReview}
                        style={{ background: "#16a34a", color: "#ffffff", border: "none", padding: "0.5rem 1rem", borderRadius: "8px", fontWeight: 700, cursor: "pointer" }}
                      >
                        Apply Override
                      </button>
                    </div>
                  )}

                  {/* Proceed / Advance Button */}
                  <button
                    onClick={handleProceedNext}
                    disabled={loading}
                    style={{
                      background: "#1e293b",
                      color: "#ffffff",
                      border: "none",
                      padding: "0.75rem 2rem",
                      borderRadius: "12px",
                      fontWeight: 800,
                      fontSize: "1rem",
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.5rem"
                    }}
                  >
                    <span>Proceed / Advance Session</span>
                    <ArrowRight size={18} />
                  </button>
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>

      {/* Child Safe Modal */}
      {showChildModal && (
        <ChildPreviewModal
          childView={childViewData}
          adaptation={currentAttempt}
          task={activeTask}
          onClose={() => setShowChildModal(false)}
        />
      )}
    </div>
  );
}
