<template>
  <section>
    <h2>Dashboard</h2>
    <el-row :gutter="16">
      <el-col :span="6" v-for="item in cards" :key="item.label">
        <el-card shadow="never">
          <div class="metric-label">{{ item.label }}</div>
          <div class="metric-value">{{ item.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>通过率趋势</template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card class="recent-card" shadow="never">
          <template #header>最近执行</template>
          <el-table :data="recentExecutions" size="small">
            <el-table-column prop="plan_name" label="计划" />
            <el-table-column prop="executor_name" label="执行人" width="140" />
            <el-table-column prop="status" label="状态" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, onUnmounted } from "vue";
import * as echarts from "echarts";

import { useAuthStore } from "../../stores/auth";
import { fetchDashboardSummary, fetchRecentExecutions, fetchDashboardTrends } from "../../api/dashboard";

const authStore = useAuthStore();


const summary = ref({
  project_count: 0,
  testcase_count: 0,
  testplan_count: 0,
  execution_count: 0
});
const recentExecutions = ref([]);
const trends = ref([]);
const chartRef = ref(null);
let chartInstance = null;

const cards = computed(() => [
  { label: "项目数量", value: summary.value.project_count },
  { label: "用例数量", value: summary.value.testcase_count },
  { label: "计划数量", value: summary.value.testplan_count },
  { label: "执行记录", value: summary.value.execution_count }
]);

onMounted(async () => {
  summary.value = await fetchDashboardSummary();
  recentExecutions.value = await fetchRecentExecutions();
  trends.value = await fetchDashboardTrends();
  initChart();
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
  }
});

function initChart() {
  if (!chartRef.value) return;
  
  chartInstance = echarts.init(chartRef.value);
  const dates = trends.value.map(t => t.date);
  const passRates = trends.value.map(t => t.pass_rate);
  
  const option = {
    tooltip: {
      trigger: "axis",
      formatter: "{b}: {c}%"
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLabel: {
        formatter: "{value}%"
      }
    },
    series: [{
      name: "通过率",
      type: "line",
      smooth: true,
      data: passRates,
      lineStyle: {
        width: 3,
        color: "#67c23a"
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(103, 194, 58, 0.3)" },
          { offset: 1, color: "rgba(103, 194, 58, 0.05)" }
        ])
      },
      symbol: "circle",
      symbolSize: 8
    }]
  };
  
  chartInstance.setOption(option);
  
  window.addEventListener("resize", handleResize);
}

function handleResize() {
  chartInstance?.resize();
}
</script>

<style scoped>
h2 {
  margin: 0 0 16px;
  color: #111827;
  font-size: 22px;
}

.metric-label {
  color: #6b7280;
  font-size: 14px;
}

.metric-value {
  margin-top: 8px;
  color: #111827;
  font-size: 28px;
  font-weight: 700;
}

.recent-card {
  margin-top: 0;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
