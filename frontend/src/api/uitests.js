import request from "./request";


export function fetchUITests(params) {
  return request.get("/ui-tests/", { params });
}

export function createUITest(data) {
  return request.post("/ui-tests/", data);
}

export function updateUITest(id, data) {
  return request.put(`/ui-tests/${id}/`, data);
}

export function deleteUITest(id) {
  return request.delete(`/ui-tests/${id}/`);
}

export function executeUITests(data) {
  return request.post("/ui-tests/execute/", data);
}

export function fetchUITestExecutions(params) {
  return request.get("/ui-test-executions/", { params });
}

export function fetchUITestExecutionResults(executionId) {
  return request.get(`/ui-test-executions/${executionId}/results/`);
}

export function cancelUITestExecution(executionId) {
  return request.post(`/ui-test-executions/${executionId}/cancel/`);
}
