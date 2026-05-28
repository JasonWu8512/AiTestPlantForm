<template>
  <el-container class="app-shell">
    <el-aside :width="isCollapse ? '64px' : '260px'" class="app-sidebar">
      <div class="brand">
        <div class="brand-icon">
          <el-icon size="28"><DataBoard /></el-icon>
        </div>
        <div class="brand-text" v-show="!isCollapse">
          <h1>AI 测试平台</h1>
          <span>智能测试管理</span>
        </div>
      </div>
      <div class="sidebar-divider" v-show="!isCollapse"></div>
      <el-menu
        router
        :default-active="activeMenu"
        :unique-opened="true"
        :collapse="isCollapse"
        :collapse-transition="true"
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <template #title>项目管理</template>
        </el-menu-item>
        <el-menu-item index="/testcases">
          <el-icon><DocumentChecked /></el-icon>
          <template #title>测试用例</template>
        </el-menu-item>
        <el-menu-item index="/testplans">
          <el-icon><Tickets /></el-icon>
          <template #title>测试计划</template>
        </el-menu-item>
        <el-menu-item index="/executions">
          <el-icon><VideoPlay /></el-icon>
          <template #title>测试执行</template>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><TrendCharts /></el-icon>
          <template #title>测试报告</template>
        </el-menu-item>
        <el-menu-item index="/api-tests">
          <el-icon><Connection /></el-icon>
          <template #title>接口测试</template>
        </el-menu-item>
        <el-menu-item index="/ui-tests">
          <el-icon><Monitor /></el-icon>
          <template #title>UI测试</template>
        </el-menu-item>
        <div class="menu-divider" v-show="!isCollapse"></div>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <template #title>通知配置</template>
        </el-menu-item>
      </el-menu>
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon :size="20">
          <DArrowLeft v-if="!isCollapse" />
          <DArrowRight v-else />
        </el-icon>
      </div>
    </el-aside>
    <el-container class="main-container">
      <el-header class="app-header">
        <div class="header-left">
          <div class="breadcrumb-wrapper">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>
        <div class="header-right">
          <el-badge :value="3" class="notification-badge">
            <el-button circle size="small">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          <div class="user-profile">
            <div class="avatar">{{ authStore.user?.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
            <div class="user-info" v-show="!isCollapse">
              <span class="username">{{ authStore.user?.username || "未登录" }}</span>
              <span class="role">管理员</span>
            </div>
            <el-dropdown>
              <el-button text size="small">
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人设置</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted, computed, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Bell, Connection, DataBoard, DocumentChecked, Folder, Monitor, Tickets, TrendCharts, User, VideoPlay, ArrowDown, DArrowLeft, DArrowRight } from "@element-plus/icons-vue";

import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const isCollapse = ref(false);

const activeMenu = computed(() => route.path);

const pageTitles = {
  "/": "仪表板",
  "/users": "用户管理",
  "/projects": "项目管理",
  "/testcases": "测试用例",
  "/testplans": "测试计划",
  "/executions": "测试执行",
  "/reports": "测试报告",
  "/api-tests": "接口测试",
  "/ui-tests": "UI测试",
  "/notifications": "通知配置"
};

const currentPageTitle = computed(() => pageTitles[route.path] || "");

function toggleCollapse() {
  isCollapse.value = !isCollapse.value;
}

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
  background: var(--color-bg);
}

.app-sidebar {
  border-right: none;
  background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width 0.3s ease;
  overflow: hidden;
}

.brand {
  height: 80px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: padding 0.3s ease;
}

.app-sidebar.collapsed .brand {
  padding: 0 8px;
  justify-content: center;
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  flex-shrink: 0;
}

.brand-text {
  overflow: hidden;
  white-space: nowrap;
  transition: opacity 0.3s ease;
}

.brand-text h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.brand-text span {
  font-size: 12px;
  color: var(--color-text-muted);
  display: block;
  line-height: 1.3;
}

.sidebar-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 0 20px;
  transition: opacity 0.3s ease;
}

.sidebar-menu {
  flex: 1;
  border: none;
  padding: 12px 12px 0;
  background: transparent;
  transition: padding 0.3s ease;
}

.sidebar-menu:not(.el-menu--collapse) {
  padding: 12px 12px 0;
}

.sidebar-menu.el-menu--collapse {
  padding: 12px 8px 0;
}

.sidebar-menu .el-menu-item {
  border-radius: 10px;
  margin-bottom: 4px;
  height: 46px;
  line-height: 46px;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.sidebar-menu .el-menu-item:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

.sidebar-menu .el-menu-item .el-icon {
  font-size: 18px;
}

.menu-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 8px 8px 12px;
  transition: opacity 0.3s ease;
}

.collapse-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
  border-top: 1px solid var(--color-border-light);
}

.collapse-btn:hover {
  color: var(--color-primary);
  background: var(--color-bg-tertiary);
}

.main-container {
  background: var(--color-bg);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 70px;
  border-bottom: none;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge :deep(.el-badge__content) {
  background: var(--color-danger);
  border: none;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: var(--color-bg);
  border-radius: 12px;
}

.avatar {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-info) 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  transition: opacity 0.3s ease;
}

.user-info .username {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.user-info .role {
  font-size: 12px;
  color: var(--color-text-muted);
}

.app-main {
  padding: 28px 32px;
  overflow-y: auto;
}
</style>
