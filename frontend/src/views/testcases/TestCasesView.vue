<template>
  <section>
    <div class="page-header">
      <h2>测试用例</h2>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">新增用例</el-button>
        <el-button @click="showExportModal = true">导出用例</el-button>
        <el-button @click="showImportModal = true">导入用例</el-button>
      </div>
    </div>

    <el-form :inline="true" class="toolbar" @submit.prevent>
      <el-form-item label="项目">
        <el-select v-model="query.project" clearable placeholder="全部项目" @change="loadTestCases">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="优先级">
        <el-select v-model="query.priority" clearable placeholder="全部" @change="loadTestCases">
          <el-option label="P0" value="P0" />
          <el-option label="P1" value="P1" />
          <el-option label="P2" value="P2" />
          <el-option label="P3" value="P3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" clearable placeholder="全部" @change="loadTestCases">
          <el-option label="草稿" value="draft" />
          <el-option label="启用" value="active" />
          <el-option label="归档" value="archived" />
        </el-select>
      </el-form-item>
    </el-form>

    <el-table :data="testcases" border>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="project_name" label="项目" width="160" />
      <el-table-column prop="priority" label="优先级" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
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

    <el-dialog v-model="dialogVisible" :title="editingTestCase ? '编辑用例' : '新增用例'" width="640px">
      <el-form :model="form" label-position="top">
        <el-form-item label="所属项目">
          <el-select v-model="form.project">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="form.precondition" type="textarea" />
        </el-form-item>
        <el-form-item label="步骤">
          <div class="steps">
            <div v-for="(step, index) in form.steps" :key="index" class="step-row">
              <el-input v-model="step.action" :placeholder="`步骤 ${index + 1}`" />
              <el-button @click="removeStep(index)">删除</el-button>
            </div>
            <el-button @click="addStep">添加步骤</el-button>
          </div>
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="form.expected_result" type="textarea" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="草稿" value="draft" />
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

    <ImportExportModal
      :visible="showExportModal"
      type="export"
      :project-id="query.project"
      @close="showExportModal = false"
    />

    <ImportExportModal
      :visible="showImportModal"
      type="import"
      :project-id="query.project"
      :projects="projects"
      @close="showImportModal = false"
      @success="handleImportSuccess"
    />
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import ImportExportModal from "../../components/ImportExportModal.vue";
import { fetchProjects } from "../../api/projects";
import { createTestCase, deleteTestCase, fetchTestCases, updateTestCase } from "../../api/testcases";


const projects = ref([]);
const testcases = ref([]);
const total = ref(0);
const dialogVisible = ref(false);
const editingTestCase = ref(null);
const showExportModal = ref(false);
const showImportModal = ref(false);
const query = reactive({ project: "", priority: "", status: "", page: 1, page_size: 20 });
const form = reactive({
  project: "",
  title: "",
  description: "",
  precondition: "",
  steps: [],
  expected_result: "",
  priority: "P2",
  status: "draft"
});

onMounted(async () => {
  await loadProjects();
  await loadTestCases();
});

async function loadProjects() {
  const data = await fetchProjects({ page_size: 100 });
  projects.value = data.results || [];
}

async function loadTestCases() {
  const params = { ...query };
  Object.keys(params).forEach((key) => {
    if (params[key] === "") {
      delete params[key];
    }
  });
  const data = await fetchTestCases(params);
  testcases.value = data.results || [];
  total.value = data.count || 0;
}

function resetForm() {
  form.project = projects.value[0]?.id || "";
  form.title = "";
  form.description = "";
  form.precondition = "";
  form.steps = [];
  form.expected_result = "";
  form.priority = "P2";
  form.status = "draft";
}

function openCreateDialog() {
  editingTestCase.value = null;
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row) {
  editingTestCase.value = row;
  form.project = row.project;
  form.title = row.title;
  form.description = row.description;
  form.precondition = row.precondition;
  form.steps = Array.isArray(row.steps) ? [...row.steps] : [];
  form.expected_result = row.expected_result;
  form.priority = row.priority;
  form.status = row.status;
  dialogVisible.value = true;
}

function addStep() {
  form.steps.push({ action: "" });
}

function removeStep(index) {
  form.steps.splice(index, 1);
}

async function handleSubmit() {
  if (editingTestCase.value) {
    await updateTestCase(editingTestCase.value.id, form);
  } else {
    await createTestCase(form);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  loadTestCases();
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用例 ${row.title}？`, "删除确认", { type: "warning" });
  await deleteTestCase(row.id);
  ElMessage.success("删除成功");
  loadTestCases();
}

function handlePageChange(page) {
  query.page = page;
  loadTestCases();
}

function handleImportSuccess() {
  showImportModal.value = false;
  loadTestCases();
  ElMessage.success("导入成功");
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

.header-actions {
  display: flex;
  gap: 8px;
}

.toolbar {
  margin-bottom: 12px;
}

.toolbar :deep(.el-select) {
  width: 180px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}

.steps {
  display: grid;
  gap: 8px;
  width: 100%;
}

.step-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}
</style>
