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

export async function analyzeResponse({ taskId, speechTranscript, speechConfidence = 0.9, learnerAge = 6 }) {
  const res = await fetch(`${API_BASE_URL}/analyze-response`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task_id: taskId,
      speech_transcript: speechTranscript,
      speech_confidence: speechConfidence,
      learner_age: learnerAge
    })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to analyze response");
  }
  return res.json();
}

export async function fetchGrammarTestCases() {
  const res = await fetch(`${API_BASE_URL}/grammar-test-cases`);
  if (!res.ok) throw new Error("Failed to fetch grammar test cases");
  return res.json();
}

export async function adaptInstruction({ taskId, learnerId, attemptNumber = 1, generationMode = "rule" }) {
  const res = await fetch(`${API_BASE_URL}/adapt-instruction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task_id: taskId,
      learner_id: learnerId,
      attempt_number: attemptNumber,
      generation_mode: generationMode
    })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to adapt instruction");
  }
  return res.json();
}

export async function fetchProgressionPreview(taskId, learnerId) {
  const res = await fetch(`${API_BASE_URL}/preview-progression/${taskId}/${learnerId}`);
  if (!res.ok) throw new Error("Failed to fetch progression preview");
  return res.json();
}

export async function validateOutput({ taskId, childInstruction, supportiveMessage = null, targetAttemptNumber = 1, supportLevel = "moderate", learnerId = null }) {
  const res = await fetch(`${API_BASE_URL}/validate-output`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      task_id: taskId,
      child_instruction: childInstruction,
      supportive_message: supportiveMessage,
      target_attempt_number: targetAttemptNumber,
      support_level: supportLevel,
      learner_id: learnerId
    })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to validate output");
  }
  return res.json();
}

export async function fetchRetryState(experimentId) {
  const res = await fetch(`${API_BASE_URL}/retry-state/${experimentId}`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch retry state");
  }
  return res.json();
}

export function getExportUrl(format) {
  return `${API_BASE_URL}/export/experiments/${format}`;
}

