import React from "react";
import { User, Activity, Award, ArrowRight, Shield, BookOpen, Info } from "lucide-react";

export default function LearnerBrowser({ learners, onSelectLearner }) {
  return (
    <div>
      <div className="section-header">
        <div>
          <h1 className="section-title">Learner Educational Performance Profiles</h1>
          <p className="section-subtitle">
            Educational performance indicators and read-only screening inputs from Component 1.
          </p>
        </div>
      </div>

      {/* Mandatory Non-Diagnostic Educational Disclaimer */}
      <div style={{
        background: "rgba(59, 130, 246, 0.08)",
        border: "1px solid rgba(59, 130, 246, 0.25)",
        borderRadius: "10px",
        padding: "0.85rem 1.25rem",
        marginBottom: "1.5rem",
        display: "flex",
        alignItems: "center",
        gap: "0.75rem",
        color: "#93c5fd"
      }}>
        <Info size={20} style={{ flexShrink: 0, color: "#60a5fa" }} />
        <span style={{ fontSize: "0.85rem", lineHeight: "1.4" }}>
          <strong>Educational Notice:</strong> This application provides educational language support and research performance tracking. It is not a diagnostic instrument and does not replace assessment or advice from qualified speech-language professionals.
        </span>
      </div>

      <div className="grid-3">
        {learners.map(l => {
          const screeningRisk = l.screening_risk_level || l.risk_support_level || "moderate";
          const recommendedSupport = l.recommended_support_level || "moderate";
          
          return (
            <div key={l.id} className="card card-glass" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.85rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <div style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "50%",
                      background: "rgba(99, 102, 241, 0.2)",
                      color: "#818cf8",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 700,
                      fontSize: "0.9rem"
                    }}>
                      {l.learner_code.slice(-3)}
                    </div>
                    <div>
                      <h2 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#ffffff" }}>
                        {l.learner_code}
                      </h2>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        Age {l.age} | {l.grade || "Pre-K"}
                      </span>
                    </div>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <span className={`chip chip-${screeningRisk}`} title="Read-only screening indicator imported from Component 1">
                      {screeningRisk} Risk (C1)
                    </span>
                    <span style={{ display: "block", fontSize: "0.65rem", color: "var(--text-muted)", marginTop: "2px" }}>
                      Read-only Screening
                    </span>
                  </div>
                </div>

                {/* Recommended Educational Support Level */}
                <div style={{
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  borderRadius: "8px",
                  padding: "0.5rem 0.75rem",
                  marginBottom: "1rem",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <span style={{ fontSize: "0.75rem", color: "#cbd5e1" }}>Recommended Support:</span>
                  <span style={{
                    fontWeight: 700,
                    fontSize: "0.78rem",
                    textTransform: "uppercase",
                    color: recommendedSupport === "strong" ? "#fca5a5" : recommendedSupport === "moderate" ? "#fde047" : "#86efac"
                  }}>
                    {recommendedSupport}
                  </span>
                </div>

                {/* Educational Performance Domain Scores */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", marginBottom: "1.25rem" }}>
                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.55rem", borderRadius: "8px" }}>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", display: "block" }}>VOCABULARY</span>
                    <strong style={{ fontSize: "1.05rem", color: l.vocabulary_score < 50 ? "#f87171" : "#34d399" }}>
                      {l.vocabulary_score}/100
                    </strong>
                    <span style={{ fontSize: "0.65rem", color: "#94a3b8", display: "block" }}>
                      Ev: {l.vocabulary_evidence_count || 0}
                    </span>
                  </div>

                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.55rem", borderRadius: "8px" }}>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", display: "block" }}>GRAMMAR</span>
                    <strong style={{ fontSize: "1.05rem", color: l.grammar_score < 50 ? "#f87171" : "#34d399" }}>
                      {l.grammar_score}/100
                    </strong>
                    <span style={{ fontSize: "0.65rem", color: "#94a3b8", display: "block" }}>
                      Ev: {l.grammar_evidence_count || 0}
                    </span>
                  </div>

                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.55rem", borderRadius: "8px" }}>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", display: "block" }}>COMPREHENSION</span>
                    <strong style={{ fontSize: "1.05rem", color: "#60a5fa" }}>
                      {l.comprehension_score}/100
                    </strong>
                    <span style={{ fontSize: "0.65rem", color: "#94a3b8", display: "block" }}>
                      Ev: {l.comprehension_evidence_count || 0}
                    </span>
                  </div>

                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.55rem", borderRadius: "8px" }}>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-muted)", display: "block" }}>INSTRUCTION</span>
                    <strong style={{ fontSize: "1.05rem", color: "#a78bfa" }}>
                      {l.instruction_following_score}/100
                    </strong>
                    <span style={{ fontSize: "0.65rem", color: "#94a3b8", display: "block" }}>
                      Ev: {l.instruction_evidence_count || 0}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => onSelectLearner(l)}
                className="btn btn-secondary btn-sm"
                style={{ width: "100%", justifyContent: "center" }}
              >
                <span>Select for Guided Session</span>
                <ArrowRight size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
