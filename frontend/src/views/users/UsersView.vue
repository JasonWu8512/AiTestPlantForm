<template>
  <section>
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
    </div>

    <el-form :inline="true" class="toolbar" @submit.prevent>
      <el-form-item label="关键词">
        <el-input v-model="query.keyword" placeholder="用户名" clearable @keyup.enter="loadUsers" />
      </el-form-item>
      <el-form-item>
        <el-button @click="loadUsers">搜索</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="users" border>
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column prop="is_active" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? "启用" : "禁用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-button text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="pagination"
      layout="prev, pager, next"
      :total="total"
      :page-size="query.page_size"
      @current-change="handlePageChange"
    />

    <el-dialog v-model="dialogVisible" :title="editingUser ? '编辑用户' : '新增用户'" width="420px">
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="Boolean(editingUser)" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="管理员" value="admin" />
            <el-option label="测试人员" value="tester" />
            <el-option label="只读用户" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { createUser, deleteUser, fetchUsers, updateUser } from "../../api/users";


const users = ref([]);
const total = ref(0);
const dialogVisible = ref(false);
const editingUser = ref(null);
const query = reactive({
  keyword: "",
  page: 1,
  page_size: 20
});
const form = reactive({
  username: "",
  password: "",
  email: "",
  role: "viewer",
  is_active: true
});

onMounted(loadUsers);

async function loadUsers() {
  const data = await fetchUsers(query);
  users.value = data.results || [];
  total.value = data.count || 0;
}

function resetForm() {
  form.username = "";
  form.password = "";
  form.email = "";
  form.role = "viewer";
  form.is_active = true;
}

function openCreateDialog() {
  editingUser.value = null;
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row) {
  editingUser.value = row;
  form.username = row.username;
  form.password = "";
  form.email = row.email;
  form.role = row.role || "viewer";
  form.is_active = row.is_active;
  dialogVisible.value = true;
}

async function handleSubmit() {
  const payload = { ...form };
  if (!payload.password) {
    delete payload.password;
  }
  if (editingUser.value) {
    await updateUser(editingUser.value.id, payload);
  } else {
    await createUser(payload);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  loadUsers();
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用户 ${row.username}？`, "删除确认", { type: "warning" });
  await deleteUser(row.id);
  ElMessage.success("删除成功");
  loadUsers();
}

function handlePageChange(page) {
  query.page = page;
  loadUsers();
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

h2 {
  margin: 0;
  color: #111827;
  font-size: 22px;
}

.toolbar {
  margin-bottom: 12px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
