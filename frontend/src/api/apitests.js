import request from "./request";


export function fetchApiTests(params) {
  return request.get("/api-tests/", { params });
}

export function createApiTest(data) {
  return request.post("/api-tests/", data);
}

export function updateApiTest(id, data) {
  return request.put(`/api-tests/${id}/`, data);
}

export function deleteApiTest(id) {
  return request.delete(`/api-tests/${id}/`);
}

export function executeApiTests(data) {
  return request.post("/api-tests/execute/", data);
}

export function fetchApiTestExecutions(params) {
  return request.get("/api-test-executions/", { params });
}

export function fetchApiTestExecutionResults(executionId) {
  return request.get(`/api-test-executions/${executionId}/results/`);
}

export function cancelApiTestExecution(executionId) {
  return request.post(`/api-test-executions/${executionId}/cancel/`);
}
