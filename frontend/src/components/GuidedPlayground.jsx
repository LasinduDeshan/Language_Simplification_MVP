import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles, Play, RotateCcw, Volume2, CheckCircle2, AlertCircle,
  HelpCircle, ArrowRight, UserCheck, ShieldCheck, Heart, Eye,
  ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Layers, Check, Compass, Timer, Pause,
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
import {
  useTranslation,
  localizeSkill,
  localizeSupport,
  localizeRisk,
  localizeStatus,
  getLocalizedInstruction,
  getLocalizedOptions,
  getLocalizedTaskTitle,
  resolveLocalizedInstruction,
  normalizeContentLocale
} from "../i18n";

function InstructionCard({
  attempt,
  activeTask,
  viewMode,
  resolvedLanguage,
  t
}) {
  const [displayedInstruction, setDisplayedInstruction] = useState("");
  const [lineageMeta, setLineageMeta] = useState(null);

  useEffect(() => {
    if (!attempt && !activeTask) return;
    const contentLocale = normalizeContentLocale(resolvedLanguage);
    const instructionResult = resolveLocalizedInstruction(
      attempt || activeTask,
      contentLocale,
      { viewMode, isChildView: viewMode === "simple", task: activeTask }
    );
    setDisplayedInstruction(instructionResult.text || "");
    setLineageMeta(attempt?.simplification_lineage || null);
  }, [
    attempt?.id,
    attempt?.attempt_number,
    attempt?.presented_instruction,
    attempt?.presented_instruction_si,
    attempt?.adaptation_strategy,
    resolvedLanguage,
    viewMode
  ]);

  const contentLocale = normalizeContentLocale(resolvedLanguage);
  const instructionResult = resolveLocalizedInstruction(
    attempt || activeTask,
    contentLocale,
    { viewMode, isChildView: viewMode === "simple", task: activeTask }
  );
  const textToShow = displayedInstruction || instructionResult.text;

  return (
    <div style={{
      background: "#fffbeb",
      borderRadius: "14px",
      padding: "1.25rem",
      border: "1px solid #fef3c7",
      marginBottom: "1rem"
    }}>
      <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#b45309", marginBottom: "0.25rem" }}>
        {t("instructionPresentedToChild")}
      </div>
      {viewMode === "researcher" && instructionResult.usedFallback && (
        <div className="translation-warning" role="status" style={{
          background: "rgba(245, 158, 11, 0.15)",
          color: "#b45309",
          padding: "0.4rem 0.75rem",
          borderRadius: "8px",
          fontSize: "0.82rem",
          fontWeight: 600,
          marginBottom: "0.5rem",
          border: "1px solid rgba(245, 158, 11, 0.3)"
        }}>
          {t("localization.sinhalaContentUnavailable")}
        </div>
      )}
      {viewMode === "simple" && instructionResult.missing && contentLocale === "si" ? (
        <div className="sinhala-unavailable-notice" role="status" style={{
          background: "#fef2f2",
          color: "#991b1b",
          border: "1px solid #fecaca",
          borderRadius: "10px",
          padding: "0.75rem 1rem",
          fontWeight: 700,
          fontSize: "1.05rem",
          textAlign: "center",
          marginBottom: "0.5rem"
        }}>
          {textToShow}
        </div>
      ) : (
        <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#1e293b", marginBottom: lineageMeta && viewMode === "researcher" ? "0.75rem" : "0" }}>
          "{textToShow}"
        </div>
      )}

      {/* Researcher View: Truthful Simplification Lineage Notice */}
      {viewMode === "researcher" && lineageMeta && (
        <div style={{
          background: "#ffffff",
          padding: "0.75rem 1rem",
          borderRadius: "10px",
          border: "1px solid #e2e8f0",
          fontSize: "0.8rem",
          color: "#334155",
          display: "flex",
          flexDirection: "column",
          gap: "0.35rem"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
            <span>
              <strong>Simplification Mode:</strong>{" "}
              {lineageMeta.generation_mode === "RULE_ENGINE" && (
                <span style={{ color: "#15803d", fontWeight: 700 }}>
                  Rule Engine ({lineageMeta.simplification_run_id}) | Rules: {lineageMeta.applied_rule_ids?.join(", ") || "SI-LEX-SUB-0001"}
                </span>
              )}
              {lineageMeta.generation_mode === "TEMPLATE_CATALOG" && (
                <span style={{ color: "#0369a1", fontWeight: 700 }}>
                  Governed Template Fallback ({lineageMeta.template_variant_id})
                </span>
              )}
              {lineageMeta.generation_mode === "UNCHANGED_REUSE" && (
                <span style={{ color: "#b45309", fontWeight: 700 }}>
                  Governed Unchanged Reuse
                </span>
              )}
            </span>
            <span style={{
              background: lineageMeta.independent_performance_measure ? "#dcfce7" : "#fef3c7",
              color: lineageMeta.independent_performance_measure ? "#15803d" : "#b45309",
              padding: "0.2rem 0.5rem",
              borderRadius: "6px",
              fontWeight: 700,
              fontSize: "0.75rem"
            }}>
              {lineageMeta.score_interpretation === "INDEPENDENT_BASELINE" ? "Independent Baseline" : "Supported Performance (Non-Independent)"}
            </span>
          </div>

          {lineageMeta.generation_mode === "UNCHANGED_REUSE" && (
            <div style={{ color: "#b45309", fontStyle: "italic", fontSize: "0.78rem" }}>
              Notice: No further safe simplification was available; previous validated instruction retained (Reason: {lineageMeta.reuse_reason_code || "Minimal safe instruction already reached"}).
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function getParticipantDisplayName(learner, lang, isResearcher = false) {
  if (!learner) return "";
  const isSi = lang?.startsWith("si");
  if (isSi) {
    if (learner.display_name) return learner.display_name;
    const num = (learner.display_code || learner.learner_code || "").replace(/\D+/g, "").padStart(2, "0") || "01";
    return `දරුවා ${num}`;
  }
  if (isResearcher) {
    return learner.display_code || learner.learner_code || "CHILD-001";
  }
  if (learner.display_code) {
    const num = learner.display_code.replace(/\D+/g, "").padStart(2, "0");
    return `Child ${num}`;
  }
  return learner.learner_code || "Child 01";
}

function getParticipantRiskInfo(learner, lang) {
  if (!learner) return { text: "", color: "#64748b", isDemonstration: false };
  const isDemo = learner.risk_source === "DEMONSTRATION_DATA" || learner.screening_source === "component_1" || !learner.risk_assessed_at;
  const rawRisk = learner.risk_level || learner.screening_risk_level || learner.risk_support_level;
  
  const text = localizeRisk(rawRisk, lang, isDemo);
  const r = String(rawRisk || "").toLowerCase();
  let color = "#64748b";
  if (r === "high" || r === "critical") color = "#ef4444";
  else if (r === "moderate") color = "#f59e0b";
  else if (r === "low") color = "#10b981";
  
  return { text, color, isDemonstration: isDemo };
}

export default function GuidedPlayground({
  tasks: initialTasks, learners: initialLearners, selectedTask: propSelectedTask,
  setSelectedTask: setPropSelectedTask, selectedLearner: propSelectedLearner,
  setSelectedLearner: setPropSelectedLearner, generationMode, viewMode, onLearnerUpdated
}) {
  const { t, resolvedLanguage } = useTranslation("playground");
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
  const requestSequenceRef = useRef(0);


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
  const handleStartActivityWithTask = async (taskToRun, learnerToRun) => {
    const targetTask = taskToRun || activeTask;
    const targetLearner = learnerToRun || activeLearner;
    if (!targetLearner || !targetTask) {
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
      const session = await createActivitySession(targetLearner.id, targetTask.id, generationMode);

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

  const handleStartActivity = () => handleStartActivityWithTask(activeTask, activeLearner);

  const handleSelectTask = async (act) => {
    setActiveTask(act);
    if (setPropSelectedTask) setPropSelectedTask(act);
    if (currentSession && currentSession.status === "active") {
      await handleStartActivityWithTask(act, activeLearner);
    }
  };

  const handleSelectLearner = async (lrn) => {
    setActiveLearner(lrn);
    if (setPropSelectedLearner) setPropSelectedLearner(lrn);
    if (currentSession && currentSession.status === "active") {
      await handleStartActivityWithTask(activeTask, lrn);
    }
  };

  const currentTaskIndex = activitiesList.findIndex(
    act => act.id === activeTask?.id || act.task_code === activeTask?.task_code
  );

  const handlePrevQuestion = async () => {
    if (currentTaskIndex > 0) {
      const prevTask = activitiesList[currentTaskIndex - 1];
      setActiveTask(prevTask);
      if (setPropSelectedTask) setPropSelectedTask(prevTask);
      await handleStartActivityWithTask(prevTask, activeLearner);
    }
  };

  const handleNextQuestion = async () => {
    if (currentTaskIndex < activitiesList.length - 1) {
      const nextTask = activitiesList[currentTaskIndex + 1];
      setActiveTask(nextTask);
      if (setPropSelectedTask) setPropSelectedTask(nextTask);
      await handleStartActivityWithTask(nextTask, activeLearner);
    }
  };

  const handleExitSession = () => {
    setCurrentSession(null);
    setCurrentAttempt(null);
    setChildViewData(null);
    setSessionHistory(null);
    setSessionOutcome(null);
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

      const reqId = ++requestSequenceRef.current;
      if (transRes.session_status === "completed" || transRes.session_status === "completed_with_adult_support") {
        setSessionOutcome("success");
      } else if (transRes.session_status === "adult_support_required") {
        setSessionOutcome("adult_support_required");
      } else if (transRes.next_action && transRes.next_action.startsWith("create_attempt")) {
        // Automatically create next attempt instruction
        const nextAtt = await createAttemptInstruction(currentSession.id, generationMode);
        if (reqId !== requestSequenceRef.current) return;
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
            <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 700, lineHeight: 1.4 }}>
              {t("headerTitle")}
            </h1>
          </div>
          <p style={{ margin: 0, color: "#94a3b8", fontSize: "0.95rem" }}>
            {t("headerSubtitle")}
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
            <span>{t("openChildPreview")}</span>
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
              <span>{t("learnerProfile")}</span>
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {learnersList.map(lrn => {
                const isSelected = activeLearner?.id === lrn.id || activeLearner?.learner_code === lrn.learner_code;
                const riskInfo = getParticipantRiskInfo(lrn, resolvedLanguage);
                const displayName = getParticipantDisplayName(lrn, resolvedLanguage, viewMode === "researcher");
                return (
                  <button
                    key={lrn.id || lrn.learner_code}
                    onClick={() => handleSelectLearner(lrn)}
                    title={viewMode !== "researcher" ? `${t("internalId") || "Internal ID"}: ${lrn.participant_id || lrn.id}` : undefined}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "stretch",
                      padding: "0.75rem 1rem",
                      background: isSelected ? "#fff7ed" : "#f8fafc",
                      border: isSelected ? "2px solid #f97316" : "1px solid #e2e8f0",
                      borderRadius: "12px",
                      cursor: "pointer",
                      textAlign: "left",
                      gap: "0.3rem"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ fontWeight: 700, color: "#1e293b", fontSize: "0.95rem" }}>
                        {displayName} ({t("ageLabel", { age: lrn.age_years ?? lrn.age })})
                      </div>
                      <span style={{
                        fontSize: "0.75rem",
                        fontWeight: 700,
                        padding: "0.2rem 0.6rem",
                        borderRadius: "9999px",
                        background: `${riskInfo.color}15`,
                        color: riskInfo.color
                      }}>
                        {riskInfo.text}
                      </span>
                    </div>

                    <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                      {t("metricVocabulary")}: {lrn.vocabulary_score} | {t("metricGrammar")}: {lrn.grammar_score} | {t("metricComprehension")}: {lrn.comprehension_score}
                    </div>

                    {viewMode === "researcher" && (
                      <div style={{
                        fontSize: "0.72rem",
                        color: "#475569",
                        marginTop: "0.25rem",
                        padding: "0.35rem 0.5rem",
                        background: "#e2e8f0",
                        borderRadius: "6px",
                        fontFamily: "monospace",
                        lineHeight: 1.4
                      }}>
                        <div><strong>{t("internalId") || "Internal ID"}:</strong> {lrn.participant_id || lrn.id}</div>
                        <div><strong>{t("riskSource") || "Risk Source"}:</strong> {lrn.risk_source || (lrn.screening_source === "component_1" ? "DEMONSTRATION_DATA" : "NOT_CONNECTED")}</div>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Activity Category Browser */}
          <div className="card" style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "16px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "#1e293b" }}>
              <BookOpen size={18} color="#f97316" />
              <span>{t("activityCatalog")}</span>
            </h3>

            {/* Category Pills */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "1rem" }}>
              {[
                { id: "all", label: t("categoryAll", { count: activitiesList.length || 30 }) },
                { id: "vocabulary", label: t("categoryVocabulary") },
                { id: "grammar", label: t("categoryGrammar") },
                { id: "sentence_and_instruction", label: t("categoryInstructions") },
                { id: "comprehension", label: t("categoryComprehension") }
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
                    onClick={() => handleSelectTask(act)}
                    style={{
                      padding: "0.6rem 0.8rem",
                      background: isSelected ? "#fff7ed" : "#ffffff",
                      border: isSelected ? "2px solid #f97316" : "1px solid #e2e8f0",
                      borderRadius: "10px",
                      cursor: "pointer",
                      textAlign: "left"
                    }}
                  >
                    <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b" }}>
                      {getLocalizedTaskTitle(act, resolvedLanguage)}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      {act.task_code} • {t("agesLabel", { min: act.minimum_age, max: act.maximum_age })}
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
                  <h2 style={{ color: "#065f46", margin: "0 0 0.5rem 0" }}>{t("sessionSuccess")}</h2>
                  <p style={{ color: "#047857", maxWidth: "500px", margin: "0 auto 1.5rem auto" }}>
                    {t("sessionSuccessDesc")}
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
                  <h2 style={{ color: "#92400e", margin: "0 0 0.5rem 0" }}>{t("sessionSupportRequired")}</h2>
                  <p style={{ color: "#b45309", maxWidth: "540px", margin: "0 auto" }}>
                    {t("sessionSupportRequiredDesc")}
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
                          {t("recalibrationTitle")}
                        </h3>
                        <div style={{ fontSize: "0.8rem", color: "#166534" }}>
                          {t("recalibrationNotice", { code: getParticipantDisplayName(profileUpdateResult, resolvedLanguage, viewMode === "researcher") || profileUpdateResult.learner_code })}
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
                        <AlertTriangle size={14} /> {t("riskShifted", {
                          before: localizeRisk(profileUpdateResult.before.risk_support_level),
                          after: localizeRisk(profileUpdateResult.after.risk_support_level)
                        })}
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
                        {t("supportTierMaintained", {
                          tier: localizeRisk(profileUpdateResult.after.risk_support_level)
                        })}
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
                      { label: t("metricVocabulary"), before: profileUpdateResult.before.vocabulary_score, after: profileUpdateResult.after.vocabulary_score, delta: profileUpdateResult.deltas.vocabulary },
                      { label: t("metricGrammar"), before: profileUpdateResult.before.grammar_score, after: profileUpdateResult.after.grammar_score, delta: profileUpdateResult.deltas.grammar },
                      { label: t("metricComprehension"), before: profileUpdateResult.before.comprehension_score, after: profileUpdateResult.after.comprehension_score, delta: profileUpdateResult.deltas.comprehension },
                      { label: t("metricInstruction"), before: profileUpdateResult.before.instruction_following_score, after: profileUpdateResult.after.instruction_following_score, delta: profileUpdateResult.deltas.instruction },
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
                      {t("compositeIndex")}: <strong>{profileUpdateResult.after.composite_language_index}/100</strong>
                      &nbsp;&bull;&nbsp;{t("englishLevel")}: <strong style={{ textTransform: "capitalize" }}>{profileUpdateResult.after.english_level}</strong>
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
                  <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 700 }}>{t("selectedLearner")}</span>
                  <div style={{ fontWeight: 800, fontSize: "1.1rem", color: "#1e293b" }}>
                    {getParticipantDisplayName(activeLearner, resolvedLanguage, viewMode === "researcher")} ({t("ageLabel", { age: activeLearner?.age_years ?? activeLearner?.age })})
                  </div>
                  {(() => {
                    const activeRiskInfo = getParticipantRiskInfo(activeLearner, resolvedLanguage);
                    return (
                      <>
                        <div style={{ fontSize: "0.85rem", color: "#475569", marginTop: "0.25rem" }}>
                          {t("riskLevel")}: <strong style={{ color: activeRiskInfo.color }}>{activeRiskInfo.text}</strong>
                        </div>
                        <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.2rem" }}>
                          {t("metricVocabulary")}: {activeLearner?.vocabulary_score} | {t("metricGrammar")}: {activeLearner?.grammar_score} | {t("metricComprehension")}: {activeLearner?.comprehension_score}
                        </div>
                        {viewMode === "researcher" && (
                          <div style={{
                            fontSize: "0.75rem",
                            color: "#475569",
                            marginTop: "0.4rem",
                            padding: "0.35rem 0.5rem",
                            background: "#e2e8f0",
                            borderRadius: "6px",
                            fontFamily: "monospace",
                            lineHeight: 1.4
                          }}>
                            <div><strong>{t("internalId") || "Internal ID"}:</strong> {activeLearner?.participant_id || activeLearner?.id}</div>
                            <div><strong>{t("riskSource") || "Risk Source"}:</strong> {activeLearner?.risk_source || (activeLearner?.screening_source === "component_1" ? "DEMONSTRATION_DATA" : "NOT_CONNECTED")}</div>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>

                <div>
                  <span style={{ fontSize: "0.8rem", color: "#64748b", fontWeight: 700 }}>{t("selectedActivity")}</span>
                  <div style={{ fontWeight: 800, fontSize: "1.1rem", color: "#1e293b" }}>
                    {getLocalizedTaskTitle(activeTask, resolvedLanguage)}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#475569" }}>
                    {t("skill")}: <strong>{localizeSkill(activeTask?.target_skill || activeTask?.subskill, resolvedLanguage)}</strong>
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
                <span>{loading ? t("starting") : t("startSession")}</span>
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
                {/* Question Navigation Toolbar */}
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  paddingBottom: "1rem",
                  marginBottom: "1rem",
                  borderBottom: "1px solid #fed7aa",
                  flexWrap: "wrap",
                  gap: "0.5rem"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                    <button
                      onClick={handlePrevQuestion}
                      disabled={currentTaskIndex <= 0 || loading}
                      title={t("prevQuestion")}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.25rem",
                        padding: "0.4rem 0.75rem",
                        borderRadius: "8px",
                        border: "1px solid #cbd5e1",
                        background: currentTaskIndex <= 0 ? "#f8fafc" : "#ffffff",
                        color: currentTaskIndex <= 0 ? "#94a3b8" : "#1e293b",
                        fontSize: "0.82rem",
                        fontWeight: 600,
                        cursor: currentTaskIndex <= 0 || loading ? "not-allowed" : "pointer",
                        transition: "all 0.15s ease"
                      }}
                    >
                      <ChevronLeft size={16} />
                      <span>{t("prevQuestion")}</span>
                    </button>

                    <span style={{
                      fontWeight: 700,
                      fontSize: "0.88rem",
                      color: "#334155",
                      padding: "0.3rem 0.6rem",
                      background: "#f1f5f9",
                      borderRadius: "6px"
                    }}>
                      {t("questionCounter", { current: currentTaskIndex >= 0 ? currentTaskIndex + 1 : 1, total: activitiesList.length || 10 })}
                      {" • "}
                      <span style={{ color: "#f97316" }}>{getLocalizedTaskTitle(activeTask, resolvedLanguage)}</span>
                    </span>

                    <button
                      onClick={handleNextQuestion}
                      disabled={currentTaskIndex >= activitiesList.length - 1 || loading}
                      title={t("nextQuestion")}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.25rem",
                        padding: "0.4rem 0.75rem",
                        borderRadius: "8px",
                        border: "1px solid #cbd5e1",
                        background: currentTaskIndex >= activitiesList.length - 1 ? "#f8fafc" : "#ffffff",
                        color: currentTaskIndex >= activitiesList.length - 1 ? "#94a3b8" : "#1e293b",
                        fontSize: "0.82rem",
                        fontWeight: 600,
                        cursor: currentTaskIndex >= activitiesList.length - 1 || loading ? "not-allowed" : "pointer",
                        transition: "all 0.15s ease"
                      }}
                    >
                      <span>{t("nextQuestion")}</span>
                      <ChevronRight size={16} />
                    </button>
                  </div>

                  <button
                    onClick={handleExitSession}
                    title={t("changeQuestion")}
                    style={{
                      background: "#f8fafc",
                      color: "#64748b",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                      padding: "0.4rem 0.75rem",
                      fontSize: "0.82rem",
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "0.35rem"
                    }}
                  >
                    <BookOpen size={15} />
                    <span>{t("changeQuestion")}</span>
                  </button>
                </div>

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
                      {t("attemptCounter", { current: currentAttempt?.attempt_number ?? 1, total: 3 })}
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
                      {viewMode === "researcher" ? (
                        <>
                          {t("supportLevel", { level: localizeSupport(currentAttempt?.support_level || "mild") })} ({localizeSupport(currentAttempt?.adaptation_strategy || "default")})
                        </>
                      ) : (
                        <>
                          {localizeSupport(currentAttempt?.adaptation_strategy || currentAttempt?.support_level || "strong_child_friendly")}
                        </>
                      )}
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
                      title={isTimerRunning ? t("pauseTimer") : t("startTimer")}
                    >
                      {isTimerRunning ? <Pause size={16} /> : <Play size={16} />}
                    </button>
                    <button
                      onClick={() => setTimerSeconds(0)}
                      style={{ background: "none", border: "none", cursor: "pointer", padding: "0 0.2rem" }}
                      title={t("resetTimer")}
                    >
                      <RotateCcw size={16} />
                    </button>
                  </div>
                </div>

                {/* Presented Child Instruction Card with Canonical Keying */}
                <InstructionCard
                  key={currentAttempt ? currentAttempt.id : "initial-task"}
                  attempt={currentAttempt}
                  activeTask={activeTask}
                  viewMode={viewMode}
                  resolvedLanguage={resolvedLanguage}
                  t={t}
                />


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
                      <span>{t("previewChildView")}</span>
                    </button>
                    <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                      {t("targetSkill")}: <strong>{localizeSkill(currentAttempt?.target_skill || activeTask?.target_skill, resolvedLanguage)}</strong>
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
                  <span>{t("adultObservationForm")}</span>
                </h3>

                {/* Manual Transcript Input */}
                <div style={{ marginBottom: "1.25rem" }}>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                    {t("childTranscript")}
                  </label>
                  <textarea
                    rows={3}
                    value={manualTranscript}
                    onChange={e => setManualTranscript(e.target.value)}
                    placeholder={t("transcriptPlaceholder")}
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

                {/* Multiple Choice Options or Word Tokens */}
                {((activeTask?.options && activeTask.options.length > 0) || (activeTask?.tokens && activeTask.tokens.length > 0)) && (
                  <div style={{ marginBottom: "1.25rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                      <label style={{ fontSize: "0.85rem", fontWeight: 700, color: "#334155" }}>
                        {activeTask?.tokens?.length > 0 ? (t("wordTokens") || "Word Tokens / පද මාලාව") : t("selectedOption")}
                      </label>
                      {manualTranscript && (
                        <button
                          type="button"
                          onClick={() => {
                            setManualTranscript("");
                            setSelectedOption("");
                          }}
                          style={{
                            fontSize: "0.75rem",
                            color: "#94a3b8",
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            textDecoration: "underline"
                          }}
                        >
                          {t("clear") || "Clear"}
                        </button>
                      )}
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                      {getLocalizedOptions(activeTask, resolvedLanguage).map((opt, i) => (
                        <button
                          key={i}
                          type="button"
                          onClick={() => {
                            setSelectedOption(opt.raw);
                            const isWordOrder = activeTask?.task_code === 'GRAM-WORD-001' || activeTask?.tokens?.length > 0 || String(activeTask?.target_skill?.code || activeTask?.target_skill || '').toLowerCase().includes('word');
                            if (isWordOrder) {
                              setManualTranscript(prev => (prev ? `${prev} ${opt.label}` : opt.label));
                            } else {
                              setManualTranscript(opt.label);
                            }
                          }}
                          style={{
                            padding: "0.5rem 1rem",
                            borderRadius: "8px",
                            fontWeight: 700,
                            fontSize: "0.95rem",
                            border: selectedOption === opt.raw ? "2px solid #f97316" : "1px solid #cbd5e1",
                            background: selectedOption === opt.raw ? "#fff7ed" : "#f8fafc",
                            color: selectedOption === opt.raw ? "#c2410c" : "#334155",
                            cursor: "pointer",
                            transition: "all 0.15s ease"
                          }}
                        >
                          {opt.emoji ? `${opt.emoji} ` : ""}{typeof opt.label === 'object' && opt.label !== null ? (opt.label.si || opt.label.en || "") : opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Completion Status & Assistance Level */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.25rem" }}>
                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                      {t("completionStatus")}
                    </label>
                    <select
                      value={completionStatus}
                      onChange={e => setCompletionStatus(e.target.value)}
                      style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                    >
                      <option value="completed">{t("status.completed")}</option>
                      <option value="no_response">{t("status.no_response")}</option>
                      <option value="asked_for_help">{t("status.asked_for_help")}</option>
                      <option value="skipped">{t("status.skipped")}</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                      {t("assistanceLevel")}
                    </label>
                    <select
                      value={assistanceLevel}
                      onChange={e => setAssistanceLevel(e.target.value)}
                      style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                    >
                      <option value="independent">{t("support.independent")}</option>
                      <option value="prompted">{t("support.prompted")}</option>
                      <option value="visually_supported">{t("support.visually_supported")}</option>
                      <option value="modelled">{t("support.modelled")}</option>
                      <option value="fully_assisted">{t("support.fully_assisted")}</option>
                    </select>
                  </div>
                </div>

                {/* Adult Notes */}
                <div style={{ marginBottom: "1.5rem" }}>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 700, color: "#334155", marginBottom: "0.4rem" }}>
                    {t("adultNotes")}
                  </label>
                  <input
                    type="text"
                    value={adultNotes}
                    onChange={e => setAdultNotes(e.target.value)}
                    placeholder={t("adultNotesPlaceholder")}
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
                    {t("saveResponse")}
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
                    <span>{currentAttempt?.adult_confirmed ? t("confirmedAndAnalysed") : t("confirmAndAnalyse")}</span>
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
                      <span>{t("analysisBreakdown")}</span>
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
                      {showAdultReview ? t("closeReview") : t("reviewOverride")}
                    </button>
                  </div>

                  {/* Results Grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                    <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b" }}>{t("conceptResult")}</div>
                      <div style={{
                        fontSize: "1.2rem",
                        fontWeight: 800,
                        color: currentAttempt?.concept_result === "correct" ? "#10b981" : "#ef4444"
                      }}>
                        {localizeStatus(currentAttempt?.final_concept_result || currentAttempt?.concept_result)}
                      </div>
                    </div>

                    <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b" }}>{t("targetSkillResult")}</div>
                      <div style={{
                        fontSize: "1.2rem",
                        fontWeight: 800,
                        color: (currentAttempt?.final_target_skill_result || currentAttempt?.target_skill_result) === "correct" ? "#10b981" : "#ef4444"
                      }}>
                        {localizeStatus(currentAttempt?.final_target_skill_result || currentAttempt?.target_skill_result)}
                      </div>
                    </div>

                    <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b" }}>{t("nextAction")}</div>
                      <div style={{ fontSize: "1.1rem", fontWeight: 800, color: (currentAttempt?.final_retry_required ?? currentAttempt?.retry_required) ? "#f59e0b" : "#10b981" }}>
                        {(currentAttempt?.final_retry_required ?? currentAttempt?.retry_required) ? t("retryRequired") : t("targetAchieved")}
                      </div>
                    </div>
                  </div>

                  {/* Observations */}
                  {currentAttempt?.grammar_observations && currentAttempt.grammar_observations.length > 0 && (
                    <div style={{ marginBottom: "1rem" }}>
                      <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#64748b" }}>{t("observedPatterns")}</span>
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
                      <h4 style={{ margin: "0 0 0.75rem 0", color: "#166534" }}>{t("adultOverrideTitle")}</h4>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem", marginBottom: "0.75rem" }}>
                        <div>
                          <label style={{ fontSize: "0.75rem", fontWeight: 700 }}>{t("conceptResult")}:</label>
                          <select value={overrideConcept} onChange={e => setOverrideConcept(e.target.value)} style={{ width: "100%", padding: "0.4rem" }}>
                            <option value="correct">{t("status.correct")}</option>
                            <option value="partial">{t("status.partial")}</option>
                            <option value="incorrect">{t("status.incorrect")}</option>
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: "0.75rem", fontWeight: 700 }}>{t("targetSkillResult")}:</label>
                          <select value={overrideTargetSkill} onChange={e => setOverrideTargetSkill(e.target.value)} style={{ width: "100%", padding: "0.4rem" }}>
                            <option value="correct">{t("status.correct")}</option>
                            <option value="incorrect">{t("status.incorrect")}</option>
                            <option value="not_applicable">{t("status.not_applicable")}</option>
                          </select>
                        </div>
                        <div>
                          <label style={{ fontSize: "0.75rem", fontWeight: 700 }}>{t("retryRequired")}:</label>
                          <select value={overrideRetry ? "yes" : "no"} onChange={e => setOverrideRetry(e.target.value === "yes")} style={{ width: "100%", padding: "0.4rem" }}>
                            <option value="no">{t("status.no")}</option>
                            <option value="yes">{t("status.yes")}</option>
                          </select>
                        </div>
                      </div>

                      <input
                        type="text"
                        placeholder={t("overrideReasonPlaceholder")}
                        value={overrideReason}
                        onChange={e => setOverrideReason(e.target.value)}
                        style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #86efac", marginBottom: "0.75rem" }}
                      />

                      <button
                        onClick={handleSubmitReview}
                        style={{ background: "#16a34a", color: "#ffffff", border: "none", padding: "0.5rem 1rem", borderRadius: "8px", fontWeight: 700, cursor: "pointer" }}
                      >
                        {t("applyOverride")}
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
                    <span>{t("proceedNext")}</span>
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
