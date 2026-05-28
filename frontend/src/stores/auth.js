import { defineStore } from "pinia";

import { login, getCurrentUser, logout as requestLogout, refreshToken } from "../api/auth";


export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem("access_token") || "",
    refreshToken: localStorage.getItem("refresh_token") || "",
    user: null,
    role: "viewer",
    refreshTimer: null
  }),
  actions: {
    async login(username, password) {
      const tokenData = await login({ username, password });
      this.accessToken = tokenData.access;
      this.refreshToken = tokenData.refresh;
      localStorage.setItem("access_token", tokenData.access);
      localStorage.setItem("refresh_token", tokenData.refresh);
      await this.loadCurrentUser();
      this.startRefreshTimer();
    },
    async loadCurrentUser() {
      if (!this.accessToken) {
        return;
      }
      const userData = await getCurrentUser();
      this.user = userData;
      this.role = userData.role || "viewer";
    },
    async logout() {
      if (this.refreshToken) {
        await requestLogout(this.refreshToken);
      }
      this.stopRefreshTimer();
      this.accessToken = "";
      this.refreshToken = "";
      this.user = null;
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    },
    async refresh() {
      if (!this.refreshToken) {
        await this.logout();
        return false;
      }
      try {
        const tokenData = await refreshToken(this.refreshToken);
        this.accessToken = tokenData.access;
        localStorage.setItem("access_token", tokenData.access);
        this.startRefreshTimer();
        return true;
      } catch {
        await this.logout();
        return false;
      }
    },
    startRefreshTimer() {
      this.stopRefreshTimer();
      const expiresIn = 25 * 60 * 1000;
      this.refreshTimer = setTimeout(() => {
        this.refresh();
      }, expiresIn);
    },
    stopRefreshTimer() {
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer);
        this.refreshTimer = null;
      }
    }
  }
});
