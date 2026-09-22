import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import GuidedPlayground from "./components/GuidedPlayground";
import ScenarioDashboard from "./components/ScenarioDashboard";
import TaskBrowser from "./components/TaskBrowser";
import LearnerBrowser from "./components/LearnerBrowser";
import AnalysisViewer from "./components/AnalysisViewer";
import AdaptiveInstructionView from "./components/AdaptiveInstructionView";
import SafetyRetryView from "./components/SafetyRetryView";
import IntegrationExplorer from "./components/IntegrationExplorer";
import EvaluationHub from "./components/EvaluationHub";
import TaskResultsHistoryView from "./components/TaskResultsHistoryView";
import { checkHealth, fetchTasks, fetchLearners, fetchScenarios } from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("playground");
  const [viewMode, setViewMode] = useState("simple"); // 'simple' | 'researcher'
  const [generationMode, setGenerationMode] = useState("rule");
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  const [tasks, setTasks] = useState([]);
  const [learners, setLearners] = useState([]);
  const [scenarios, setScenarios] = useState([]);

  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedLearner, setSelectedLearner] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    let retryTimer = null;

    async function initData() {
      try {
        await checkHealth();
        if (!isMounted) return;
        setIsBackendHealthy(true);

        const [tList, lList, sList] = await Promise.all([
          fetchTasks(),
          fetchLearners(),
          fetchScenarios()
        ]);

        if (!isMounted) return;
        setTasks(tList);
        setLearners(lList);
        setScenarios(sList);

        if (tList.length > 0) setSelectedTask(prev => prev || tList[0]);
        if (lList.length > 0) setSelectedLearner(prev => prev || lList[0]);
        setLoading(false);
      } catch (err) {
        console.warn("Backend not available yet or loading error:", err);
        if (isMounted) {
          setIsBackendHealthy(false);
          setLoading(false);
          // Automatically retry every 2.5 seconds until backend connects
          retryTimer = setTimeout(initData, 2500);
        }
      }
    }

    initData();

    return () => {
      isMounted = false;
      if (retryTimer) clearTimeout(retryTimer);
    };
  }, []);

  const handleRefreshLearners = async () => {
    try {
      const updated = await fetchLearners();
      if (updated && updated.length > 0) {
        setLearners(updated);
        setSelectedLearner(prev => {
          if (!prev) return updated[0];
          return updated.find(l => l.id === prev.id || l.learner_code === prev.learner_code) || updated[0];
        });
      }
      return updated;
    } catch (err) {
      console.warn("Failed to refresh learners in App:", err);
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendHealthy={isBackendHealthy}
        generationMode={generationMode}
        setGenerationMode={setGenerationMode}
        viewMode={viewMode}
        setViewMode={setViewMode}
      />

      <main className="main-content">
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem" }}>
            <p style={{ color: "var(--text-secondary)", fontSize: "1.1rem" }}>
              Initializing Learning Environment...
            </p>
          </div>
        ) : (
          <>
            {/* 1. Primary User-Friendly Interactive Playground (Default) */}
            {activeTab === "playground" && (
              <GuidedPlayground
                tasks={tasks}
                learners={learners}
                scenarios={scenarios}
                selectedTask={selectedTask}
                setSelectedTask={setSelectedTask}
                selectedLearner={selectedLearner}
                setSelectedLearner={setSelectedLearner}
                generationMode={generationMode}
                viewMode={viewMode}
                onLearnerUpdated={handleRefreshLearners}
              />
            )}

            {/* 2. Safety & Anti-Leakage Sandbox */}
            {activeTab === "safety" && (
              <SafetyRetryView
                tasks={tasks}
                learners={learners}
                selectedTask={selectedTask}
                selectedLearner={selectedLearner}
              />
            )}

            {/* 3. Evaluation & Exports */}
            {activeTab === "evaluation" && (
              <EvaluationHub
                tasks={tasks}
                learners={learners}
              />
            )}

            {/* 4. Technical Lab Tabs */}
            {activeTab === "dashboard" && (
              <ScenarioDashboard
                tasks={tasks}
                learners={learners}
                scenarios={scenarios}
                selectedTask={selectedTask}
                setSelectedTask={setSelectedTask}
                selectedLearner={selectedLearner}
                setSelectedLearner={setSelectedLearner}
                generationMode={generationMode}
              />
            )}

            {activeTab === "integrations" && (
              <IntegrationExplorer
                tasks={tasks}
                learners={learners}
                selectedTask={selectedTask}
                setSelectedTask={setSelectedTask}
                selectedLearner={selectedLearner}
                setSelectedLearner={setSelectedLearner}
              />
            )}

            {activeTab === "personalization" && (
              <AdaptiveInstructionView
                tasks={tasks}
                learners={learners}
                selectedTask={selectedTask}
                selectedLearner={selectedLearner}
              />
            )}

            {activeTab === "analysis" && (
              <AnalysisViewer
                tasks={tasks}
                learners={learners}
                selectedTask={selectedTask}
              />
            )}

            {activeTab === "tasks" && (
              <TaskBrowser
                tasks={tasks}
                onSelectTask={(task) => {
                  setSelectedTask(task);
                  setActiveTab("playground");
                }}
              />
            )}

            {activeTab === "learners" && (
              <LearnerBrowser
                learners={learners}
                onSelectLearner={(learner) => {
                  setSelectedLearner(learner);
                  setActiveTab("playground");
                }}
              />
            )}

            {/* Results & History View */}
            {activeTab === "results" && (
              <TaskResultsHistoryView
                onNavigateToPlayground={() => setActiveTab("playground")}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}
