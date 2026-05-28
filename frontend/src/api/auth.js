import request from "./request";


export function login(data) {
  return request.post("/auth/login/", data);
}

export function getCurrentUser() {
  return request.get("/auth/me/");
}

export function logout(refresh) {
  return request.post("/auth/logout/", { refresh });
}

export function refreshToken(refresh) {
  return request.post("/auth/refresh/", { refresh });
}
