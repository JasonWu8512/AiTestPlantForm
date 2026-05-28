import request from "./request";


export function fetchTestPlans(params) {
  return request.get("/testplans/", { params });
}

export function createTestPlan(data) {
  return request.post("/testplans/", data);
}

export function updateTestPlan(id, data) {
  return request.put(`/testplans/${id}/`, data);
}

export function addCaseToPlan(planId, data) {
  return request.post(`/testplans/${planId}/cases/`, data);
}

export function removeCaseFromPlan(planId, caseId) {
  return request.delete(`/testplans/${planId}/cases/${caseId}/`);
}

export function reorderCases(planId, cases) {
  return request.post(`/testplans/${planId}/cases/reorder/`, { cases });
}
