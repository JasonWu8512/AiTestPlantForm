<template>
  <el-container class="app-shell">
    <el-aside width="220px" class="app-sidebar">
      <div class="brand">AI 测试平台</div>
      <el-menu router default-active="/">
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/testcases">
          <el-icon><DocumentChecked /></el-icon>
          <span>测试用例</span>
        </el-menu-item>
        <el-menu-item index="/testplans">
          <el-icon><Tickets /></el-icon>
          <span>测试计划</span>
        </el-menu-item>
        <el-menu-item index="/executions">
          <el-icon><VideoPlay /></el-icon>
          <span>测试执行</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><TrendCharts /></el-icon>
          <span>测试报告</span>
        </el-menu-item>
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <span>通知配置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <span>{{ authStore.user?.username || "未登录" }}</span>
        <el-button text @click="handleLogout">退出</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { Bell, DataBoard, DocumentChecked, Folder, Tickets, TrendCharts, User, VideoPlay } from "@element-plus/icons-vue";

import { useAuthStore } from "../../stores/auth";


const router = useRouter();
const authStore = useAuthStore();

onMounted(() => {
  authStore.loadCurrentUser();
  if (authStore.accessToken) {
    authStore.startRefreshTimer();
  }
});

function handleLogout() {
  authStore.logout().finally(() => {
    router.push({ name: "login" });
  });
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-sidebar {
  border-right: 1px solid #e5e7eb;
  background: #ffffff;
}

.brand {
  height: 56px;
  padding: 0 20px;
  color: #111827;
  font-size: 18px;
  font-weight: 700;
  line-height: 56px;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
}
</style>
