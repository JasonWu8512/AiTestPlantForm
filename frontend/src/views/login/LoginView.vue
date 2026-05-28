<template>
  <main class="login-page">
    <div class="login-content">
      <div class="hero-section">
        <div class="hero-content">
          <div class="hero-icon">
            <el-icon size="48"><DataBoard /></el-icon>
          </div>
          <h1>AI 测试平台</h1>
          <p>智能高效的测试管理解决方案<br />助力团队提升产品质量</p>
          <div class="feature-list">
            <div class="feature-item">
              <el-icon><SuccessFilled /></el-icon>
              <span>自动化测试管理</span>
            </div>
            <div class="feature-item">
              <el-icon><SuccessFilled /></el-icon>
              <span>实时报告与分析</span>
            </div>
            <div class="feature-item">
              <el-icon><SuccessFilled /></el-icon>
              <span>多项目协同工作</span>
            </div>
          </div>
        </div>
        <div class="hero-decoration">
          <div class="decoration-circle circle-1"></div>
          <div class="decoration-circle circle-2"></div>
          <div class="decoration-circle circle-3"></div>
        </div>
      </div>
      <section class="login-panel">
        <div class="panel-header">
          <h2>欢迎回来</h2>
          <p>请登录您的账户继续</p>
        </div>
        <el-form :model="form" label-position="top" @submit.prevent="handleLogin" class="login-form">
          <el-form-item label="用户名">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
            </div>
          </el-form-item>
          <el-form-item label="密码">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="current-password" show-password />
            </div>
          </el-form-item>
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <a href="#" class="forgot-password">忘记密码？</a>
          </div>
          <el-button type="primary" :loading="loading" native-type="submit" class="login-button">
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form>
        <div class="panel-footer">
          <span>还没有账户？</span>
          <a href="#" class="signup-link">联系管理员</a>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { DataBoard, User, Lock, SuccessFilled } from "@element-plus/icons-vue";

import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const rememberMe = ref(false);
const form = reactive({
  username: "",
  password: ""
});

async function handleLogin() {
  loading.value = true;
  try {
    await authStore.login(form.username, form.password);
    router.push({ name: "dashboard" });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px;
  position: relative;
  overflow: hidden;
}

.login-page::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(30px, -30px);
  }
}

.login-content {
  display: flex;
  max-width: 1100px;
  width: 100%;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.hero-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  margin-bottom: 28px;
  backdrop-filter: blur(10px);
}

.hero-section h1 {
  margin: 0 0 16px;
  color: #ffffff;
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
}

.hero-section p {
  margin: 0 0 36px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 16px;
  line-height: 1.6;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #ffffff;
  font-size: 15px;
}

.feature-item .el-icon {
  font-size: 20px;
  color: #a7f3d0;
}

.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -100px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: 50px;
  left: -50px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 40%;
  right: 10%;
}

.login-panel {
  width: 440px;
  padding: 56px 48px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.panel-header {
  margin-bottom: 36px;
}

.panel-header h2 {
  margin: 0 0 8px;
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
}

.panel-header p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
}

.login-form {
  margin-bottom: 24px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: #94a3b8;
  font-size: 18px;
  z-index: 1;
}

.input-wrapper :deep(.el-input__wrapper) {
  padding-left: 44px;
  box-shadow: 0 0 0 1px var(--color-border) inset;
  transition: all var(--transition-fast);
}

.input-wrapper :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--color-primary) inset, 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  font-size: 14px;
}

.forgot-password {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.forgot-password:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.login-button {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border: none;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
  transition: all var(--transition-fast);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.panel-footer {
  text-align: center;
  font-size: 14px;
  color: #64748b;
}

.signup-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
  transition: color var(--transition-fast);
}

.signup-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}
</style>
