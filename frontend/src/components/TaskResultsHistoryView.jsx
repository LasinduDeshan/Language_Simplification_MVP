import React, { useState, useEffect } from "react";
import {
  Clock, Award, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp,
  RefreshCw, Search, TrendingUp, TrendingDown, Minus,
  User, Activity, BarChart2, X, Sparkles
} from "lucide-react";
import { fetchTaskResults, deleteTaskResult } from "../services/api";

const CATEGORY_COLORS = {
  vocabulary: { bg: "#eff6ff", text: "#1d4ed8", border: "#bfdbfe" },
  grammar: { bg: "#fdf4ff", text: "#7e22ce", border: "#e9d5ff" },
  comprehension: { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
  sentence_and_instruction: { bg: "#fff7ed", text: "#c2410c", border: "#fed7aa" }
};

const DIFFICULTY_BADGES = {
  easy: { bg: "#dcfce7", text: "#15803d" },
  medium: { bg: "#fef9c3", text: "#854d0e" },
  hard: { bg: "#fee2e2", text: "#b91c1c" }
};

const OUTCOME_CONFIG = {
  success: { label: "✓ Independent Mastery", bg: "#dcfce7", text: "#15803d", border: "#86efac" },
  completed_with_adult_support: { label: "◑ With Adult Support", bg: "#eff6ff", text: "#1d4ed8", border: "#bfdbfe" },
  adult_support_required: { label: "⚠ Adult Support Required", bg: "#fffbeb", text: "#92400e", border: "#fde68a" }
};

function DeltaBadge({ delta }) {
  const isPos = delta > 0, isNeg = delta < 0;
  const color = isPos ? "#15803d" : isNeg ? "#b91c1c" : "#64748b";
  const bg = isPos ? "#dcfce7" : isNeg ? "#fee2e2" : "#f1f5f9";
  const Icon = isPos ? TrendingUp : isNeg ? TrendingDown : Minus;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "0.2rem",
      background: bg, color, borderRadius: "6px",
      padding: "0.15rem 0.5rem", fontSize: "0.75rem", fontWeight: 800
    }}>
      <Icon size={11} />
      {isPos ? `+${delta}` : delta} pts
    </span>
  );
}

function ScoreBar({ label, before, after, delta }) {
  return (
    <div style={{ marginBottom: "0.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.2rem" }}>
        <span style={{ fontSize: "0.72rem", color: "#64748b", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.03em" }}>
          {label}
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ fontSize: "0.78rem", color: "#94a3b8", textDecoration: "line-through" }}>{before}</span>
          <span style={{ fontSize: "0.85rem", fontWeight: 800, color: "#1e293b" }}>{after}</span>
          <DeltaBadge delta={delta} />
        </div>
      </div>
      <div style={{ background: "#f1f5f9", borderRadius: "9999px", height: "6px", overflow: "hidden" }}>
        <div style={{
          width: `${after}%`, height: "100%",
          background: after >= 68 ? "#10b981" : after >= 48 ? "#f59e0b" : "#ef4444",
          borderRadius: "9999px", transition: "width 0.5s ease"
        }} />
      </div>
    </div>
  );
}

