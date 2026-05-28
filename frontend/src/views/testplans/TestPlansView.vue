<template>
  <section>
    <div class="page-header">
      <h2>测试计划</h2>
      <el-button type="primary" @click="openCreateDialog">新增计划</el-button>
    </div>

    <el-table :data="plans" border row-key="id">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="case-list">
            <div class="case-toolbar">
              <el-select v-model="selectedCase[row.id]" placeholder="选择用例">
                <el-option
                  v-for="testcase in testcases.filter((item) => item.project === row.project)"
                  :key="testcase.id"
                  :label="testcase.title"
                  :value="testcase.id"
                />
              </el-select>
              <el-button @click="handleAddCase(row)">添加用例</el-button>
            </div>
            <div class="sort-hint">拖拽行调整执行顺序</div>
            <el-table 
              :data="row.cases || []" 
              size="small" 
              border
              @row-drag-end="(e) => handleRowDragEnd(row, e)"
              :row-class-name="(row) => row === draggingRow ? 'dragging' : ''"
              draggable="true"
            >
              <el-table-column prop="sort_order" label="顺序" width="80" />
              <el-table-column prop="testcase_detail.title" label="用例标题" />
              <el-table-column label="操作" width="120">
                <template #default="{ row: caseRow }">
                  <el-button text type="danger" @click="handleRemoveCase(row, caseRow)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="计划名称" />
      <el-table-column prop="project_name" label="项目" width="160" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-button text @click="handleCreateExecution(row)">创建执行</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingPlan ? '编辑计划' : '新增计划'" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="所属项目">
          <el-select v-model="form.project">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
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
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { createExecution } from "../../api/executions";
import { fetchProjects } from "../../api/projects";
import { fetchTestCases } from "../../api/testcases";
import { addCaseToPlan, createTestPlan, fetchTestPlans, reorderCases, removeCaseFromPlan, updateTestPlan } from "../../api/testplans";


const projects = ref([]);
const testcases = ref([]);
const plans = ref([]);
const selectedCase = reactive({});
const dialogVisible = ref(false);
const editingPlan = ref(null);
const draggingRow = ref(null);
const form = reactive({ project: "", name: "", description: "", status: "draft" });

onMounted(async () => {
  await Promise.all([loadProjects(), loadTestCases()]);
  await loadPlans();
});

async function loadProjects() {
  const data = await fetchProjects({ page_size: 100 });
  projects.value = data.results || [];
}

async function loadTestCases() {
  const data = await fetchTestCases({ page_size: 100 });
  testcases.value = data.results || [];
}

async function loadPlans() {
  const data = await fetchTestPlans({ page_size: 100 });
  plans.value = data.results || [];
}

function resetForm() {
  form.project = projects.value[0]?.id || "";
  form.name = "";
  form.description = "";
  form.status = "draft";
}

function openCreateDialog() {
  editingPlan.value = null;
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row) {
  editingPlan.value = row;
  form.project = row.project;
  form.name = row.name;
  form.description = row.description;
  form.status = row.status;
  dialogVisible.value = true;
}

async function handleSubmit() {
  if (editingPlan.value) {
    await updateTestPlan(editingPlan.value.id, form);
  } else {
    await createTestPlan(form);
  }
  ElMessage.success("保存成功");
  dialogVisible.value = false;
  loadPlans();
}

async function handleAddCase(plan) {
  const testcase = selectedCase[plan.id];
  if (!testcase) {
    return;
  }
  await addCaseToPlan(plan.id, { testcase });
  ElMessage.success("添加成功");
  selectedCase[plan.id] = "";
  loadPlans();
}

async function handleRemoveCase(plan, caseRow) {
  await removeCaseFromPlan(plan.id, caseRow.testcase);
  ElMessage.success("移除成功");
  loadPlans();
}

async function handleCreateExecution(plan) {
  await createExecution({ plan: plan.id });
  ElMessage.success("执行记录已创建");
}

async function handleRowDragEnd(plan, event) {
  const { oldIndex, newIndex } = event;
  if (oldIndex === newIndex) return;
  
  const cases = [...(plan.cases || [])];
  const [removed] = cases.splice(oldIndex, 1);
  cases.splice(newIndex, 0, removed);
  
  const caseIds = cases.map(c => c.testcase);
  await reorderCases(plan.id, caseIds);
  ElMessage.success("排序已更新");
  loadPlans();
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

.case-list {
  display: grid;
  gap: 12px;
  padding: 12px 24px;
}

.case-toolbar {
  display: flex;
  gap: 8px;
}

.sort-hint {
  font-size: 12px;
  color: #6b7280;
  padding: 4px 0;
}

:deep(.el-table__row.dragging) {
  background: #f0f5ff;
}
</style>
