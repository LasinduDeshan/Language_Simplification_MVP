import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import ScenarioDashboard from "./components/ScenarioDashboard";
import TaskBrowser from "./components/TaskBrowser";
import LearnerBrowser from "./components/LearnerBrowser";
import { checkHealth, fetchTasks, fetchLearners, fetchScenarios } from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [generationMode, setGenerationMode] = useState("rule");
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  const [tasks, setTasks] = useState([]);
  const [learners, setLearners] = useState([]);
  const [scenarios, setScenarios] = useState([]);

  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedLearner, setSelectedLearner] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initData() {
      try {
        await checkHealth();
        setIsBackendHealthy(true);

        const [tList, lList, sList] = await Promise.all([
          fetchTasks(),
          fetchLearners(),
          fetchScenarios()
        ]);

        setTasks(tList);
        setLearners(lList);
        setScenarios(sList);

        if (tList.length > 0) setSelectedTask(tList[0]);
        if (lList.length > 0) setSelectedLearner(lList[0]);
      } catch (err) {
        console.warn("Backend not available yet or loading error:", err);
        setIsBackendHealthy(false);
      } finally {
        setLoading(false);
      }
    }
    initData();
  }, []);

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendHealthy={isBackendHealthy}
        generationMode={generationMode}
        setGenerationMode={setGenerationMode}
      />

      <main className="main-content">
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem" }}>
            <p style={{ color: "var(--text-secondary)", fontSize: "1.1rem" }}>
              Initializing Research Environment...
            </p>
          </div>
        ) : (
          <>
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

            {activeTab === "tasks" && (
              <TaskBrowser
                tasks={tasks}
                onSelectTask={(task) => {
                  setSelectedTask(task);
                  setActiveTab("dashboard");
                }}
              />
            )}

            {activeTab === "learners" && (
              <LearnerBrowser
                learners={learners}
                onSelectLearner={(learner) => {
                  setSelectedLearner(learner);
                  setActiveTab("dashboard");
                }}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}
