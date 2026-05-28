<template>
  <section>
    <div class="page-header">
      <h2>测试执行</h2>
    </div>

    <el-table :data="executions" border row-key="id">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="result-list">
            <el-table :data="row.plan_detail?.cases || []" size="small" border>
              <el-table-column prop="testcase_detail.title" label="用例标题" />
              <el-table-column label="结果" width="160">
                <template #default="{ row: caseRow }">
                  <el-select v-model="resultForms[row.id][caseRow.testcase].status">
                    <el-option label="通过" value="passed" />
                    <el-option label="失败" value="failed" />
                    <el-option label="阻塞" value="blocked" />
                    <el-option label="跳过" value="skipped" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="实际结果">
                <template #default="{ row: caseRow }">
                  <el-input v-model="resultForms[row.id][caseRow.testcase].actual_result" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row: caseRow }">
                  <el-button text type="primary" @click="handleSubmitResult(row, caseRow)">保存结果</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="plan_detail.name" label="计划" />
      <el-table-column prop="executor_name" label="执行人" width="140" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button text type="primary" @click="handleStart(row)">开始</el-button>
          <el-button text type="danger" @click="handleCancel(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { cancelExecution, fetchExecutions, startExecution, submitExecutionResult } from "../../api/executions";


const executions = ref([]);
const resultForms = reactive({});

onMounted(loadExecutions);

async function loadExecutions() {
  const data = await fetchExecutions({ page_size: 100 });
  executions.value = data.results || [];
  executions.value.forEach(initResultForms);
}

function initResultForms(execution) {
  resultForms[execution.id] = resultForms[execution.id] || {};
  const existingResults = new Map((execution.results || []).map((item) => [item.testcase, item]));
  (execution.plan_detail?.cases || []).forEach((caseRow) => {
    const existing = existingResults.get(caseRow.testcase);
    resultForms[execution.id][caseRow.testcase] = {
      status: existing?.status || "passed",
      actual_result: existing?.actual_result || "",
      remark: existing?.remark || ""
    };
  });
}

async function handleStart(row) {
  await startExecution(row.id);
  ElMessage.success("执行已开始");
  loadExecutions();
}

async function handleCancel(row) {
  await cancelExecution(row.id);
  ElMessage.success("执行已取消");
  loadExecutions();
}

async function handleSubmitResult(execution, caseRow) {
  await submitExecutionResult(execution.id, {
    testcase: caseRow.testcase,
    ...resultForms[execution.id][caseRow.testcase]
  });
  ElMessage.success("结果已保存");
  loadExecutions();
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

.result-list {
  padding: 12px 24px;
}
</style>
