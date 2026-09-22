import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles, PlayCircle, ShieldCheck, Award, Layers, Clock,
  ChevronDown, BookOpen, Users, Activity, Sliders, Cpu, Check
} from "lucide-react";

export default function Navbar({
  activeTab,
  setActiveTab,
  isBackendHealthy,
  generationMode,
  setGenerationMode,
  viewMode,
  setViewMode
}) {
  const [isLabMenuOpen, setIsLabMenuOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsLabMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const labTabs = [
    { id: "dashboard", label: "Advanced Scenario Console", icon: PlayCircle, desc: "Full simulation & attempt matrix" },
    { id: "tasks", label: "Task Repository (10)", icon: BookOpen, desc: "Browse curated English tasks" },
    { id: "learners", label: "Learner Profiles (5)", icon: Users, desc: "Review educational performance profiles" },
    { id: "analysis", label: "Linguistic & spaCy Diagnostics", icon: Activity, desc: "Clause & grammar parse tree" },
    { id: "personalization", label: "Personalization Rules", icon: Sliders, desc: "Pedagogical templates & tier rules" },
    { id: "integrations", label: "Subsystem JSON Payloads", icon: Cpu, desc: "Component 1, 2 (AR), 4 schemas" }
  ];

  const isLabTabActive = labTabs.some(t => t.id === activeTab);

  return (
    <header className="navbar">
      {/* Brand & Title */}
      <div className="navbar-brand" onClick={() => setActiveTab("playground")} style={{ cursor: "pointer" }}>
        <div className="brand-icon">
          <Sparkles size={22} />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span className="brand-title">Adaptive Language MVP</span>
            <span className="brand-tag">v2.2</span>
          </div>
          <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
            Child-Friendly Language Simplifier (Ages 4–8)
          </p>
        </div>
      </div>

      {/* Streamlined Primary Navigation Tabs */}
      <nav className="nav-tabs">
        {/* 1. Primary: Guided Playground */}
        <button
          className={`nav-tab ${activeTab === "playground" ? "active" : ""}`}
          onClick={() => setActiveTab("playground")}
          title="Interactive child instruction playground with voice playback"
        >
          <Sparkles size={16} />
          <span>Interactive Playground</span>
        </button>

        {/* 2. Safety & Anti-Leakage */}
        <button
          className={`nav-tab ${activeTab === "safety" ? "active" : ""}`}
          onClick={() => setActiveTab("safety")}
          title="Test whether instructions leak answers or use complex words"
        >
          <ShieldCheck size={16} />
          <span>Safety & Anti-Leakage</span>
        </button>

        {/* 3. Evaluation & Data Exports */}
        <button
          className={`nav-tab ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          title="Rate adaptations and download CSV / ZIP research bundles"
        >
          <Award size={16} />
          <span>Evaluation &amp; Exports</span>
        </button>

        {/* 4. Results & History */}
        <button
          className={`nav-tab ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
          title="View all stored task outcome records with score evolution history"
        >
          <Clock size={16} />
          <span>Results &amp; History</span>
        </button>

        {/* 4. Technical Lab Dropdown Menu */}
        <div className="dropdown-container" ref={dropdownRef} style={{ position: "relative" }}>
          <button
            className={`nav-tab ${isLabTabActive ? "active" : ""}`}
            onClick={() => setIsLabMenuOpen(!isLabMenuOpen)}
            style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}
          >
            <Layers size={16} />
            <span>Technical Lab</span>
            <ChevronDown size={14} style={{ transform: isLabMenuOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
          </button>

          {isLabMenuOpen && (
            <div className="dropdown-menu">
              <div className="dropdown-header">Advanced Research Modules</div>
              {labTabs.map(tab => {
                const IconComponent = tab.icon;
                const isSelected = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    className={`dropdown-item ${isSelected ? "selected" : ""}`}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setIsLabMenuOpen(false);
                    }}
                  >
                    <div className="item-icon">
                      <IconComponent size={16} />
                    </div>
                    <div className="item-text">
                      <div className="item-title">{tab.label}</div>
                      <div className="item-desc">{tab.desc}</div>
                    </div>
                    {isSelected && <Check size={14} className="item-check" />}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </nav>

      {/* Right-Hand Controls: View Mode Switcher + Backend Status */}
      <div className="navbar-actions">
        {/* Simple vs Researcher View Mode Toggle */}
        <div className="view-mode-toggle">
          <button
            className={`toggle-btn ${viewMode === "simple" ? "active" : ""}`}
            onClick={() => setViewMode("simple")}
            title="Clean, easy-to-use interface without technical clutter"
          >
            ✨ Simple View
          </button>
          <button
            className={`toggle-btn ${viewMode === "researcher" ? "active" : ""}`}
            onClick={() => setViewMode("researcher")}
            title="Unhide raw JSON, acoustic confidence, and educational metrics"
          >
            🔬 Researcher
          </button>
        </div>

        {/* Generation Mode Selector */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
          <select
            className="form-select"
            style={{ padding: "4px 8px", fontSize: "0.78rem", width: "auto" }}
            value={generationMode}
            onChange={(e) => setGenerationMode(e.target.value)}
            title="Choose AI generation engine"
          >
            <option value="rule">Rule (Offline)</option>
            <option value="hybrid">Hybrid (Target)</option>
            <option value="llm">LLM (Simulated)</option>
          </select>
        </div>

        {/* Backend Online Status Pill */}
        <div className={`status-badge ${isBackendHealthy ? "status-healthy" : ""}`} title="FastAPI Health Status">
          <div className="status-indicator" />
          <span>{isBackendHealthy ? "Online" : "Connecting..."}</span>
        </div>
      </div>
    </header>
  );
}
