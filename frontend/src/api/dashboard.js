import request from "./request";


export function fetchDashboardSummary() {
  return request.get("/dashboard/summary/");
}

export function fetchDashboardTrends() {
  return request.get("/dashboard/trends/");
}

export function fetchRecentExecutions() {
  return request.get("/dashboard/recent-executions/");
}
