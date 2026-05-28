import request from "./request";


export function fetchProjects(params) {
  return request.get("/projects/", { params });
}

export function createProject(data) {
  return request.post("/projects/", data);
}

export function updateProject(id, data) {
  return request.put(`/projects/${id}/`, data);
}

export function deleteProject(id) {
  return request.delete(`/projects/${id}/`);
}
