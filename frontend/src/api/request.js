import axios from "axios";
import { ElMessage } from "element-plus";


const request = axios.create({
  baseURL: "/api",
  timeout: 10000
});

request.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => {
    // 如果响应是统一的 {code, message, data} 格式，返回 data
    if (response.data && response.data.code !== undefined) {
      return response.data.data ?? response.data;
    }
    // 否则直接返回响应数据（如列表分页）
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.message || error.response?.data?.detail || "请求失败，请稍后重试";
    ElMessage.error(String(message));
    return Promise.reject(error);
  }
);

export default request;
