<template>
  <section>
    <div class="page-header">
      <h2>UI自动化测试</h2>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">新增用例</el-button>
        <el-button type="success" @click="openExecuteDialog">执行测试</el-button>
      </div>
    </div>

    <el-form :inline="true" class="toolbar" @submit.prevent>
      <el-form-item label="项目">
        <el-select v-model="query.project" clearable placeholder="全部项目" @change="loadUITests">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="浏览器">
        <el-select v-model="query.browser" clearable placeholder="全部" @change="loadUITests">
          <el-option label="Chromium" value="chromium" />
          <el-option label="Firefox" value="firefox" />
          <el-option label="WebKit" value="webkit" />
        </el-select>
      </el-form-item>
      <el-form-item label="优先级">
        <el-select v-model="query.priority" clearable placeholder="全部" @change="loadUITests">
          <el-option label="P0" value="P0" />
          <el-option label="P1" value="P1" />
          <el-option label="P2" value="P2" />
          <el-option label="P3" value="P3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" clearable placeholder="全部" @change="loadUITests">
          <el-option label="草稿" value="draft" />
          <el-option label="启用" value="active" />
          <el-option label="归档" value="archived" />
        </el-select>
      </el-form-item>
    </el-form>

    <el-table :data="uiTests" border stripe>
      <el-table-column prop="name" label="用例名称" min-width="150" />
      <el-table-column prop="browser" label="浏览器" width="100">
        <template #default="{ row }">
          <el-tag :type="getBrowserType(row.browser)" size="small">{{ row.browser }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="base_url" label="基础URL" min-width="180" show-overflow-tooltip />
      <el-table-column prop="project_name" label="项目" width="120" />
      <el-table-column prop="priority" label="优先级" width="80" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : row.status === 'draft' ? '草稿' : '归档' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-button text type="success" @click="handleExecuteSingle(row)">执行</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editingTest ? '编辑UI用例' : '新增UI用例'" width="800px">
      <el-form :model="form" label-position="top">
        <el-form-item label="所属项目">
          <el-select v-model="form.project">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用例名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="浏览器">
              <el-select v-model="form.browser">
                <el-option label="Chromium" value="chromium" />
                <el-option label="Firefox" value="firefox" />
                <el-option label="WebKit" value="webkit" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="无头模式">
              <el-switch v-model="form.headless" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="超时(ms)">
              <el-input-number v-model="form.timeout" :min="1000" :max="300000" :step="1000" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="视口宽度">
              <el-input-number v-model="form.viewport_width" :min="320" :max="3840" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="视口高度">
              <el-input-number v-model="form.viewport_height" :min="240" :max="2160" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="基础URL">
          <el-input v-model="form.base_url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="测试步骤">
          <div class="steps-container">
            <div v-for="(step, index) in form.steps" :key="index" class="step-item">
              <div class="step-header">
                <span class="step-index">步骤 {{ index + 1 }}</span>
                <el-select v-model="step.type" placeholder="操作类型" size="small" style="width: 140px;">
                  <el-option label="导航" value="navigate" />
                  <el-option label="点击" value="click" />
                  <el-option label="输入" value="fill" />
                  <el-option label="逐字输入" value="type" />
                  <el-option label="选择选项" value="select_option" />
                  <el-option label="勾选" value="check" />
                  <el-option label="取消勾选" value="uncheck" />
                  <el-option label="悬停" value="hover" />
                  <el-option label="等待" value="wait" />
                  <el-option label="等待元素" value="wait_for" />
                  <el-option label="断言文本" value="assert_text" />
                  <el-option label="断言URL" value="assert_url" />
                  <el-option label="断言标题" value="assert_title" />
                  <el-option label="断言存在" value="assert_exists" />
                  <el-option label="断言不存在" value="assert_not_exists" />
                  <el-option label="滚动" value="scroll_to" />
                  <el-option label="上传" value="upload" />
                  <el-option label="拖拽" value="drag_drop" />
                </el-select>
                <el-button type="danger" size="small" circle @click="removeStep(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <div class="step-content">
                <el-input v-if="step.type && needUrl.includes(step.type)" v-model="step.url" placeholder="URL" size="small" />
                <el-input v-if="step.type && needSelector.includes(step.type)" v-model="step.selector" placeholder="选择器 (如: #id, .class)" size="small" />
                <el-input v-if="step.type && needValue.includes(step.type)" v-model="step.value" placeholder="值" size="small" />
                <el-input v-if="step.type && needText.includes(step.type)" v-model="step.text" placeholder="文本" size="small" />
                <el-input-number v-if="step.type === 'wait'" v-model="step.duration" :min="100" :max="60000" placeholder="毫秒" size="small" />
                <el-select v-if="step.type === 'wait_for'" v-model="step.state" placeholder="状态" size="small">
                  <el-option label="可见" value="visible" />
                  <el-option label="隐藏" value="hidden" />
                  <el-option label="附加" value="attached" />
                  <el-option label="分离" value="detached" />
                </el-select>
                <el-input v-if="step.type === 'drag_drop'" v-model="step.source" placeholder="源选择器" size="small" />
                <el-input v-if="step.type === 'drag_drop'" v-model="step.target" placeholder="目标选择器" size="small" />
              </div>
            </div>
            <el-button type="primary" plain @click="addStep" block>
              <el-icon><Plus /></el-icon>
              添加步骤
            </el-button>
          </div>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-select v-model="form.priority">
                <el-option label="P0" value="P0" />
                <el-option label="P1" value="P1" />
                <el-option label="P2" value="P2" />
                <el-option label="P3" value="P3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status">
                <el-option label="草稿" value="draft" />
                <el-option label="启用" value="active" />
                <el-option label="归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="executeDialogVisible" title="执行UI测试" width="500px">
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="所属项目" required>
          <el-select v-model="executeForm.project">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行模式">
          <el-radio-group v-model="executeForm.async_mode">
            <el-radio :label="false">同步执行</el-radio>
            <el-radio :label="true">异步执行</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="说明">
          <span style="color: #909399; font-size: 12px;">
            同步执行会等待所有用例执行完成，异步执行则立即返回任务ID
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleExecute">开始执行</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resultsDialogVisible" title="执行结果" width="900px">
      <div v-if="executeResult" class="execute-result">
        <el-alert :type="executeResult.failed === 0 ? 'success' : 'warning'" :closable="false">
          <template #title>
            执行完成 - 总数: {{ executeResult.total }} | 通过: {{ executeResult.passed }} | 失败: {{ executeResult.failed }} | 通过率: {{ executeResult.pass_rate }}%
          </template>
        </el-alert>
        <el-button type="primary" size="small" @click="loadExecutionResults" style="margin-top: 12px;">
          查看详细结果
        </el-button>
      </div>
      <el-table v-if="executionResults.length > 0" :data="executionResults" border stripe max-height="500">
        <el-table-column prop="testcase_name" label="用例名称" min-width="150" />
        <el-table-column prop="testcase_browser" label="浏览器" width="100">
          <template #default="{ row }">
            <el-tag :type="getBrowserType(row.testcase_browser)" size="small">{{ row.testcase_browser }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status === 'passed' ? '通过' : row.status === 'failed' ? '失败' : '错误' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长(ms)" width="100" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="showResultDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="detailDialogVisible" title="结果详情" width="800px" append-to-body>
        <el-descriptions v-if="selectedResult" :column="1" border>
          <el-descriptions-item label="用例名称">{{ selectedResult.testcase_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedResult.status)" size="small">
              {{ selectedResult.status === 'passed' ? '通过' : selectedResult.status === 'failed' ? '失败' : '错误' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时长">{{ selectedResult.duration || '-' }} ms</el-descriptions-item>
          <el-descriptions-item label="错误信息">{{ selectedResult.error_message || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="selectedResult?.screenshot" style="margin-top: 16px;">
          <h4>截图:</h4>
          <img :src="'data:image/png;base64,' + selectedResult.screenshot" alt="screenshot" style="max-width: 100%; border: 1px solid #ddd;" />
        </div>
        <div v-if="selectedResult?.logs" style="margin-top: 16px;">
          <h4>执行日志:</h4>
          <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 300px; overflow: auto; white-space: pre-wrap; word-break: break-all;">{{ selectedResult.logs }}</pre>
        </div>
      </el-dialog>
    </el-dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Delete, Plus } from "@element-plus/icons-vue";

import { fetchProjects } from "../../api/projects";
import {
  createUITest,
  deleteUITest,
  executeUITests,
  fetchUITestExecutions,
  fetchUITestExecutionResults,
  fetchUITests,
  updateUITest,
} from "../../api/uitests";


const projects = ref([]);
const uiTests = ref([]);
const total = ref(0);
const dialogVisible = ref(false);
const executeDialogVisible = ref(false);
const resultsDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const editingTest = ref(null);
const executeResult = ref(null);
const executionResults = ref([]);
const selectedResult = ref(null);

const query = reactive({
  project: "",
  browser: "",
  priority: "",
  status: "",
  page: 1,
  page_size: 20
});

const form = reactive({
  project: "",
  name: "",
  description: "",
  browser: "chromium",
  headless: true,
  viewport_width: 1280,
  viewport_height: 720,
  base_url: "",
  steps: [],
  timeout: 30000,
  priority: "P2",
  status: "draft"
});

const executeForm = reactive({
  project: "",
  async_mode: false
});

const needUrl = ["navigate"];
const needSelector = ["click", "fill", "type", "select_option", "check", "uncheck", "hover", "wait_for", "assert_text", "assert_exists", "assert_not_exists", "scroll_to", "upload"];
const needValue = ["fill", "type", "select_option", "upload"];
const needText = ["assert_text", "assert_title"];

onMounted(async () => {
  await loadProjects();
  await loadUITests();
});

async function loadProjects() {
  const data = await fetchProjects({ page_size: 100 });
  projects.value = data.results || [];
}

async function loadUITests() {
  const params = { ...query };
  Object.keys(params).forEach((key) => {
    if (params[key] === "") {
      delete params[key];
    }
  });
  const data = await fetchUITests(params);
  uiTests.value = data.results || [];
  total.value = data.count || 0;
}

function resetForm() {
  form.project = projects.value[0]?.id || "";
  form.name = "";
  form.description = "";
  form.browser = "chromium";
  form.headless = true;
  form.viewport_width = 1280;
  form.viewport_height = 720;
  form.base_url = "";
  form.steps = [];
  form.timeout = 30000;
  form.priority = "P2";
  form.status = "draft";
}

function openCreateDialog() {
  editingTest.value = null;
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row) {
  editingTest.value = row;
  form.project = row.project;
  form.name = row.name;
  form.description = row.description;
  form.browser = row.browser;
  form.headless = row.headless;
  form.viewport_width = row.viewport_width;
  form.viewport_height = row.viewport_height;
  form.base_url = row.base_url;
  form.steps = Array.isArray(row.steps) ? [...row.steps] : [];
  form.timeout = row.timeout;
  form.priority = row.priority;
  form.status = row.status;
  dialogVisible.value = true;
}

function addStep() {
  form.steps.push({
    type: "navigate",
    url: "",
    selector: "",
    value: "",
    text: "",
    duration: 1000,
    state: "visible",
    source: "",
    target: ""
  });
}

function removeStep(index) {
  form.steps.splice(index, 1);
}

async function handleSubmit() {
  if (editingTest.value) {
    await updateUITest(editingTest.value.id, form);
  } else {
    await createUITest(form);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  loadUITests();
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用例 ${row.name}?`, "删除确认", { type: "warning" });
  await deleteUITest(row.id);
  ElMessage.success("删除成功");
  loadUITests();
}

function handlePageChange(page) {
  query.page = page;
  loadUITests();
}

function openExecuteDialog() {
  executeForm.project = query.project || projects.value[0]?.id || "";
  executeForm.async_mode = false;
  executeDialogVisible.value = true;
}

async function handleExecute() {
  if (!executeForm.project) {
    ElMessage.warning("请选择项目");
    return;
  }

  try {
    const data = await executeUITests({
      project: executeForm.project,
      async_mode: executeForm.async_mode
    });

    if (executeForm.async_mode) {
      ElMessage.success(`任务已提交，任务ID: ${data.data.task_id}`);
    } else {
      executeResult.value = data.data;
      resultsDialogVisible.value = true;
      await loadExecutionResults();
    }
    executeDialogVisible.value = false;
  } catch (error) {
    ElMessage.error(error.response?.data?.message || "执行失败");
  }
}

async function handleExecuteSingle(row) {
  try {
    const data = await executeUITests({
      project: row.project,
      testcase_ids: [row.id],
      async_mode: false
    });

    executeResult.value = data.data;
    resultsDialogVisible.value = true;
    await loadExecutionResults();
  } catch (error) {
    ElMessage.error(error.response?.data?.message || "执行失败");
  }
}

async function loadExecutionResults() {
  if (!executeResult.value?.execution_id) return;

  try {
    const data = await fetchUITestExecutionResults(executeResult.value.execution_id);
    executionResults.value = data.data || [];
  } catch (error) {
    ElMessage.error("加载执行结果失败");
  }
}

function showResultDetail(row) {
  selectedResult.value = row;
  detailDialogVisible.value = true;
}

function getBrowserType(browser) {
  const typeMap = {
    chromium: "",
    firefox: "success",
    webkit: "warning"
  };
  return typeMap[browser] || "";
}

function getStatusType(status) {
  const typeMap = {
    passed: "success",
    failed: "danger",
    error: "warning"
  };
  return typeMap[status] || "";
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

.steps-container {
  width: 100%;
}

.step-item {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  background: #fafafa;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.step-index {
  font-weight: 600;
  color: #409eff;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.execute-result {
  margin-bottom: 16px;
}
</style>
