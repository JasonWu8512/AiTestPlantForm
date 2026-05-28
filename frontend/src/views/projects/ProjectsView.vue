<template>
  <section>
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="openCreateDialog">新增项目</el-button>
    </div>

    <el-table :data="projects" border>
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="项目描述" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="created_by_name" label="创建人" width="140" />
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

    <el-dialog v-model="dialogVisible" :title="editingProject ? '编辑项目' : '新增项目'" width="460px">
      <el-form :model="form" label-position="top">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="启用" value="active" />
            <el-option label="归档" value="archived" />
          </el-select>
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

import { createProject, deleteProject, fetchProjects, updateProject } from "../../api/projects";


const projects = ref([]);
const total = ref(0);
const dialogVisible = ref(false);
const editingProject = ref(null);
const query = reactive({ page: 1, page_size: 20 });
const form = reactive({ name: "", description: "", status: "active" });

onMounted(loadProjects);

async function loadProjects() {
  const data = await fetchProjects(query);
  projects.value = data.results || [];
  total.value = data.count || 0;
}

function openCreateDialog() {
  editingProject.value = null;
  form.name = "";
  form.description = "";
  form.status = "active";
  dialogVisible.value = true;
}

function openEditDialog(row) {
  editingProject.value = row;
  form.name = row.name;
  form.description = row.description;
  form.status = row.status;
  dialogVisible.value = true;
}

async function handleSubmit() {
  if (editingProject.value) {
    await updateProject(editingProject.value.id, form);
  } else {
    await createProject(form);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  loadProjects();
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除项目 ${row.name}？`, "删除确认", { type: "warning" });
  await deleteProject(row.id);
  ElMessage.success("删除成功");
  loadProjects();
}

function handlePageChange(page) {
  query.page = page;
  loadProjects();
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

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
