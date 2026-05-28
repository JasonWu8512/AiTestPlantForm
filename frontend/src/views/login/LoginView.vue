<template>
  <main class="login-page">
    <section class="login-panel">
      <h1>AI 测试平台</h1>
      <el-form :model="form" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" autocomplete="current-password" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" native-type="submit" class="login-button">
          登录
        </el-button>
      </el-form>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../../stores/auth";


const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
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
  background: #eef2f7;
}

.login-panel {
  width: min(420px, calc(100vw - 32px));
  padding: 28px;
  border: 1px solid #dbe2ea;
  border-radius: 8px;
  background: #ffffff;
}

h1 {
  margin: 0 0 24px;
  color: #111827;
  font-size: 24px;
}

.login-button {
  width: 100%;
}
</style>
