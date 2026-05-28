import request from "./request";


export function fetchExecutions(params) {
  return request.get("/executions/", { params });
}

export function createExecution(data) {
  return request.post("/executions/", data);
}

export function startExecution(id) {
  return request.post(`/executions/${id}/start/`);
}

export function cancelExecution(id) {
  return request.post(`/executions/${id}/cancel/`);
}

export function submitExecutionResult(id, data) {
  return request.post(`/executions/${id}/results/`, data);
}
