const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error("Backend offline");
  return res.json();
}

// ----------------- Activities & Learners -----------------
export async function fetchActivities(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.append("category", filters.category);
  if (filters.subskill) params.append("subskill", filters.subskill);
  if (filters.age) params.append("age", filters.age);
  if (filters.delivery_mode) params.append("delivery_mode", filters.delivery_mode);

  const url = `${API_BASE_URL}/activities${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch activities");
  return res.json();
}

export async function fetchActivityCategories() {
  const res = await fetch(`${API_BASE_URL}/activities/categories`);
  if (!res.ok) throw new Error("Failed to fetch activity categories");
  return res.json();
}

export async function fetchActivityById(activityId) {
  const res = await fetch(`${API_BASE_URL}/activities/${activityId}`);
  if (!res.ok) throw new Error("Failed to fetch activity");
  return res.json();
}

export async function fetchLearners() {
  const res = await fetch(`${API_BASE_URL}/learners`);
  if (!res.ok) throw new Error("Failed to fetch learners");
  return res.json();
}

export async function fetchLearnerById(learnerId) {
  const res = await fetch(`${API_BASE_URL}/learners/${learnerId}`);
  if (!res.ok) throw new Error("Failed to fetch learner");
  return res.json();
}

// ----------------- Activity Session Lifecycle -----------------
export async function createActivitySession(learnerId, taskId, generationMode = "rule", createdBy = "authorized_adult") {
  const res = await fetch(`${API_BASE_URL}/activity-sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      learner_id: learnerId,
      task_id: taskId,
      generation_mode: generationMode,
      created_by: createdBy
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create activity session");
  }
  return res.json();
}

