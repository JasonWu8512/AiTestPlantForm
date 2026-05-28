<template>
  <section class="projects-page">
    <div class="page-header">
      <div>
        <h1>项目管理</h1>
        <p>管理和查看所有测试项目</p>
      </div>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目..."
          class="search-input"
          :prefix-icon="Search"
          clearable
        />
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新增项目
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="project-stats">
      <el-col :span="6">
        <div class="stat-item active">
          <span class="stat-value">{{ projects.filter(p => p.status === 'active').length }}</span>
          <span class="stat-label">活跃项目</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-item archived">
          <span class="stat-value">{{ projects.filter(p => p.status === 'archived').length }}</span>
          <span class="stat-label">归档项目</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-item total">
          <span class="stat-value">{{ projects.length }}</span>
          <span class="stat-label">总项目数</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-item cases">
          <span class="stat-value">{{ totalTestCases }}</span>
          <span class="stat-label">总用例数</span>
        </div>
      </el-col>
    </el-row>

    <el-card class="table-card" shadow="never">
      <el-table :data="filteredProjects" style="width: 100%" class="custom-table" stripe>
        <el-table-column prop="name" label="项目名称" min-width="200">
          <template #default="{ row }">
            <div class="project-info">
              <div class="project-avatar">{{ row.name?.charAt(0)?.toUpperCase() }}</div>
              <div>
                <div class="project-name">{{ row.name }}</div>
                <div class="project-desc">{{ row.description }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="test_cases_count" label="用例数量" width="140">
          <template #default="{ row }">
            <span class="case-count">{{ row.test_cases_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '活跃' : '归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="140">
          <template #default="{ row }">
            <div class="creator-info">
              <div class="creator-avatar">{{ row.created_by_name?.charAt(0)?.toUpperCase() }}</div>
              <span>{{ row.created_by_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button text type="primary" size="small" @click="viewProject(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadProjects"
          @current-change="loadProjects"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingProject ? '编辑项目' : '新增项目'"
      width="520px"
      class="project-dialog"
    >
      <el-form :model="form" label-position="top" class="project-form">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        <el-form-item label="项目状态">
          <el-select v-model="form.status" placeholder="请选择项目状态" style="width: 100%">
            <el-option label="活跃" value="active" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Plus, Edit, Delete, View, Check } from "@element-plus/icons-vue";

import { createProject, deleteProject, fetchProjects, updateProject } from "../../api/projects";

const projects = ref([
  { id: 1, name: "用户中心系统", description: "用户相关功能测试", status: "active", created_by_name: "张三", created_at: "2024-01-10", test_cases_count: 45 },
  { id: 2, name: "电商平台", description: "电商核心流程测试", status: "active", created_by_name: "李四", created_at: "2024-01-08", test_cases_count: 128 },
  { id: 3, name: "支付系统", description: "支付流程安全测试", status: "active", created_by_name: "王五", created_at: "2024-01-05", test_cases_count: 76 },
  { id: 4, name: "库存管理", description: "库存管理功能测试", status: "archived", created_by_name: "赵六", created_at: "2023-12-20", test_cases_count: 34 }
]);

const total = ref(projects.value.length);
const dialogVisible = ref(false);
const editingProject = ref(null);
const searchQuery = ref("");
const query = reactive({ page: 1, page_size: 20 });
const form = reactive({ name: "", description: "", status: "active" });

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value;
  return projects.value.filter(p => 
    p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    (p.description && p.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
  );
});

const totalTestCases = computed(() => {
  return projects.value.reduce((sum, p) => sum + (p.test_cases_count || 0), 0);
});

onMounted(loadProjects);

async function loadProjects() {
  try {
    const data = await fetchProjects(query);
    projects.value = data.results || projects.value;
    total.value = data.count || projects.value.length;
  } catch (e) {
    console.log('使用模拟数据');
  }
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

function viewProject(row) {
  ElMessage.info(`查看项目: ${row.name}`);
}

async function handleSubmit() {
  if (!form.name) {
    ElMessage.warning("请输入项目名称");
    return;
  }

  try {
    if (editingProject.value) {
      await updateProject(editingProject.value.id, form);
      const index = projects.value.findIndex(p => p.id === editingProject.value.id);
      if (index > -1) {
        projects.value[index] = { ...projects.value[index], ...form };
      }
      ElMessage.success("项目更新成功");
    } else {
      const newProject = await createProject(form);
      projects.value.unshift({
        id: Date.now(),
        ...form,
        created_by_name: "当前用户",
        created_at: new Date().toISOString().split('T')[0],
        test_cases_count: 0
      });
      total.value++;
      ElMessage.success("项目创建成功");
    }
    dialogVisible.value = false;
  } catch (e) {
    ElMessage.error("操作失败，请重试");
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目「${row.name}」吗？此操作不可恢复。`,
      "删除确认",
      {
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        type: "warning",
        confirmButtonClass: "el-button--danger"
      }
    );

    await deleteProject(row.id);
    projects.value = projects.value.filter(p => p.id !== row.id);
    total.value--;
    ElMessage.success("项目已删除");
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error("删除失败，请重试");
    }
  }
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  });
}
</script>

<style scoped>
.projects-page {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.project-stats {
  margin-bottom: 24px;
}

.stat-item {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border-left: 3px solid;
}

.stat-item.active {
  border-left-color: #22c55e;
}

.stat-item.archived {
  border-left-color: #64748b;
}

.stat-item.total {
  border-left-color: #6366f1;
}

.stat-item.cases {
  border-left-color: #f59e0b;
}

.stat-value {
  display: block;
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 6px;
}

.stat-label {
  color: #64748b;
  font-size: 14px;
}

.table-card {
  border-radius: 16px;
  border: 1px solid #f1f5f9;
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

.project-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.project-name {
  color: #1e293b;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.project-desc {
  color: #64748b;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.case-count {
  color: #1e293b;
  font-weight: 600;
}

.creator-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.creator-avatar {
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

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
}

.project-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 20px;
}

.project-form {
  padding-top: 8px;
}
</style>