function AttemptDrawer({ attempts }) {
  const [open, setOpen] = useState(false);
  if (!attempts || attempts.length === 0) return null;
  return (
    <div style={{ marginTop: "0.75rem" }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          display: "flex", alignItems: "center", gap: "0.4rem",
          background: "none", border: "1px solid #e2e8f0", borderRadius: "8px",
          padding: "0.4rem 0.8rem", fontSize: "0.8rem", color: "#475569",
          cursor: "pointer", fontWeight: 600
        }}
      >
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        {open ? "Hide" : "View"} Attempt Details ({attempts.length} attempt{attempts.length > 1 ? "s" : ""})
      </button>
      {open && (
        <div style={{ marginTop: "0.6rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {attempts.map((att, i) => {
            const isSuccess = att.target_skill_result === "correct" && !att.retry_required;
            return (
              <div key={i} style={{
                background: isSuccess ? "#f0fdf4" : "#fff8f8",
                border: `1px solid ${isSuccess ? "#bbf7d0" : "#fecaca"}`,
                borderRadius: "10px", padding: "0.75rem"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.4rem", flexWrap: "wrap", gap: "0.3rem" }}>
                  <span style={{ fontSize: "0.78rem", fontWeight: 800, color: "#1e293b" }}>
                    Attempt {att.attempt_number}
                  </span>
                  <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                    <span style={{
                      fontSize: "0.7rem", fontWeight: 700, padding: "0.1rem 0.5rem",
                      borderRadius: "9999px",
                      background: isSuccess ? "#dcfce7" : "#fee2e2",
                      color: isSuccess ? "#15803d" : "#b91c1c"
                    }}>
                      {isSuccess ? "✓ Correct" : "✗ Retry"}
                    </span>
                    <span style={{
                      fontSize: "0.7rem", fontWeight: 600, padding: "0.1rem 0.5rem",
                      borderRadius: "9999px", background: "#f1f5f9", color: "#475569"
                    }}>
                      {att.assistance_level}
                    </span>
                    {att.response_time_ms > 0 && (
                      <span style={{ fontSize: "0.7rem", color: "#94a3b8" }}>
                        {(att.response_time_ms / 1000).toFixed(1)}s
                      </span>
                    )}
                  </div>
                </div>
                {att.instruction && (
                  <div style={{ fontSize: "0.78rem", color: "#475569", marginBottom: "0.3rem" }}>
                    <strong>Instruction:</strong> {att.instruction}
                  </div>
                )}
                {(att.transcript || att.selected_option) && (
                  <div style={{ fontSize: "0.78rem", color: "#1e293b", fontStyle: "italic" }}>
                    <strong>Response:</strong> {att.transcript || att.selected_option}
                  </div>
                )}
                {att.grammar_observations && att.grammar_observations.length > 0 && (
                  <div style={{ marginTop: "0.3rem", fontSize: "0.7rem", color: "#7c3aed" }}>
                    Grammar observations: {att.grammar_observations.join(", ")}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ResultCard({ result, onDelete }) {
  const outcome = OUTCOME_CONFIG[result.final_outcome] || OUTCOME_CONFIG.adult_support_required;
  const catColor = CATEGORY_COLORS[result.category] || CATEGORY_COLORS.vocabulary;
  const diffBadge = DIFFICULTY_BADGES[result.difficulty] || DIFFICULTY_BADGES.medium;
  const riskColor = result.risk_after === "high" ? "#ef4444" : result.risk_after === "moderate" ? "#f59e0b" : "#10b981";

  const date = result.completed_at ? new Date(result.completed_at) : null;
  const dateStr = date ? date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

  return (
    <div style={{
      background: "#ffffff", borderRadius: "18px",
      border: `1px solid ${outcome.border}`,
      boxShadow: "0 2px 12px rgba(0,0,0,0.05)", overflow: "hidden"
    }}>
      {/* Header */}
      <div style={{
        background: outcome.bg, borderBottom: `1px solid ${outcome.border}`,
        padding: "0.85rem 1.25rem",
        display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{
            width: "32px", height: "32px", borderRadius: "50%",
            background: "#ffffff", display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 1px 4px rgba(0,0,0,0.1)"
          }}>
            <User size={16} color={riskColor} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: "0.95rem", color: "#1e293b" }}>
              {result.learner_code}
            </div>
            <div style={{ fontSize: "0.72rem", color: "#64748b" }}>
              Age {result.learner_age} · Risk: <strong style={{ color: riskColor, textTransform: "capitalize" }}>{result.risk_after}</strong>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
          <span style={{
            fontSize: "0.72rem", fontWeight: 700, padding: "0.2rem 0.65rem",
            borderRadius: "9999px", background: catColor.bg, color: catColor.text, border: `1px solid ${catColor.border}`
          }}>
            {result.category}
          </span>
          <span style={{
            fontSize: "0.7rem", fontWeight: 700, padding: "0.2rem 0.6rem",
            borderRadius: "9999px", background: diffBadge.bg, color: diffBadge.text
          }}>
            {result.difficulty}
          </span>
          <span style={{
            fontSize: "0.72rem", fontWeight: 700, padding: "0.2rem 0.65rem",
            borderRadius: "9999px", background: outcome.bg, color: outcome.text, border: `1px solid ${outcome.border}`
          }}>
            {outcome.label}
          </span>
          <button onClick={() => onDelete(result.id)} style={{
            background: "none", border: "none", cursor: "pointer", color: "#94a3b8", padding: "0.1rem"
          }} title="Remove this record">
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: "1rem 1.25rem" }}>
        <div style={{ marginBottom: "0.75rem" }}>
          <div style={{ fontWeight: 700, fontSize: "1rem", color: "#1e293b", marginBottom: "0.1rem" }}>
            {result.task_title}
          </div>
          <div style={{ fontSize: "0.78rem", color: "#64748b" }}>
            {result.task_code} · Skill: <strong>{result.target_skill || "—"}</strong>
            &nbsp;·&nbsp;{result.attempts_count} attempt{result.attempts_count > 1 ? "s" : ""}
            &nbsp;·&nbsp;<Clock size={11} style={{ verticalAlign: "middle" }} /> {dateStr}
          </div>
        </div>

        {/* Score evolution */}
        {result.score_before && result.score_after && (
          <div style={{ background: "#f8fafc", borderRadius: "12px", padding: "0.9rem 1rem", marginBottom: "0.75rem" }}>
            <div style={{ fontSize: "0.72rem", color: "#64748b", fontWeight: 700, marginBottom: "0.6rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
              Score Evolution (Before → After)
            </div>
            <ScoreBar label="Grammar" before={result.score_before.grammar_score} after={result.score_after.grammar_score} delta={result.score_deltas?.grammar ?? 0} />
            <ScoreBar label="Vocabulary" before={result.score_before.vocabulary_score} after={result.score_after.vocabulary_score} delta={result.score_deltas?.vocabulary ?? 0} />
            <ScoreBar label="Comprehension" before={result.score_before.comprehension_score} after={result.score_after.comprehension_score} delta={result.score_deltas?.comprehension ?? 0} />
            <ScoreBar label="Instruction" before={result.score_before.instruction_following_score} after={result.score_after.instruction_following_score} delta={result.score_deltas?.instruction ?? 0} />
          </div>
        )}

        {/* CLI + Risk + English badges */}
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.5rem" }}>
          {result.composite_language_index != null && (
            <span style={{ fontSize: "0.78rem", fontWeight: 700, padding: "0.25rem 0.75rem", borderRadius: "9999px", background: "#f1f5f9", color: "#334155", border: "1px solid #e2e8f0" }}>
              CLI: {result.composite_language_index}/100
            </span>
          )}
          {result.risk_changed && (
            <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "0.25rem 0.75rem", borderRadius: "9999px", background: "#fee2e2", color: "#b91c1c", border: "1px solid #f87171", display: "flex", alignItems: "center", gap: "0.3rem" }}>
              <AlertTriangle size={11} /> Risk: {result.risk_before} → {result.risk_after}
            </span>
          )}
          {result.score_after?.english_level && (
            <span style={{ fontSize: "0.75rem", fontWeight: 600, padding: "0.25rem 0.75rem", borderRadius: "9999px", background: "#eff6ff", color: "#1d4ed8", border: "1px solid #bfdbfe", textTransform: "capitalize" }}>
              English: {result.score_after.english_level}
            </span>
          )}
        </div>

        {result.diagnostic_notes && (
          <div style={{ fontSize: "0.75rem", color: "#64748b", background: "#f8fafc", borderRadius: "8px", padding: "0.6rem 0.8rem", borderLeft: "3px solid #cbd5e1", marginBottom: "0.5rem" }}>
            {result.diagnostic_notes}
          </div>
        )}

        <AttemptDrawer attempts={result.attempt_history} />
      </div>
    </div>
  );
}

export default function TaskResultsHistoryView({ onNavigateToPlayground }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterLearner, setFilterLearner] = useState("all");
  const [filterCategory, setFilterCategory] = useState("all");
  const [filterOutcome, setFilterOutcome] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const loadResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = {};
      if (filterLearner !== "all") filters.learner_code = filterLearner;
      if (filterCategory !== "all") filters.category = filterCategory;
      if (filterOutcome !== "all") filters.outcome = filterOutcome;
      filters.limit = 200;
      const res = await fetchTaskResults(filters);
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadResults(); }, [filterLearner, filterCategory, filterOutcome]);

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this result record?")) return;
    try { await deleteTaskResult(id); loadResults(); }
    catch (err) { alert("Delete failed: " + err.message); }
  };

  const results = (data?.results || []).filter(r => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      r.task_title?.toLowerCase().includes(q) ||
      r.learner_code?.toLowerCase().includes(q) ||
      r.target_skill?.toLowerCase().includes(q) ||
      r.category?.toLowerCase().includes(q)
    );
  });

  const agg = data?.aggregate || {};
  const allLearners = [...new Set((data?.results || []).map(r => r.learner_code))].sort();

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "1.5rem" }}>
      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)", borderRadius: "20px", padding: "1.75rem 2rem", color: "#ffffff", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.3rem" }}>
              <Clock size={22} color="#f97316" />
              <h1 style={{ margin: 0, fontSize: "1.45rem", fontWeight: 900 }}>Results &amp; History</h1>
            </div>
            <p style={{ margin: 0, color: "#94a3b8", fontSize: "0.9rem" }}>
              Every completed session is stored automatically. Track Grammar, Vocabulary, Comprehension &amp; Instruction score evolution over time.
            </p>
          </div>
          <button onClick={loadResults} style={{ background: "#f97316", border: "none", borderRadius: "10px", padding: "0.6rem 1.2rem", color: "#fff", fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem" }}>
            <RefreshCw size={15} /> Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      {data && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
          {[
            { label: "Total Sessions", value: agg.total ?? 0, icon: Activity, color: "#6366f1" },
            { label: "Mastery Rate", value: `${agg.mastery_rate_pct ?? 0}%`, icon: Award, color: "#10b981" },
            { label: "Adult Escalations", value: agg.adult_escalations ?? 0, icon: AlertTriangle, color: "#f59e0b" },
            { label: "Avg Attempts", value: agg.avg_attempts ?? 0, icon: BarChart2, color: "#8b5cf6" },
            { label: "Avg Grammar Δ", value: `${agg.avg_grammar_delta > 0 ? "+" : ""}${agg.avg_grammar_delta ?? 0}`, icon: TrendingUp, color: (agg.avg_grammar_delta ?? 0) >= 0 ? "#10b981" : "#ef4444" }
          ].map(kpi => {
            const IconComp = kpi.icon;
            return (
              <div key={kpi.label} style={{ background: "#ffffff", borderRadius: "14px", padding: "1rem 1.25rem", border: "1px solid #e2e8f0", boxShadow: "0 1px 6px rgba(0,0,0,0.04)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                  <span style={{ fontSize: "0.68rem", color: "#64748b", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em" }}>{kpi.label}</span>
                  <div style={{ width: "28px", height: "28px", borderRadius: "8px", background: `${kpi.color}15`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <IconComp size={14} color={kpi.color} />
                  </div>
                </div>
                <div style={{ fontSize: "1.5rem", fontWeight: 900, color: "#1e293b" }}>{kpi.value}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Filters */}
      <div style={{ background: "#ffffff", borderRadius: "16px", padding: "1rem 1.25rem", border: "1px solid #e2e8f0", marginBottom: "1.5rem", display: "flex", flexWrap: "wrap", gap: "0.75rem", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flex: 1, minWidth: "180px" }}>
          <Search size={15} color="#94a3b8" />
          <input type="text" placeholder="Search task title, learner, skill…" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} style={{ border: "none", outline: "none", width: "100%", fontSize: "0.88rem", color: "#1e293b" }} />
          {searchQuery && <button onClick={() => setSearchQuery("")} style={{ background: "none", border: "none", cursor: "pointer", color: "#94a3b8" }}><X size={13} /></button>}
        </div>
        <select value={filterLearner} onChange={e => setFilterLearner(e.target.value)} style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "0.4rem 0.75rem", fontSize: "0.85rem", color: "#1e293b", background: "#f8fafc", cursor: "pointer" }}>
          <option value="all">All Learners</option>
          {allLearners.map(code => <option key={code} value={code}>{code}</option>)}
        </select>
        <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)} style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "0.4rem 0.75rem", fontSize: "0.85rem", color: "#1e293b", background: "#f8fafc", cursor: "pointer" }}>
          <option value="all">All Categories</option>
          <option value="vocabulary">Vocabulary</option>
          <option value="grammar">Grammar</option>
          <option value="comprehension">Comprehension</option>
          <option value="sentence_and_instruction">Sentence &amp; Instruction</option>
        </select>
        <select value={filterOutcome} onChange={e => setFilterOutcome(e.target.value)} style={{ border: "1px solid #e2e8f0", borderRadius: "8px", padding: "0.4rem 0.75rem", fontSize: "0.85rem", color: "#1e293b", background: "#f8fafc", cursor: "pointer" }}>
          <option value="all">All Outcomes</option>
          <option value="success">✓ Independent Mastery</option>
          <option value="adult_support_required">⚠ Adult Support Required</option>
          <option value="completed_with_adult_support">◑ With Adult Support</option>
        </select>
        <span style={{ fontSize: "0.8rem", color: "#94a3b8", whiteSpace: "nowrap" }}>{results.length} result{results.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Results list */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "4rem", color: "#94a3b8" }}>
          <div style={{ fontSize: "1rem", marginTop: "1rem" }}>Loading results…</div>
        </div>
      ) : error ? (
        <div style={{ background: "#fee2e2", border: "1px solid #f87171", borderRadius: "14px", padding: "1.5rem", textAlign: "center", color: "#b91c1c" }}>
          {error}
        </div>
      ) : results.length === 0 ? (
        <div style={{ background: "#f8fafc", borderRadius: "18px", padding: "4rem 2rem", textAlign: "center", border: "2px dashed #e2e8f0" }}>
          <Sparkles size={48} color="#cbd5e1" style={{ marginBottom: "1rem" }} />
          <h3 style={{ color: "#64748b", margin: "0 0 0.5rem 0" }}>No Results Yet</h3>
          <p style={{ color: "#94a3b8", margin: 0 }}>
            Complete a learning session in the Interactive Playground — results are stored automatically.
          </p>
          {onNavigateToPlayground && (
            <button onClick={onNavigateToPlayground} style={{ marginTop: "1.5rem", background: "#f97316", color: "#fff", border: "none", borderRadius: "12px", padding: "0.75rem 1.75rem", fontSize: "0.95rem", fontWeight: 700, cursor: "pointer" }}>
              Go to Interactive Playground
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {results.map(result => (
            <ResultCard key={result.id} result={result} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
