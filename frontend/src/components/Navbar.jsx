import React from "react";
import { Sparkles, Activity, BookOpen, Users, PlayCircle, Eye, Sliders } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, isBackendHealthy, generationMode, setGenerationMode }) {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <div className="brand-icon">
          <Sparkles size={22} />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span className="brand-title">Adaptive Language MVP</span>
            <span className="brand-tag">v2.2</span>
          </div>
          <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
            DLD-Friendly Language Simplification (Ages 4–8)
          </p>
        </div>
      </div>

      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          <PlayCircle size={16} />
          <span>Dashboard & Simulation</span>
        </button>

        <button
          className={`nav-tab ${activeTab === "personalization" ? "active" : ""}`}
          onClick={() => setActiveTab("personalization")}
        >
          <Sliders size={16} />
          <span>Personalization & Rules</span>
        </button>

        <button
          className={`nav-tab ${activeTab === "analysis" ? "active" : ""}`}
          onClick={() => setActiveTab("analysis")}
        >
          <Activity size={16} />
          <span>Analysis & Diagnostics</span>
        </button>

        <button
          className={`nav-tab ${activeTab === "tasks" ? "active" : ""}`}
          onClick={() => setActiveTab("tasks")}
        >
          <BookOpen size={16} />
          <span>Task Repository (10)</span>
        </button>

        <button
          className={`nav-tab ${activeTab === "learners" ? "active" : ""}`}
          onClick={() => setActiveTab("learners")}
        >
          <Users size={16} />
          <span>Learner Profiles (5)</span>
        </button>
      </nav>

      <div className="navbar-actions">
        {/* Generation Mode Switcher */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)", fontWeight: 600 }}>MODE:</span>
          <select
            className="form-select"
            style={{ padding: "4px 8px", fontSize: "0.8rem", width: "auto" }}
            value={generationMode}
            onChange={(e) => setGenerationMode(e.target.value)}
          >
            <option value="rule">Rule (100% Offline)</option>
            <option value="hybrid">Hybrid (Target)</option>
            <option value="llm">LLM (Experimental)</option>
          </select>
        </div>

        {/* Health Status */}
        <div className={`status-badge ${isBackendHealthy ? "status-healthy" : ""}`}>
          <div className="status-indicator" />
          <span>{isBackendHealthy ? "FastAPI Online" : "Connecting..."}</span>
        </div>
      </div>
    </header>
  );
}
