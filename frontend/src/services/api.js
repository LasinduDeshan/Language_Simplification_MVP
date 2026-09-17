const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error("Backend offline");
  return res.json();
}

export async function fetchTasks() {
  const res = await fetch(`${API_BASE_URL}/tasks`);
  if (!res.ok) throw new Error("Failed to fetch tasks");
  return res.json();
}

export async function fetchTaskById(taskId) {
  const res = await fetch(`${API_BASE_URL}/tasks/${taskId}`);
  if (!res.ok) throw new Error("Failed to fetch task");
  return res.json();
}

export async function fetchLearners() {
  const res = await fetch(`${API_BASE_URL}/learners`);
  if (!res.ok) throw new Error("Failed to fetch learners");
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE_URL}/scenarios`);
  if (!res.ok) throw new Error("Failed to fetch scenarios");
  return res.json();
}

export async function createExperiment(learnerId, taskId, generationMode = "rule") {
  const res = await fetch(`${API_BASE_URL}/experiments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      learner_id: learnerId,
      task_id: taskId,
      generation_mode: generationMode
    })
  });
  if (!res.ok) throw new Error("Failed to create experiment");
  return res.json();
}

export async function generateInitialAdaptation(experimentId) {
  const res = await fetch(`${API_BASE_URL}/experiments/${experimentId}/initial-adaptation`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to generate initial adaptation");
  return res.json();
}

export async function recordAttempt(experimentId, attemptPayload) {
  const res = await fetch(`${API_BASE_URL}/experiments/${experimentId}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(attemptPayload)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to record attempt");
  }
  return res.json();
}

export async function fetchExperimentHistory(experimentId) {
  const res = await fetch(`${API_BASE_URL}/experiments/${experimentId}/history`);
  if (!res.ok) throw new Error("Failed to fetch experiment history");
  return res.json();
}

export async function fetchComp1Output(experimentId) {
  const res = await fetch(`${API_BASE_URL}/output/component-1/${experimentId}`);
  if (!res.ok) throw new Error("Failed to fetch Component 1 payload");
  return res.json();
}

export async function fetchComp4Output(experimentId) {
  const res = await fetch(`${API_BASE_URL}/output/component-4/${experimentId}`);
  if (!res.ok) throw new Error("Failed to fetch Component 4 payload");
  return res.json();
}

export async function fetchAROutput(experimentId) {
  const res = await fetch(`${API_BASE_URL}/output/ar/${experimentId}`);
  if (!res.ok) throw new Error("Failed to fetch AR payload");
  return res.json();
}

export async function submitExpertEvaluation(evalData) {
  const res = await fetch(`${API_BASE_URL}/expert-evaluations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(evalData)
  });
  if (!res.ok) throw new Error("Failed to submit expert evaluation");
  return res.json();
}

export function getExportUrl(format) {
  return `${API_BASE_URL}/export/experiments/${format}`;
}
