<template>
  <section>
    <div class="page-header">
      <h2>测试报告</h2>
      <div class="generate-form">
        <el-select v-model="executionId" placeholder="选择执行记录">
          <el-option
            v-for="execution in executions"
            :key="execution.id"
            :label="`${execution.plan_detail?.name || '执行记录'} #${execution.id}`"
            :value="execution.id"
          />
        </el-select>
        <el-select v-model="asyncMode" placeholder="生成模式" width="120">
          <el-option label="同步" :value="false" />
          <el-option label="异步" :value="true" />
        </el-select>
        <el-button type="primary" @click="handleGenerate" :loading="generating">
          {{ generating ? '生成中...' : '生成报告' }}
        </el-button>
      </div>
    </div>

    <div v-if="taskStatusVisible" class="task-status-card">
      <el-card title="报告生成进度" :body-style="{ padding: '16px' }">
        <div class="task-status">
          <el-progress :percentage="taskProgress" :status="taskStatusColor" />
          <p class="status-text">{{ taskStatusText }}</p>
          <p v-if="taskId" class="task-id">任务ID: {{ taskId }}</p>
        </div>
      </el-card>
    </div>

    <el-table :data="reports" border>
      <el-table-column prop="name" label="报告名称" />
      <el-table-column prop="plan_name" label="测试计划" width="180" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="通过率" width="120">
        <template #default="{ row }">{{ row.summary?.pass_rate || 0 }}%</template>
      </el-table-column>
      <el-table-column label="结果统计" width="240">
        <template #default="{ row }">
          通过 {{ row.summary?.passed || 0 }} / 失败 {{ row.summary?.failed || 0 }} / 阻塞 {{ row.summary?.blocked || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="报告" width="120">
        <template #default="{ row }">
          <el-link v-if="row.allure_report_path" :href="`http://127.0.0.1:8000${row.allure_report_path}`" target="_blank" type="primary">
            查看
          </el-link>
          <span v-else>-</span>
        </template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { ElMessage } from "element-plus";

import { fetchExecutions } from "../../api/executions";
import { fetchReports, generateReport, getReportTaskStatus } from "../../api/reports";


const reports = ref([]);
const executions = ref([]);
const executionId = ref("");
const asyncMode = ref(false);
const generating = ref(false);
const taskStatusVisible = ref(false);
const taskProgress = ref(0);
const taskStatusText = ref("");
const taskId = ref("");
let pollingInterval = null;

const taskStatusColor = computed(() => {
  if (taskStatusText.value.includes("成功")) return "success";
  if (taskStatusText.value.includes("失败")) return "exception";
  return "active";
});

onMounted(async () => {
  await Promise.all([loadReports(), loadExecutions()]);
});

async function loadReports() {
  const data = await fetchReports({ page_size: 100 });
  reports.value = data.results || [];
}

async function loadExecutions() {
  const data = await fetchExecutions({ page_size: 100 });
  executions.value = data.results || [];
}

async function handleGenerate() {
  if (!executionId.value) {
    ElMessage.warning("请选择执行记录");
    return;
  }

  generating.value = true;

  try {
    const response = await generateReport({
      execution: executionId.value,
      async_mode: asyncMode.value
    });

    if (response.data.async_mode) {
      // 异步模式
      taskId.value = response.data.task_id;
      taskStatusVisible.value = true;
      taskProgress.value = 25;
      taskStatusText.value = "报告正在生成中...";
      startPolling();
    } else {
      // 同步模式
      ElMessage.success("报告已生成");
      loadReports();
    }
  } catch (error) {
    ElMessage.error("生成报告失败: " + error.message);
  } finally {
    generating.value = false;
  }
}

function startPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }

  pollingInterval = setInterval(async () => {
    try {
      const response = await getReportTaskStatus(taskId.value);
      const status = response.data.status;
      const result = response.data.result;

      if (status === "SUCCESS") {
        taskProgress.value = 100;
        taskStatusText.value = "报告生成成功！";
        stopPolling();
        setTimeout(() => {
          taskStatusVisible.value = false;
          loadReports();
        }, 1500);
      } else if (status === "FAILURE") {
        taskProgress.value = 0;
        taskStatusText.value = `生成失败: ${result?.error || '未知错误'}`;
        stopPolling();
      } else {
        // PENDING, STARTED, RETRY
        if (taskProgress.value < 90) {
          taskProgress.value += 10;
        }
        taskStatusText.value = `报告正在生成中... (${status})`;
      }
    } catch (error) {
      taskStatusText.value = "查询状态失败";
      stopPolling();
    }
  }, 2000);
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
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

.generate-form {
  display: flex;
  gap: 8px;
  align-items: center;
}

.generate-form :deep(.el-select) {
  width: 220px;
}

.task-status-card {
  margin-bottom: 16px;
}

.task-status {
  text-align: center;
}

.status-text {
  margin: 12px 0 8px;
  color: #666;
}

.task-id {
  font-size: 12px;
  color: #999;
  margin: 0;
}
</style>
