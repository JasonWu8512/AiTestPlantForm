<template>
  <section class="dashboard">
    <div class="page-header">
      <div>
        <h1>仪表板</h1>
        <p>欢迎回来，这是您的测试平台概览</p>
      </div>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="(item, index) in cards" :key="index">
        <div class="stat-card" :class="'card-' + index">
          <div class="stat-icon">
            <el-icon :size="28"><component :is="item.icon" /></el-icon>
          </div>
          <div class="stat-content">
            <span class="stat-label">{{ item.label }}</span>
            <span class="stat-value">{{ item.value }}</span>
            <div class="stat-change" :class="item.change > 0 ? 'positive' : 'negative'">
              <el-icon><component :is="item.change > 0 ? 'Top' : 'Bottom'" /></el-icon>
              {{ Math.abs(item.change) }}% 较上周
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-title">通过率趋势</span>
                <span class="card-subtitle">最近 7 天</span>
              </div>
              <el-button-group>
                <el-button size="small">日</el-button>
                <el-button size="small" type="primary">周</el-button>
                <el-button size="small">月</el-button>
              </el-button-group>
            </div>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-title">执行统计</span>
                <span class="card-subtitle">按类型分布</span>
              </div>
            </div>
          </template>
          <div ref="pieChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="bottom-row">
      <el-col :xs="24" :lg="16">
        <el-card class="recent-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-title">最近执行</span>
                <span class="card-subtitle">最近 10 次测试执行记录</span>
              </div>
              <el-button text>查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentExecutions" style="width: 100%" class="custom-table">
            <el-table-column prop="plan_name" label="计划名称">
              <template #default="{ row }">
                <div class="plan-name">
                  <div class="plan-icon">{{ row.plan_name?.charAt(0) }}</div>
                  <span>{{ row.plan_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="executor_name" label="执行人" width="140">
              <template #default="{ row }">
                <div class="executor-info">
                  <div class="executor-avatar">{{ row.executor_name?.charAt(0)?.toUpperCase() }}</div>
                  <span>{{ row.executor_name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="执行时间" width="180">
              <template #default="{ row }">
                {{ row.time }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card class="quick-actions-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div>
                <span class="card-title">快捷操作</span>
                <span class="card-subtitle">常用功能</span>
              </div>
            </div>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="$router.push('/testcases')">
              <div class="action-icon">
                <el-icon><Document /></el-icon>
              </div>
              <span>测试用例</span>
            </div>
            <div class="action-item" @click="$router.push('/testplans')">
              <div class="action-icon">
                <el-icon><Tickets /></el-icon>
              </div>
              <span>测试计划</span>
            </div>
            <div class="action-item" @click="$router.push('/executions')">
              <div class="action-icon">
                <el-icon><VideoPlay /></el-icon>
              </div>
              <span>执行测试</span>
            </div>
            <div class="action-item" @click="$router.push('/reports')">
              <div class="action-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <span>查看报告</span>
            </div>
            <div class="action-item" @click="$router.push('/api-tests')">
              <div class="action-icon">
                <el-icon><Connection /></el-icon>
              </div>
              <span>接口测试</span>
            </div>
            <div class="action-item" @click="$router.push('/ui-tests')">
              <div class="action-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <span>UI 测试</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, onUnmounted } from "vue";
import { Plus, Document, Tickets, VideoPlay, TrendCharts, Connection, Monitor, DataBoard, Folder, DocumentChecked } from "@element-plus/icons-vue";
import * as echarts from "echarts";

import { fetchDashboardSummary, fetchRecentExecutions, fetchDashboardTrends } from "../../api/dashboard";

const summary = ref({
  project_count: 12,
  testcase_count: 284,
  testplan_count: 36,
  execution_count: 1256
});

const recentExecutions = ref([
  { plan_name: "登录功能测试", executor_name: "张三", status: "通过", time: "2024-01-15 14:30" },
  { plan_name: "支付流程测试", executor_name: "李四", status: "失败", time: "2024-01-15 13:15" },
  { plan_name: "购物车测试", executor_name: "王五", status: "通过", time: "2024-01-15 11:45" },
  { plan_name: "用户注册测试", executor_name: "张三", status: "通过", time: "2024-01-15 10:20" },
  { plan_name: "搜索功能测试", executor_name: "赵六", status: "进行中", time: "2024-01-15 09:00" }
]);

const trends = ref([
  { date: "周一", pass_rate: 85 },
  { date: "周二", pass_rate: 92 },
  { date: "周三", pass_rate: 88 },
  { date: "周四", pass_rate: 95 },
  { date: "周五", pass_rate: 90 },
  { date: "周六", pass_rate: 94 },
  { date: "周日", pass_rate: 91 }
]);

const cards = computed(() => [
  { label: "项目数量", value: summary.value.project_count, change: 12, icon: Folder },
  { label: "用例数量", value: summary.value.testcase_count, change: 8, icon: DocumentChecked },
  { label: "计划数量", value: summary.value.testplan_count, change: -3, icon: Tickets },
  { label: "执行记录", value: summary.value.execution_count, change: 25, icon: DataBoard }
]);

const chartRef = ref(null);
const pieChartRef = ref(null);
let chartInstance = null;
let pieChartInstance = null;

onMounted(async () => {
  try {
    summary.value = await fetchDashboardSummary();
    recentExecutions.value = await fetchRecentExecutions();
    trends.value = await fetchDashboardTrends();
  } catch (e) {
    console.log('使用模拟数据');
  }
  initChart();
  initPieChart();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
  }
  if (pieChartInstance) {
    pieChartInstance.dispose();
  }
  window.removeEventListener("resize", handleResize);
});

function initChart() {
  if (!chartRef.value) return;
  
  chartInstance = echarts.init(chartRef.value);
  const dates = trends.value.map(t => t.date);
  const passRates = trends.value.map(t => t.pass_rate);
  
  const option = {
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#e2e8f0",
      borderWidth: 1,
      textStyle: {
        color: "#1e293b"
      },
      formatter: "{b}: {c}%"
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      top: "10%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dates,
      axisLine: {
        lineStyle: {
          color: "#e2e8f0"
        }
      },
      axisLabel: {
        color: "#64748b"
      }
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: "#f1f5f9"
        }
      },
      axisLabel: {
        color: "#64748b",
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
        color: "#6366f1"
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(99, 102, 241, 0.2)" },
          { offset: 1, color: "rgba(99, 102, 241, 0.02)" }
        ])
      },
      symbol: "circle",
      symbolSize: 8,
      itemStyle: {
        color: "#6366f1",
        borderColor: "#ffffff",
        borderWidth: 2
      }
    }]
  };
  
  chartInstance.setOption(option);
}

