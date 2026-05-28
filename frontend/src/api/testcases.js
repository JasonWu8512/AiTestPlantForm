import request from "./request";


export function fetchTestCases(params) {
  return request.get("/testcases/", { params });
}

export function createTestCase(data) {
  return request.post("/testcases/", data);
}

export function updateTestCase(id, data) {
  return request.put(`/testcases/${id}/`, data);
}

export function deleteTestCase(id) {
  return request.delete(`/testcases/${id}/`);
}

export function exportTestCasesExcel(projectId) {
  return request.get(`/testcases/export_excel/`, {
    params: { project: projectId },
    responseType: "blob"
  });
}

export function exportTestCasesJson(projectId) {
  return request.get(`/testcases/export_json/`, {
    params: { project: projectId }
  });
}

export function importTestCasesExcel(formData) {
  return request.post("/testcases/import_excel/", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
}

export function importTestCasesJson(data) {
  return request.post("/testcases/import_json/", data);
}
