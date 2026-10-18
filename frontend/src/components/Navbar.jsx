import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles, PlayCircle, ShieldCheck, Award, Layers, Clock,
  ChevronDown, BookOpen, Users, Activity, Sliders, Cpu, Check
} from "lucide-react";
import LanguageSelector from "./language/LanguageSelector";
import { useTranslation } from "../i18n/useTranslation.js";

export default function Navbar({
  activeTab,
  setActiveTab,
  isBackendHealthy,
  generationMode,
  setGenerationMode,
  viewMode,
  setViewMode
}) {
  const { t } = useTranslation();
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
    { id: "dashboard", label: t("nav.labDashboard"), icon: PlayCircle, desc: t("nav.labDashboardDesc") },
    { id: "tasks", label: t("nav.labTasks"), icon: BookOpen, desc: t("nav.labTasksDesc") },
    { id: "learners", label: t("nav.labLearners"), icon: Users, desc: t("nav.labLearnersDesc") },
    { id: "analysis", label: t("nav.labAnalysis"), icon: Activity, desc: t("nav.labAnalysisDesc") },
    { id: "personalization", label: t("nav.labPersonalization"), icon: Sliders, desc: t("nav.labPersonalizationDesc") },
    { id: "integrations", label: t("nav.labIntegrations"), icon: Cpu, desc: t("nav.labIntegrationsDesc") }
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
            <span className="brand-title">{t("nav.brandTitle")}</span>
            <span className="brand-tag">{t("nav.brandTag")}</span>
          </div>
          <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
            {t("nav.brandSubtitle")}
          </p>
        </div>
      </div>

      {/* Streamlined Primary Navigation Tabs */}
      <nav className="nav-tabs">
        {/* 1. Primary: Guided Playground */}
        <button
          className={`nav-tab ${activeTab === "playground" ? "active" : ""}`}
          onClick={() => setActiveTab("playground")}
          title={t("nav.interactivePlaygroundTitle")}
        >
          <Sparkles size={16} />
          <span>{t("nav.interactivePlayground")}</span>
        </button>

        {/* 2. Safety & Anti-Leakage */}
        <button
          className={`nav-tab ${activeTab === "safety" ? "active" : ""}`}
          onClick={() => setActiveTab("safety")}
          title={t("nav.safetyTitle")}
        >
          <ShieldCheck size={16} />
          <span>{t("nav.safety")}</span>
        </button>

        {/* 3. Evaluation & Data Exports */}
        <button
          className={`nav-tab ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          title={t("nav.evaluationTitle")}
        >
          <Award size={16} />
          <span>{t("nav.evaluation")}</span>
        </button>

        {/* 4. Results & History */}
        <button
          className={`nav-tab ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
          title={t("nav.resultsTitle")}
        >
          <Clock size={16} />
          <span>{t("nav.results")}</span>
        </button>

        {/* 5. Technical Lab Dropdown Menu */}
        <div className="dropdown-container" ref={dropdownRef} style={{ position: "relative" }}>
          <button
            className={`nav-tab ${isLabTabActive ? "active" : ""}`}
            onClick={() => setIsLabMenuOpen(!isLabMenuOpen)}
            style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}
          >
            <Layers size={16} />
            <span>{t("nav.technicalLab")}</span>
            <ChevronDown size={14} style={{ transform: isLabMenuOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
          </button>

          {isLabMenuOpen && (
            <div className="dropdown-menu">
              <div className="dropdown-header">{t("nav.advancedModules")}</div>
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

      {/* Right-Hand Controls: Language Selector + View Mode Switcher + Backend Status */}
      <div className="navbar-actions" style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <LanguageSelector id="navbar-language-selector" />
        {/* Simple vs Researcher View Mode Toggle */}
        <div className="view-mode-toggle">
          <button
            className={`toggle-btn ${viewMode === "simple" ? "active" : ""}`}
            onClick={() => setViewMode("simple")}
            title={t("common.simpleViewTitle")}
          >
            ✨ {t("common.simpleView")}
          </button>
          <button
            className={`toggle-btn ${viewMode === "researcher" ? "active" : ""}`}
            onClick={() => setViewMode("researcher")}
            title={t("common.researcherViewTitle")}
          >
            🔬 {t("common.researcherView")}
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
            <option value="rule">{t("nav.generationRule")}</option>
            <option value="hybrid">{t("nav.generationHybrid")}</option>
            <option value="llm">{t("nav.generationLlm")}</option>
          </select>
        </div>

        {/* Backend Online Status Pill */}
        <div className={`status-badge ${isBackendHealthy ? "status-healthy" : ""}`} title="FastAPI Health Status">
          <div className="status-indicator" />
          <span>{isBackendHealthy ? t("common.online") : t("common.connecting")}</span>
        </div>
      </div>
    </header>
  );
}
