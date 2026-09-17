import React from "react";
import { User, Activity, Award, ArrowRight } from "lucide-react";

export default function LearnerBrowser({ learners, onSelectLearner }) {
  return (
    <div>
      <div className="section-header">
        <div>
          <h1 className="section-title">Learner Profile Repository</h1>
          <p className="section-subtitle">
            Simulated Component 1 profiles with varying risk levels, vocabulary & grammar scores, and English proficiency.
          </p>
        </div>
      </div>

      <div className="grid-3">
        {learners.map(l => (
          <div key={l.id} className="card card-glass" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
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

                <span className={`chip chip-${l.risk_support_level}`}>
                  {l.risk_support_level} Risk
                </span>
              </div>

              {/* Metrics breakdown */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.6rem", marginBottom: "1.25rem" }}>
                <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.6rem", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>VOCABULARY</span>
                  <strong style={{ fontSize: "1.1rem", color: l.vocabulary_score < 50 ? "#f87171" : "#34d399" }}>
                    {l.vocabulary_score}/100
                  </strong>
                </div>

                <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.6rem", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>GRAMMAR</span>
                  <strong style={{ fontSize: "1.1rem", color: l.grammar_score < 50 ? "#f87171" : "#34d399" }}>
                    {l.grammar_score}/100
                  </strong>
                </div>

                <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.6rem", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>COMPREHENSION</span>
                  <strong style={{ fontSize: "1.1rem", color: "#60a5fa" }}>
                    {l.comprehension_score}/100
                  </strong>
                </div>

                <div style={{ background: "rgba(0,0,0,0.2)", padding: "0.6rem", borderRadius: "8px" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "block" }}>ENGLISH LEVEL</span>
                  <strong style={{ fontSize: "0.85rem", color: "#e2e8f0", textTransform: "capitalize" }}>
                    {l.english_level}
                  </strong>
                </div>
              </div>
            </div>

            <button
              onClick={() => onSelectLearner(l)}
              className="btn btn-secondary btn-sm"
              style={{ width: "100%", justifyContent: "center" }}
            >
              <span>Load Profile into Simulator</span>
              <ArrowRight size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