function initPieChart() {
  if (!pieChartRef.value) return;
  
  pieChartInstance = echarts.init(pieChartRef.value);
  
  const option = {
    tooltip: {
      trigger: "item",
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderColor: "#e2e8f0",
      borderWidth: 1,
      textStyle: {
        color: "#1e293b"
      }
    },
    legend: {
      orient: "vertical",
      right: "5%",
      top: "center",
      itemWidth: 12,
      itemHeight: 12,
      textStyle: {
        color: "#64748b",
        fontSize: 13
      }
    },
    series: [{
      name: "执行统计",
      type: "pie",
      radius: ["40%", "70%"],
      center: ["35%", "50%"],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: "#fff",
        borderWidth: 3
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: "bold",
          color: "#1e293b"
        }
      },
      data: [
        { value: 35, name: "通过", itemStyle: { color: "#22c55e" } },
        { value: 10, name: "失败", itemStyle: { color: "#ef4444" } },
        { value: 8, name: "阻塞", itemStyle: { color: "#f59e0b" } },
        { value: 7, name: "跳过", itemStyle: { color: "#64748b" } }
      ]
    }]
  };
  
  pieChartInstance.setOption(option);
}

function handleResize() {
  chartInstance?.resize();
  pieChartInstance?.resize();
}

function getStatusType(status) {
  const map = {
    '通过': 'success',
    '失败': 'danger',
    '进行中': 'warning',
    '阻塞': 'info'
  };
  return map[status] || 'info';
}
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.page-header h1 {
  margin: 0 0 6px;
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-0 .stat-icon {
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  color: #ffffff;
}

.card-1 .stat-icon {
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
  color: #ffffff;
}

.card-2 .stat-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  color: #ffffff;
}

.card-3 .stat-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  color: #ffffff;
}

.stat-content {
  flex: 1;
}

.stat-label {
  display: block;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 6px;
}

.stat-value {
  display: block;
  color: #1e293b;
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 6px;
}

.stat-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
}

.stat-change.positive {
  color: #22c55e;
}

.stat-change.negative {
  color: #ef4444;
}

.charts-row,
.bottom-row {
  margin-bottom: 24px;
}

.chart-card,
.recent-card,
.quick-actions-card {
  border-radius: 16px;
  border: 1px solid #f1f5f9;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: block;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.card-subtitle {
  display: block;
  color: #64748b;
  font-size: 13px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.pie-chart-container {
  width: 100%;
  height: 320px;
}

.custom-table :deep(.el-table__header-wrapper th) {
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  border-bottom: 1px solid #f1f5f9;
}

.custom-table :deep(.el-table__row) {
  transition: background var(--transition-fast);
}

.custom-table :deep(.el-table__row:hover) {
  background: #f8fafc;
}

.plan-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plan-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 600;
  font-size: 14px;
}

.executor-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.executor-avatar {
  width: 30px;
  height: 30px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-weight: 600;
  font-size: 12px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-item {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-item:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%);
  transform: translateY(-2px);
}

.action-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  color: #ffffff;
}

.action-item span {
  color: #1e293b;
  font-size: 14px;
  font-weight: 500;
}
</style>
