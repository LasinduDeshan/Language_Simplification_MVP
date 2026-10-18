import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles, PlayCircle, ShieldCheck, Award, Layers, Clock,
  ChevronDown, BookOpen, Users, Activity, Sliders, Cpu, Check,
  Menu, X
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
  const [isMoreMenuOpen, setIsMoreMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const labDropdownRef = useRef(null);
  const moreDropdownRef = useRef(null);

  // Close dropdowns on outside click or Escape key (Plan §9, §13)
  useEffect(() => {
    function handleClickOutside(event) {
      if (labDropdownRef.current && !labDropdownRef.current.contains(event.target)) {
        setIsLabMenuOpen(false);
      }
      if (moreDropdownRef.current && !moreDropdownRef.current.contains(event.target)) {
        setIsMoreMenuOpen(false);
      }
    }
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setIsLabMenuOpen(false);
        setIsMoreMenuOpen(false);
        setIsMobileMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const labTabs = [
    { id: "dashboard", label: t("nav.labDashboard"), icon: PlayCircle, desc: t("nav.labDashboardDesc") },
    { id: "tasks", label: t("nav.labTasks"), icon: BookOpen, desc: t("nav.labTasksDesc") },
    { id: "learners", label: t("nav.labLearners"), icon: Users, desc: t("nav.labLearnersDesc") },
    { id: "analysis", label: t("nav.labAnalysis"), icon: Activity, desc: t("nav.labAnalysisDesc") },
    { id: "personalization", label: t("nav.labPersonalization"), icon: Sliders, desc: t("nav.labPersonalizationDesc") },
    { id: "integrations", label: t("nav.labIntegrations"), icon: Cpu, desc: t("nav.labIntegrationsDesc") }
  ];

  const isLabTabActive = labTabs.some(tab => tab.id === activeTab);

  return (
    <header className="navbar">
     

      {/* 2. Main Navigation Region (Desktop & Tablet) (Plan §5, §7) */}
      <nav className="nav-tabs" aria-label={t("nav.brandTitle")}>
        {/* Playground / Activities */}
        <button
          type="button"
          className={`nav-tab ${activeTab === "playground" ? "active" : ""}`}
          onClick={() => setActiveTab("playground")}
          title={t("nav.interactivePlaygroundTitle")}
        >
          <Sparkles size={16} />
          <span>{t("nav.interactivePlayground")}</span>
        </button>

        {/* Safety & Anti-Leakage */}
        <button
          type="button"
          className={`nav-tab ${activeTab === "safety" ? "active" : ""}`}
          onClick={() => setActiveTab("safety")}
          title={t("nav.safetyTitle")}
        >
          <ShieldCheck size={16} />
          <span>{t("nav.safety")}</span>
        </button>

        {/* Evaluation & Data Exports */}
        <button
          type="button"
          className={`nav-tab ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
          title={t("nav.evaluationTitle")}
        >
          <Award size={16} />
          <span>{t("nav.evaluation")}</span>
        </button>

        {/* Results & History */}
        <button
          type="button"
          className={`nav-tab ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
          title={t("nav.resultsTitle")}
        >
          <Clock size={16} />
          <span>{t("nav.results")}</span>
        </button>

        {/* Technical Lab Dropdown Menu */}
        <div className="dropdown-container" ref={labDropdownRef} style={{ position: "relative" }}>
          <button
            type="button"
            className={`nav-tab ${isLabTabActive ? "active" : ""}`}
            onClick={() => setIsLabMenuOpen(!isLabMenuOpen)}
            title={t("nav.technicalLabTitle")}
            aria-expanded={isLabMenuOpen}
            aria-haspopup="true"
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
                    type="button"
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

      {/* 3. Controls Region: Language + View Mode + More/Settings (Plan §5, §8, §9) */}
      <div className="navbar-actions">
        <LanguageSelector id="navbar-language-selector" />

        {/* View Mode Control — Pill-Shaped Segmented Control (Plan §8) */}
        <div className="view-mode-control" role="group" aria-label={t("common.viewMode") || "View mode"}>
          <button
            type="button"
            className={`view-mode-btn ${viewMode === "simple" ? "active" : ""}`}
            onClick={() => setViewMode("simple")}
            title={t("common.simpleViewTitle")}
            aria-pressed={viewMode === "simple"}
          >
            ✨ <span>{t("common.simpleView")}</span>
          </button>
          <button
            type="button"
            className={`view-mode-btn ${viewMode === "researcher" ? "active" : ""}`}
            onClick={() => setViewMode("researcher")}
            title={t("common.researcherViewTitle")}
            aria-pressed={viewMode === "researcher"}
          >
            🔬 <span>{t("common.researcherView")}</span>
          </button>
        </div>

        {/* Secondary Technical Controls (Visible on >1500px Viewports) */}
        <div className="secondary-controls">
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
            <select
              className="form-select"
              style={{ padding: "4px 8px", fontSize: "0.78rem", width: "auto" }}
              value={generationMode}
              onChange={(e) => setGenerationMode(e.target.value)}
              title={t("nav.modelEngine") || "Choose AI generation engine"}
            >
              <option value="rule">{t("nav.generationRule")}</option>
              <option value="hybrid">{t("nav.generationHybrid")}</option>
              <option value="llm">{t("nav.generationLlm")}</option>
            </select>
          </div>

          <div className={`status-badge ${isBackendHealthy ? "status-healthy" : ""}`} title="FastAPI Health Status">
            <div className="status-indicator" />
            <span>{isBackendHealthy ? t("common.online") : t("common.connecting")}</span>
          </div>
        </div>

        {/* More Settings Menu Trigger (Visible on <=1500px Viewports) */}
        <div className="more-menu-container" ref={moreDropdownRef} style={{ position: "relative" }}>
          <button
            type="button"
            className="more-menu-trigger"
            onClick={() => setIsMoreMenuOpen(prev => !prev)}
            title={t("nav.moreMenuTitle")}
            aria-haspopup="true"
            aria-expanded={isMoreMenuOpen}
          >
            <Sliders size={16} />
            <span>{t("nav.moreMenu")}</span>
            <ChevronDown size={14} style={{ transform: isMoreMenuOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }} />
          </button>

          {isMoreMenuOpen && (
            <div className="dropdown-menu more-menu-dropdown">
              <div className="dropdown-header">{t("nav.moreMenuTitle")}</div>

              <div style={{ padding: "0.5rem 0.75rem" }}>
                <label style={{ fontSize: "0.75rem", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
                  {t("nav.modelEngine")}:
                </label>
                <select
                  className="form-select"
                  style={{ width: "100%", padding: "6px 8px", fontSize: "0.82rem" }}
                  value={generationMode}
                  onChange={(e) => setGenerationMode(e.target.value)}
                >
                  <option value="rule">{t("nav.generationRule")}</option>
                  <option value="hybrid">{t("nav.generationHybrid")}</option>
                  <option value="llm">{t("nav.generationLlm")}</option>
                </select>
              </div>

              <div style={{ padding: "0.5rem 0.75rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                  {t("common.status")}:
                </span>
                <div className={`status-badge ${isBackendHealthy ? "status-healthy" : ""}`}>
                  <div className="status-indicator" />
                  <span>{isBackendHealthy ? t("common.online") : t("common.connecting")}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Mobile Menu Trigger (Visible on <=760px Viewports) */}
        <button
          type="button"
          className="mobile-menu-trigger"
          onClick={() => setIsMobileMenuOpen(prev => !prev)}
          aria-label="Toggle Navigation Menu"
        >
          {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Drawer (Visible on <=760px when toggled) */}
      {isMobileMenuOpen && (
        <div className="mobile-drawer">
          <div className="mobile-nav-list">
            <button
              type="button"
              className={`mobile-nav-item ${activeTab === "playground" ? "active" : ""}`}
              onClick={() => { setActiveTab("playground"); setIsMobileMenuOpen(false); }}
            >
              <Sparkles size={18} />
              <span>{t("nav.interactivePlayground")}</span>
            </button>
            <button
              type="button"
              className={`mobile-nav-item ${activeTab === "safety" ? "active" : ""}`}
              onClick={() => { setActiveTab("safety"); setIsMobileMenuOpen(false); }}
            >
              <ShieldCheck size={18} />
              <span>{t("nav.safety")}</span>
            </button>
            <button
              type="button"
              className={`mobile-nav-item ${activeTab === "evaluation" ? "active" : ""}`}
              onClick={() => { setActiveTab("evaluation"); setIsMobileMenuOpen(false); }}
            >
              <Award size={18} />
              <span>{t("nav.evaluation")}</span>
            </button>
            <button
              type="button"
              className={`mobile-nav-item ${activeTab === "results" ? "active" : ""}`}
              onClick={() => { setActiveTab("results"); setIsMobileMenuOpen(false); }}
            >
              <Clock size={18} />
              <span>{t("nav.results")}</span>
            </button>
            <button
              type="button"
              className={`mobile-nav-item ${isLabTabActive ? "active" : ""}`}
              onClick={() => { setActiveTab("dashboard"); setIsMobileMenuOpen(false); }}
            >
              <Layers size={18} />
              <span>{t("nav.technicalLab")}</span>
            </button>
          </div>

          <div className="mobile-drawer-footer">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{t("common.viewMode")}:</span>
              <div className="view-mode-control">
                <button
                  type="button"
                  className={`view-mode-btn ${viewMode === "simple" ? "active" : ""}`}
                  onClick={() => setViewMode("simple")}
                >
                  ✨ {t("common.simpleView")}
                </button>
                <button
                  type="button"
                  className={`view-mode-btn ${viewMode === "researcher" ? "active" : ""}`}
                  onClick={() => setViewMode("researcher")}
                >
                  🔬 {t("common.researcherView")}
                </button>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{t("nav.modelEngine")}:</span>
              <select
                className="form-select"
                style={{ padding: "4px 8px", fontSize: "0.78rem" }}
                value={generationMode}
                onChange={(e) => setGenerationMode(e.target.value)}
              >
                <option value="rule">{t("nav.generationRule")}</option>
                <option value="hybrid">{t("nav.generationHybrid")}</option>
                <option value="llm">{t("nav.generationLlm")}</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
