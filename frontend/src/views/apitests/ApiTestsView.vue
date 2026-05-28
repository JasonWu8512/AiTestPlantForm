<template>
  <section>
    <div class="page-header">
      <h2>接口自动化测试</h2>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">新增用例</el-button>
        <el-button type="success" @click="openExecuteDialog">执行测试</el-button>
      </div>
    </div>

    <el-form :inline="true" class="toolbar" @submit.prevent>
      <el-form-item label="项目">
        <el-select v-model="query.project" clearable placeholder="全部项目" @change="loadApiTests">
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="方法">
        <el-select v-model="query.method" clearable placeholder="全部" @change="loadApiTests">
          <el-option label="GET" value="GET" />
          <el-option label="POST" value="POST" />
          <el-option label="PUT" value="PUT" />
          <el-option label="DELETE" value="DELETE" />
          <el-option label="PATCH" value="PATCH" />
        </el-select>
      </el-form-item>
      <el-form-item label="优先级">
        <el-select v-model="query.priority" clearable placeholder="全部" @change="loadApiTests">
          <el-option label="P0" value="P0" />
          <el-option label="P1" value="P1" />
          <el-option label="P2" value="P2" />
          <el-option label="P3" value="P3" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" clearable placeholder="全部" @change="loadApiTests">
          <el-option label="草稿" value="draft" />
          <el-option label="启用" value="active" />
          <el-option label="归档" value="archived" />
        </el-select>
      </el-form-item>
    </el-form>

    <el-table :data="apiTests" border stripe>
      <el-table-column prop="name" label="用例名称" min-width="150" />
      <el-table-column prop="method" label="方法" width="80">
        <template #default="{ row }">
          <el-tag :type="getMethodType(row.method)" size="small">{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="URL" min-width="250" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" :title="editingTest ? '编辑接口用例' : '新增接口用例'" width="800px">
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
          <el-col :span="4">
            <el-form-item label="方法">
              <el-select v-model="form.method">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="20">
            <el-form-item label="URL">
              <el-input v-model="form.url" placeholder="https://api.example.com/endpoint" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="URL 参数 (JSON)">
              <el-input v-model="paramsText" type="textarea" :rows="3" placeholder='{"key": "value"}' />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="请求头 (JSON)">
              <el-input v-model="headersText" type="textarea" :rows="3" placeholder='{"Content-Type": "application/json"}' />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="请求体类型">
          <el-select v-model="form.body_type">
            <el-option label="无" value="none" />
            <el-option label="JSON" value="json" />
            <el-option label="表单数据" value="form-data" />
            <el-option label="URL编码表单" value="x-www-form-urlencoded" />
            <el-option label="原始文本" value="raw" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.body_type !== 'none'" label="请求体 (JSON)">
          <el-input v-model="bodyText" type="textarea" :rows="4" placeholder='{"key": "value"}' />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="期望状态码">
              <el-input-number v-model="form.expected_status" :min="100" :max="599" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="超时时间 (秒)">
              <el-input-number v-model="form.timeout" :min="1" :max="300" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="验证规则 (JSON Array)">
          <el-input v-model="validationRulesText" type="textarea" :rows="3" placeholder='[{"type": "status_code", "params": {"expected": 200}}]' />
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

    <el-dialog v-model="executeDialogVisible" title="执行接口测试" width="500px">
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
        <el-table-column prop="testcase_method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.testcase_method)" size="small">{{ row.testcase_method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="testcase_url" label="URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status === 'passed' ? '通过' : row.status === 'failed' ? '失败' : '错误' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_status" label="响应状态" width="100" />
        <el-table-column prop="response_time" label="响应时间(ms)" width="100" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="showResultDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="detailDialogVisible" title="结果详情" width="700px" append-to-body>
        <el-descriptions v-if="selectedResult" :column="1" border>
          <el-descriptions-item label="用例名称">{{ selectedResult.testcase_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedResult.status)" size="small">
              {{ selectedResult.status === 'passed' ? '通过' : selectedResult.status === 'failed' ? '失败' : '错误' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应状态码">{{ selectedResult.response_status || '-' }}</el-descriptions-item>
          <el-descriptions-item label="响应时间">{{ selectedResult.response_time || '-' }} ms</el-descriptions-item>
          <el-descriptions-item label="错误信息">{{ selectedResult.error_message || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="selectedResult?.response_body" style="margin-top: 16px;">
          <h4>响应体:</h4>
          <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 300px; overflow: auto;">{{ JSON.stringify(selectedResult.response_body, null, 2) }}</pre>
        </div>
        <div v-if="selectedResult?.validation_results?.length > 0" style="margin-top: 16px;">
          <h4>验证结果:</h4>
          <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 200px; overflow: auto;">{{ JSON.stringify(selectedResult.validation_results, null, 2) }}</pre>
        </div>
      </el-dialog>
    </el-dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { fetchProjects } from "../../api/projects";
import {
  createApiTest,
  deleteApiTest,
  executeApiTests,
  fetchApiTestExecutions,
  fetchApiTestExecutionResults,
  fetchApiTests,
  updateApiTest,
} from "../../api/apitests";


const projects = ref([]);
const apiTests = ref([]);
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
  method: "",
  priority: "",
  status: "",
  page: 1,
  page_size: 20
});

const form = reactive({
  project: "",
  name: "",
  description: "",
  method: "GET",
  url: "",
  headers: {},
  params: {},
  body_type: "none",
  body: {},
  expected_status: 200,
  validation_rules: [],
  timeout: 30,
  priority: "P2",
  status: "draft"
});

const executeForm = reactive({
  project: "",
  async_mode: false
});

const paramsText = ref("");
const headersText = ref("");
const bodyText = ref("");
const validationRulesText = ref("");

onMounted(async () => {
  await loadProjects();
  await loadApiTests();
});

async function loadProjects() {
  const data = await fetchProjects({ page_size: 100 });
  projects.value = data.results || [];
}

async function loadApiTests() {
  const params = { ...query };
  Object.keys(params).forEach((key) => {
    if (params[key] === "") {
      delete params[key];
    }
  });
  const data = await fetchApiTests(params);
  apiTests.value = data.results || [];
  total.value = data.count || 0;
}

function resetForm() {
  form.project = projects.value[0]?.id || "";
  form.name = "";
  form.description = "";
  form.method = "GET";
  form.url = "";
  form.headers = {};
  form.params = {};
  form.body_type = "none";
  form.body = {};
  form.expected_status = 200;
  form.validation_rules = [];
  form.timeout = 30;
  form.priority = "P2";
  form.status = "draft";
  paramsText.value = "";
  headersText.value = "";
  bodyText.value = "";
  validationRulesText.value = "";
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
  form.method = row.method;
  form.url = row.url;
  form.headers = row.headers || {};
  form.params = row.params || {};
  form.body_type = row.body_type;
  form.body = row.body || {};
  form.expected_status = row.expected_status;
  form.validation_rules = row.validation_rules || [];
  form.timeout = row.timeout;
  form.priority = row.priority;
  form.status = row.status;
  paramsText.value = JSON.stringify(row.params || {}, null, 2);
  headersText.value = JSON.stringify(row.headers || {}, null, 2);
  bodyText.value = JSON.stringify(row.body || {}, null, 2);
  validationRulesText.value = JSON.stringify(row.validation_rules || [], null, 2);
  dialogVisible.value = true;
}

function parseJson(text) {
  if (!text || text.trim() === "") {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch (e) {
    return {};
  }
}

async function handleSubmit() {
  form.params = parseJson(paramsText.value);
  form.headers = parseJson(headersText.value);
  form.body = parseJson(bodyText.value);
  form.validation_rules = parseJson(validationRulesText.value);

  if (editingTest.value) {
    await updateApiTest(editingTest.value.id, form);
  } else {
    await createApiTest(form);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  loadApiTests();
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除用例 ${row.name}？`, "删除确认", { type: "warning" });
  await deleteApiTest(row.id);
  ElMessage.success("删除成功");
  loadApiTests();
}

function handlePageChange(page) {
  query.page = page;
  loadApiTests();
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
    const result = await executeApiTests({
      project: executeForm.project,
      async_mode: executeForm.async_mode
    });

    if (executeForm.async_mode) {
      ElMessage.success(`任务已提交，任务ID: ${result.data.task_id}`);
    } else {
      executeResult.value = result.data;
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
    const result = await executeApiTests({
      project: row.project,
      testcase_ids: [row.id],
      async_mode: false
    });

    executeResult.value = result.data;
    resultsDialogVisible.value = true;
    await loadExecutionResults();
  } catch (error) {
    ElMessage.error(error.response?.data?.message || "执行失败");
  }
}

async function loadExecutionResults() {
  if (!executeResult.value?.execution_id) return;

  try {
    const data = await fetchApiTestExecutionResults(executeResult.value.execution_id);
    executionResults.value = data.data || [];
  } catch (error) {
    ElMessage.error("加载执行结果失败");
  }
}

function showResultDetail(row) {
  selectedResult.value = row;
  detailDialogVisible.value = true;
}

function getMethodType(method) {
  const typeMap = {
    GET: "",
    POST: "success",
    PUT: "warning",
    DELETE: "danger",
    PATCH: "info"
  };
  return typeMap[method] || "";
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

.execute-result {
  margin-bottom: 16px;
}
</style>