export async function createAttemptInstruction(sessionId, generationMode = null) {
  const res = await fetch(`${API_BASE_URL}/activity-sessions/${sessionId}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ generation_mode: generationMode })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate attempt instruction");
  }
  return res.json();
}

export async function recordAttemptResponse(attemptId, payload) {
  const res = await fetch(`${API_BASE_URL}/attempts/${attemptId}/response`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to record child response");
  }
  return res.json();
}

export async function confirmAttemptResponse(attemptId, confirmed = true, manualTranscript = null) {
  const res = await fetch(`${API_BASE_URL}/attempts/${attemptId}/confirm-response`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed, manual_transcript: manualTranscript })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to confirm response");
  }
  return res.json();
}

export async function analyseAttempt(attemptId) {
  const res = await fetch(`${API_BASE_URL}/attempts/${attemptId}/analyse`, {
    method: "POST"
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to analyse attempt");
  }
  return res.json();
}

export async function reviewAttempt(attemptId, reviewPayload) {
  const res = await fetch(`${API_BASE_URL}/attempts/${attemptId}/review`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reviewPayload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to submit adult review");
  }
  return res.json();
}

export async function transitionAttempt(attemptId) {
  const res = await fetch(`${API_BASE_URL}/attempts/${attemptId}/transition`, {
    method: "POST"
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to transition attempt");
  }
  return res.json();
}

export async function fetchChildSafeView(sessionId, attemptId = null) {
  const url = `${API_BASE_URL}/activity-sessions/${sessionId}/child-view${attemptId ? `?attempt_id=${attemptId}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch child-safe view");
  return res.json();
}

export async function fetchActivitySessionHistory(sessionId) {
  const res = await fetch(`${API_BASE_URL}/activity-sessions/${sessionId}/history`);
  if (!res.ok) throw new Error("Failed to fetch session history");
  return res.json();
}

export async function completeActivitySession(sessionId) {
  const res = await fetch(`${API_BASE_URL}/activity-sessions/${sessionId}/complete`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to complete session");
  return res.json();
}

// ----------------- Legacy Compatibility Methods -----------------
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
  const res = await fetch(`${API_BASE_URL}/integration-payloads/component-1/${experimentId}`);
  if (!res.ok) throw new Error("Failed to fetch Component 1 payload");
  return res.json();
}

export async function fetchComp4Output(experimentId) {
  const res = await fetch(`${API_BASE_URL}/integration-payloads/component-4/${experimentId}`);
  if (!res.ok) throw new Error("Failed to fetch Component 4 payload");
  return res.json();
}

export async function fetchAROutput(experimentId) {
  const res = await fetch(`${API_BASE_URL}/integration-payloads/component-3-ar/${experimentId}`);
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

export async function analyzeResponse(payload) {
  const res = await fetch(`${API_BASE_URL}/analyze-response`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to analyze response");
  return res.json();
}

export async function fetchGrammarTestCases() {
  const res = await fetch(`${API_BASE_URL}/grammar-test-cases`);
  if (!res.ok) throw new Error("Failed to fetch grammar test cases");
  return res.json();
}

export async function adaptInstruction(payload) {
  const res = await fetch(`${API_BASE_URL}/adapt-instruction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to adapt instruction");
  return res.json();
}

export async function fetchProgressionPreview(taskId, learnerId) {
  const res = await fetch(`${API_BASE_URL}/progression-preview/${taskId}/${learnerId}`);
  if (!res.ok) throw new Error("Failed to fetch progression preview");
  return res.json();
}

export async function validateOutput(payload) {
  const res = await fetch(`${API_BASE_URL}/validate-output`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to validate output");
  return res.json();
}

export async function fetchRetryState(experimentId) {
  const res = await fetch(`${API_BASE_URL}/experiments/${experimentId}/history`);
  if (!res.ok) throw new Error("Failed to fetch retry state");
  return res.json();
}

export async function fetchIntegrationEvents(experimentId) {
  const res = await fetch(`${API_BASE_URL}/integration-events/${experimentId}`);
  if (!res.ok) throw new Error("Failed to fetch integration events");
  return res.json();
}

export async function fetchGeneratorComparison(taskId, learnerId, attemptNumber = 1) {
  const res = await fetch(`${API_BASE_URL}/generate-comparison/${taskId}/${learnerId}?attempt_number=${attemptNumber}`);
  if (!res.ok) throw new Error("Failed to fetch generator comparison");
  return res.json();
}

export async function fetchEvaluationStats() {
  const res = await fetch(`${API_BASE_URL}/expert-evaluations/stats`);
  if (!res.ok) throw new Error("Failed to fetch evaluation stats");
  return res.json();
}

export function getExportUrl(format = "csv") {
  return `${API_BASE_URL}/export/experiments/${format}`;
}

export function getExportAdaptationsUrl() {
  return `${API_BASE_URL}/export/adaptations/csv`;
}

export function getExportAttemptsUrl() {
  return `${API_BASE_URL}/export/attempts/csv`;
}

export function getExportEvaluationsUrl() {
  return `${API_BASE_URL}/export/evaluations/csv`;
}

export function getExportResearchBundleZipUrl() {
  return `${API_BASE_URL}/export/research-bundle/zip`;
}

// ----------------- Task Results History -----------------

export async function fetchTaskResults(filters = {}) {
  const params = new URLSearchParams();
  if (filters.learner_code) params.append("learner_code", filters.learner_code);
  if (filters.category) params.append("category", filters.category);
  if (filters.outcome) params.append("outcome", filters.outcome);
  if (filters.limit) params.append("limit", filters.limit);

  const url = `${API_BASE_URL}/results${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch task results");
  return res.json();
}

export async function fetchTaskResultById(resultId) {
  const res = await fetch(`${API_BASE_URL}/results/${resultId}`);
  if (!res.ok) throw new Error("Failed to fetch task result");
  return res.json();
}

export async function deleteTaskResult(resultId) {
  const res = await fetch(`${API_BASE_URL}/results/${resultId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete task result");
}

export async function backfillTaskResults() {
  const res = await fetch(`${API_BASE_URL}/results/backfill`, { method: "POST" });
  if (!res.ok) throw new Error("Backfill failed");
  return res.json();
}
