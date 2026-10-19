import React, { useState, useEffect } from "react";
import { CheckCircle2, RotateCcw, AlertCircle, Info, Sparkles, BookOpen } from "lucide-react";

/**
 * SubjectPredicateTask Component
 * Implements the governed two-stage activity for GRAM-SI-SUBPRED-001:
 * උක්තය සහ ආඛ්‍යාතය (Subject and Predicate)
 * 
 * Rules:
 * - State 1: Select Subject (උක්තය)
 * - State 2: Select Predicate (ආඛ්‍යාතය)
 * - State 3: Completed / Results
 * - Predicate is NOT just the verb (verb is part of predicate)
 * - Blue for Subject, Orange for Predicate, Green for confirmation
 * - Resets on attempt change
 * - Screen reader announcements with aria-live="polite"
 * - Simple View hides technical metadata; Researcher View displays contract details
 */
export default function SubjectPredicateTask({
  task,
  attempt,
  viewMode = "simple",
  resolvedLanguage = "si",
  onSelectionChange,
  isChildModal = false
}) {
  const isSi = String(resolvedLanguage || "").toLowerCase().startsWith("si");

  // Primary item data
  const sentence = "ළමයා පොත කියවයි.";
  const expectedSubject = "ළමයා";
  const expectedPredicate = "පොත කියවයි";
  const verbOnly = "කියවයි";

  // Available selectable segments / options
  const segments = [
    { id: "subj", text: "ළමයා", role: "subject", label: isSi ? "උක්තය" : "Subject" },
    { id: "pred", text: "පොත කියවයි", role: "predicate", label: isSi ? "ආඛ්‍යාතය" : "Predicate" },
    { id: "verb", text: "කියවයි", role: "verb", label: isSi ? "ක්‍රියා පදය පමණක්" : "Verb only" }
  ];

  // Stage: 1 = subject selection, 2 = predicate selection, 3 = completed
  const [stage, setStage] = useState(1);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedPredicate, setSelectedPredicate] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [announcement, setAnnouncement] = useState("");

  // Reset state when attempt or task changes
  useEffect(() => {
    setStage(1);
    setSelectedSubject(null);
    setSelectedPredicate(null);
    setFeedback(null);
    setAnnouncement(isSi ? "පළමුව උක්තය තෝරන්න." : "First, select the subject.");
  }, [attempt?.id, task?.task_code, task?.id]);

  const handleSelectSegment = (segment) => {
    if (stage === 1) {
      // Expecting Subject
      if (segment.text === expectedSubject) {
        setSelectedSubject(segment.text);
        setStage(2);
        const fbText = isSi ? "හරි! “ළමයා” උක්තයයි. දැන් ආඛ්‍යාතය තෝරන්න." : "Correct! “ළමයා” is the subject. Now select the predicate.";
        setFeedback({ type: "success", text: fbText });
        setAnnouncement(fbText);
        if (onSelectionChange) {
          onSelectionChange({ subject: segment.text, predicate: null, stage: 2 });
        }
      } else {
        const errText = isSi ? "නැවත බලන්න. වාක්‍යය කවුරුන් ගැනද?" : "Try again. Whom is the sentence about?";
        setFeedback({ type: "hint", text: errText });
        setAnnouncement(errText);
      }
    } else if (stage === 2) {
      // Expecting Predicate
      if (segment.text === expectedPredicate) {
        setSelectedPredicate(segment.text);
        setStage(3);
        const fbText = isSi
          ? "හොඳයි! ඔබ උක්තය සහ ආඛ්‍යාතය හඳුනාගත්තා. “පොත කියවයි” ආඛ්‍යාතයයි."
          : "Well done! You identified the subject and predicate. “පොත කියවයි” is the predicate.";
        setFeedback({ type: "completed", text: fbText });
        setAnnouncement(fbText);
        if (onSelectionChange) {
          onSelectionChange({
            subject: selectedSubject,
            predicate: segment.text,
            stage: 3,
            isCompleted: true,
            summary: `${selectedSubject} | ${segment.text}`
          });
        }
      } else if (segment.text === verbOnly) {
        // Trap: Selected only the verb!
        const hintText = isSi
          ? "නැවත බලන්න. “කියවයි” ක්‍රියා පදය පමණි. ආඛ්‍යාතයට ක්‍රියාව සහ ඒ හා බැඳි අනෙක් වචන ද අයත් වේ (සම්පූර්ණ ආඛ්‍යාතය: “පොත කියවයි”)."
          : "Notice: “කියවයි” is only the verb. The full predicate includes what is said about the subject: “පොත කියවයි”.";
        setFeedback({ type: "hint", text: hintText });
        setAnnouncement(hintText);
      } else {
        const errText = isSi ? "නැවත බලන්න. උක්තය ගැන කියන්නේ කුමක්ද?" : "Try again. What does the sentence say about the subject?";
        setFeedback({ type: "hint", text: errText });
        setAnnouncement(errText);
      }
    }
  };

  const handleReset = () => {
    setStage(1);
    setSelectedSubject(null);
    setSelectedPredicate(null);
    setFeedback(null);
    const msg = isSi ? "නැවත ආරම්භ විය. පළමුව උක්තය තෝරන්න." : "Reset. First, select the subject.";
    setAnnouncement(msg);
    if (onSelectionChange) {
      onSelectionChange({ subject: null, predicate: null, stage: 1 });
    }
  };

  return (
    <div
      className="subject-predicate-task"
      style={{
        fontFamily: '"Noto Sans Sinhala", "Nirmala UI", "Iskoola Pota", sans-serif',
        lineHeight: 1.55,
        letterSpacing: "normal",
        fontSynthesis: "none",
        background: isChildModal ? "rgba(255, 255, 255, 0.95)" : "#f8fafc",
        borderRadius: "20px",
        padding: isChildModal ? "1.5rem" : "1.25rem",
        border: "2px solid #e2e8f0",
        marginTop: "1rem",
        marginBottom: "1rem"
      }}
    >
      {/* Screen Reader Announcement */}
      <div
        aria-live="polite"
        style={{ position: "absolute", width: "1px", height: "1px", overflow: "hidden", clip: "rect(0,0,0,0)" }}
      >
        {announcement}
      </div>

      {/* Header & Stage indicator */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <BookOpen size={20} color="#f97316" />
          <span style={{ fontWeight: 800, fontSize: "1rem", color: "#1e293b" }}>
            {isSi ? "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම" : "Identifying Subject and Predicate"}
          </span>
        </div>
        <div style={{ display: "flex", gap: "0.4rem" }}>
          <span
            style={{
              padding: "0.25rem 0.6rem",
              borderRadius: "9999px",
              fontSize: "0.75rem",
              fontWeight: 700,
              background: stage === 1 ? "#dbeafe" : "#f1f5f9",
              color: stage === 1 ? "#1d4ed8" : "#64748b",
              border: stage === 1 ? "1px solid #3b82f6" : "1px solid #cbd5e1"
            }}
          >
            {isSi ? "1. උක්තය" : "1. Subject"}
          </span>
          <span
            style={{
              padding: "0.25rem 0.6rem",
              borderRadius: "9999px",
              fontSize: "0.75rem",
              fontWeight: 700,
              background: stage === 2 ? "#ffedd5" : "#f1f5f9",
              color: stage === 2 ? "#c2410c" : "#64748b",
              border: stage === 2 ? "1px solid #f97316" : "1px solid #cbd5e1"
            }}
          >
            {isSi ? "2. ආඛ්‍යාතය" : "2. Predicate"}
          </span>
          {stage === 3 && (
            <span
              style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "9999px",
                fontSize: "0.75rem",
                fontWeight: 700,
                background: "#dcfce7",
                color: "#15803d",
                border: "1px solid #16a34a"
              }}
            >
              ✓ {isSi ? "සම්පූර්ණයි" : "Done"}
            </span>
          )}
        </div>
      </div>

      {/* Main Sentence Card with Segment Visual Mapping */}
      <div
        style={{
          background: "#ffffff",
          borderRadius: "16px",
          padding: "1.5rem",
          border: "2px solid #fed7aa",
          boxShadow: "0 4px 12px rgba(249, 115, 22, 0.08)",
          textAlign: "center",
          marginBottom: "1.25rem"
        }}
      >
        <div style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600, marginBottom: "0.5rem" }}>
          {stage === 1
            ? (isSi ? "පළමුව උක්තය (කවුරුන් ගැනද කියන්නේ) තෝරන්න:" : "First, select the subject (whom the sentence is about):")
            : stage === 2
            ? (isSi ? "දැන් ආඛ්‍යාතය (උක්තය ගැන කියන දෙය) තෝරන්න:" : "Now select the predicate (what is said about the subject):")
            : (isSi ? "වාක්‍යය විශ්ලේෂණය සම්පූර්ණයි:" : "Sentence analysis complete:")}
        </div>

        {/* Big Sentence Display */}
        <div
          style={{
            fontSize: "1.85rem",
            fontWeight: 800,
            color: "#1e293b",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "0.75rem",
            flexWrap: "wrap",
            margin: "1rem 0"
          }}
        >
          {/* Subject span */}
          <span
            style={{
              padding: "0.3rem 0.8rem",
              borderRadius: "10px",
              background: selectedSubject ? "#dbeafe" : "transparent",
              color: selectedSubject ? "#1e40af" : "inherit",
              border: selectedSubject ? "2px solid #3b82f6" : "2px dashed #cbd5e1",
              position: "relative",
              transition: "all 0.2s"
            }}
          >
            {expectedSubject}
            {selectedSubject && (
              <span
                style={{
                  position: "absolute",
                  bottom: "-18px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  fontSize: "0.7rem",
                  fontWeight: 700,
                  color: "#1d4ed8",
                  background: "#eff6ff",
                  padding: "1px 6px",
                  borderRadius: "4px",
                  border: "1px solid #bfdbfe"
                }}
              >
                {isSi ? "උක්තය" : "Subject"}
              </span>
            )}
          </span>

          {/* Predicate span */}
          <span
            style={{
              padding: "0.3rem 0.8rem",
              borderRadius: "10px",
              background: selectedPredicate ? "#ffedd5" : "transparent",
              color: selectedPredicate ? "#c2410c" : "inherit",
              border: selectedPredicate ? "2px solid #f97316" : "2px dashed #cbd5e1",
              position: "relative",
              transition: "all 0.2s"
            }}
          >
            {expectedPredicate}
            {selectedPredicate && (
              <span
                style={{
                  position: "absolute",
                  bottom: "-18px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  fontSize: "0.7rem",
                  fontWeight: 700,
                  color: "#c2410c",
                  background: "#fff7ed",
                  padding: "1px 6px",
                  borderRadius: "4px",
                  border: "1px solid #fed7aa"
                }}
              >
                {isSi ? "ආඛ්‍යාතය" : "Predicate"}
              </span>
            )}
          </span>
        </div>
      </div>

      {/* Selectable Options */}
      {stage < 3 && (
        <div style={{ marginBottom: "1rem" }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#475569", marginBottom: "0.5rem" }}>
            {isSi ? "පහත කොටස් වලින් නිවැරදි කොටස තෝරන්න:" : "Choose the matching segment below:"}
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", justifyContent: "center" }}>
            {segments.map((seg) => (
              <button
                key={seg.id}
                type="button"
                onClick={() => handleSelectSegment(seg)}
                style={{
                  padding: "0.6rem 1.25rem",
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  borderRadius: "12px",
                  border: "2px solid #cbd5e1",
                  background: "#ffffff",
                  color: "#1e293b",
                  cursor: "pointer",
                  boxShadow: "0 2px 6px rgba(0,0,0,0.04)",
                  transition: "all 0.15s ease-in-out"
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = "#f97316";
                  e.currentTarget.style.background = "#fff7ed";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = "#cbd5e1";
                  e.currentTarget.style.background = "#ffffff";
                }}
              >
                {seg.text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Localized Feedback Banner */}
      {feedback && (
        <div
          role="status"
          style={{
            padding: "0.75rem 1rem",
            borderRadius: "12px",
            fontSize: "0.95rem",
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            gap: "0.6rem",
            marginBottom: "0.75rem",
            background:
              feedback.type === "completed" || feedback.type === "success"
                ? "#ecfdf5"
                : "#fffbeb",
            color:
              feedback.type === "completed" || feedback.type === "success"
                ? "#065f46"
                : "#92400e",
            border:
              feedback.type === "completed" || feedback.type === "success"
                ? "1px solid #a7f3d0"
                : "1px solid #fde68a"
          }}
        >
          {feedback.type === "completed" || feedback.type === "success" ? (
            <CheckCircle2 size={20} color="#10b981" />
          ) : (
            <Info size={20} color="#d97706" />
          )}
          <span>{feedback.text}</span>
        </div>
      )}

      {/* Completion Details & Linguistic Note (Explains predicate contains verb) */}
      {stage === 3 && (
        <div
          style={{
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
            borderRadius: "12px",
            padding: "1rem",
            fontSize: "0.9rem",
            color: "#1e40af",
            marginBottom: "1rem"
          }}
        >
          <div style={{ fontWeight: 800, marginBottom: "0.3rem" }}>
            {isSi ? "භාෂාමය පැහැදිලි කිරීම:" : "Linguistic Explanation:"}
          </div>
          <ul style={{ margin: "0 0 0 1.25rem", padding: 0 }}>
            <li>
              <strong>{isSi ? "උක්තය:" : "Subject:"}</strong> {expectedSubject} ({isSi ? "වාක්‍යය කවුරුන් ගැනද කියයි" : "identifies whom the sentence is about"})
            </li>
            <li>
              <strong>{isSi ? "ආඛ්‍යාතය:" : "Predicate:"}</strong> {expectedPredicate} ({isSi ? "උක්තය ගැන කියන දෙය; මෙහි ක්‍රියා පදය “කියවයි” ද අන්තර්ගත වේ" : "what is said about the subject; contains the verb “කියවයි”"})
            </li>
            <li>
              <strong>{isSi ? "ක්‍රියා පදය:" : "Verb:"}</strong> {verbOnly} ({isSi ? "සිදු කරන ක්‍රියාව — මෙය ආඛ්‍යාතයේ කොටසකි" : "the action; part of the predicate"})
            </li>
          </ul>
        </div>
      )}

      {/* Reset button */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <button
          type="button"
          onClick={handleReset}
          style={{
            background: "none",
            border: "none",
            color: "#64748b",
            fontSize: "0.85rem",
            fontWeight: 700,
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: "0.3rem",
            padding: "0.3rem 0.5rem"
          }}
        >
          <RotateCcw size={14} />
          <span>{isSi ? "නැවත උත්සාහ කරන්න" : "Try Again"}</span>
        </button>

        {/* Researcher Mode Metadata - Strictly hidden from Simple View */}
        {viewMode === "researcher" && (
          <div style={{ fontSize: "0.75rem", color: "#64748b", textAlign: "right" }}>
            <span>Task: <code>{task?.task_code || "GRAM-SI-SUBPRED-001"}</code></span> • 
            <span> Validation: <code>draft</code></span> • 
            <span> Delivery Approved: <code>false</code></span>
          </div>
        )}
      </div>
    </div>
  );
}
