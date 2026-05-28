import request from "./request";


export function fetchReports(params) {
  return request.get("/reports/", { params });
}

export function generateReport(data) {
  return request.post("/reports/generate/", data);
}

export function getReportTaskStatus(taskId) {
  return request.get("/reports/task_status/", {
    params: { task_id: taskId }
  });
}
