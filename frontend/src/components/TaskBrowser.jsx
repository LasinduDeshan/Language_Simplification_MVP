import React, { useState } from "react";
import { BookOpen, ShieldCheck, Box, Tag, ArrowRight } from "lucide-react";

export default function TaskBrowser({ tasks, onSelectTask }) {
  const [filterType, setFilterType] = useState("all");

  const filteredTasks = tasks.filter(t => filterType === "all" || t.task_type === filterType);
  const types = ["all", "classroom", "categorization", "vocabulary", "grammar", "sequence", "comprehension", "ar"];

  return (
    <div>
      <div className="section-header">
        <div>
          <h1 className="section-title">Preloaded Task Repository</h1>
          <p className="section-subtitle">
            Sprint 1 curated task bank designed for ages 4–8 with protected answers and AR metadata.
          </p>
        </div>

        {/* Filter Pills */}
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {types.map(t => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`btn btn-sm ${filterType === t ? "btn-primary" : "btn-secondary"}`}
              style={{ textTransform: "capitalize" }}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="grid-2">
        {filteredTasks.map(task => (
          <div key={task.id} className="card card-glass" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                <span className="chip chip-type">{task.task_type}</span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontFamily: "monospace" }}>
                  {task.task_code}
                </span>
              </div>

              <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.5rem" }}>
                {task.title}
              </h2>

              <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
                <strong>Objective:</strong> {task.learning_objective}
              </p>

              <div style={{
                background: "rgba(0, 0, 0, 0.25)",
                padding: "0.85rem",
                borderRadius: "var(--radius-sm)",
                borderLeft: "3px solid var(--accent-primary)",
                marginBottom: "1rem"
              }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700, display: "block", marginBottom: "0.25rem" }}>
                  Original Classroom Instruction
                </span>
                <p style={{ fontSize: "0.9rem", color: "#e2e8f0", fontStyle: "italic" }}>
                  "{task.original_instruction}"
                </p>
              </div>

              {/* Protected answers metadata check */}
              {task.protected_answers && task.protected_answers.restricted_solution_phrases && (
                <div style={{ marginBottom: "1rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.75rem", color: "#34d399", fontWeight: 600, marginBottom: "0.3rem" }}>
                    <ShieldCheck size={14} />
                    <span>PROTECTED ANSWER RELATIONS ({task.protected_answers.relations?.length || 0})</span>
                  </div>
                  <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                    {task.protected_answers.restricted_solution_phrases.slice(0, 2).map((phrase, idx) => (
                      <span key={idx} style={{ fontSize: "0.75rem", background: "rgba(52, 211, 153, 0.1)", color: "#a7f3d0", padding: "2px 8px", borderRadius: "4px" }}>
                        🔒 {phrase}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid var(--border-color)" }}>
              <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                Ages: <strong>{task.minimum_age}–{task.maximum_age} yrs</strong> | Diff: <strong style={{ textTransform: "capitalize" }}>{task.base_difficulty}</strong>
              </span>

              <button
                onClick={() => onSelectTask(task)}
                className="btn btn-primary btn-sm"
              >
                <span>Select For Simulation</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
