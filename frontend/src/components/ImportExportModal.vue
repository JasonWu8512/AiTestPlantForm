<template>
  <el-dialog :title="title" v-model="isVisible" width="500px">
    <div class="import-export-form">
      <template v-if="type === 'export'">
        <el-form :model="exportForm" label-width="120px">
          <el-form-item label="导出格式">
            <el-select v-model="exportForm.format" placeholder="请选择格式">
              <el-option label="Excel (.xlsx)" value="excel" />
              <el-option label="JSON" value="json" />
            </el-select>
          </el-form-item>
        </el-form>
      </template>

      <template v-else>
        <el-form :model="importForm" label-width="120px">
          <el-form-item label="导入格式">
            <el-select v-model="importForm.format" placeholder="请选择格式">
              <el-option label="Excel (.xlsx)" value="excel" />
              <el-option label="JSON" value="json" />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="importForm.format === 'excel'" label="上传文件">
            <el-upload
              class="upload-demo"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :before-upload="handleFileSelect"
              accept=".xlsx,.xls"
            >
              <el-button type="primary" @click="triggerUpload">
                <el-icon><Upload /></el-icon>
                选择文件
              </el-button>
            </el-upload>
            <span v-if="importForm.file" class="file-name">{{ importForm.file.name }}</span>
          </el-form-item>

          <el-form-item v-if="importForm.format === 'json'" label="JSON数据">
            <el-input
              v-model="importForm.jsonData"
              type="textarea"
              :rows="6"
              placeholder="请粘贴JSON数据"
            />
          </el-form-item>

          <el-form-item label="目标项目">
            <el-select v-model="importForm.projectId" placeholder="请选择项目">
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </template>

      <div v-if="result" class="result-section">
        <el-divider />
        <template v-if="result.success">
          <div class="success-message">
            <el-icon class="success-icon"><CircleCheck /></el-icon>
            <span v-if="type === 'export'">
              导出成功！共 {{ result.count }} 条数据
            </span>
            <span v-else>
              导入成功！共导入 {{ result.imported_count }} 条数据
              <span v-if="result.error_rows && result.error_rows.length">
                ，失败 {{ result.error_rows.length }} 条
              </span>
            </span>
          </div>
          <div v-if="type === 'export' && result.download_url" class="download-link">
            <el-button type="success" @click="downloadFile">
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
          </div>
          <div v-if="result.error_rows && result.error_rows.length" class="error-list">
            <el-alert title="失败记录" type="warning" :closable="false" />
            <ul>
              <li v-for="(error, index) in result.error_rows" :key="index">
                第 {{ error.row }} 行: {{ error.error }}
              </li>
            </ul>
          </div>
        </template>
        <template v-else>
          <div class="error-message">
            <el-icon class="error-icon"><CircleClose /></el-icon>
            {{ result.error }}
          </div>
        </template>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading">
          {{ type === 'export' ? '导出' : '导入' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Upload, Download, CircleCheck, CircleClose } from '@element-plus/icons-vue';
import { exportTestCasesExcel, exportTestCasesJson, importTestCasesExcel, importTestCasesJson } from '../api/testcases';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'export'
  },
  projectId: {
    type: Number,
    default: null
  },
  projects: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close', 'success']);

const isVisible = ref(false);

watch(() => props.visible, (val) => {
  isVisible.value = val;
});

const title = props.type === 'export' ? '导出测试用例' : '导入测试用例';

const exportForm = ref({
  format: 'excel'
});

const importForm = ref({
  format: 'excel',
  file: null,
  jsonData: '',
  projectId: props.projectId || null
});

const result = ref(null);
const loading = ref(false);

const triggerUpload = () => {
  document.querySelector('.upload-demo input[type="file"]')?.click();
};

const handleFileSelect = (file) => {
  importForm.value.file = file;
  return false;
};

const handleConfirm = async () => {
  loading.value = true;
  result.value = null;
  try {
    if (props.type === 'export') {
      await handleExport();
    } else {
      await handleImport();
    }
  } catch (error) {
    result.value = { success: false, error: error.message };
  } finally {
    loading.value = false;
  }
};

const handleExport = async () => {
  const projectId = props.projectId;
  if (!projectId) {
    result.value = { success: false, error: '请先选择项目' };
    return;
  }
  if (exportForm.value.format === 'excel') {
    const response = await exportTestCasesExcel(projectId);
    if (response.data.success) {
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      result.value = {
        success: true,
        count: response.data.count,
        download_url: url,
        filename: `testcases.xlsx`
      };
    } else {
      result.value = response.data;
    }
  } else {
    const response = await exportTestCasesJson(projectId);
    if (response.data.success) {
      const blob = new Blob([JSON.stringify(response.data.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      result.value = {
        success: true,
        count: response.data.count,
        download_url: url,
        filename: `testcases.json`
      };
    } else {
      result.value = response.data;
    }
  }
};

const handleImport = async () => {
  if (!importForm.value.projectId) {
    result.value = { success: false, error: '请选择目标项目' };
    return;
  }
  if (importForm.value.format === 'excel') {
    if (!importForm.value.file) {
      result.value = { success: false, error: '请选择要上传的文件' };
      return;
    }
    const formData = new FormData();
    formData.append('project', importForm.value.projectId);
    formData.append('file', importForm.value.file);
    const response = await importTestCasesExcel(formData);
    result.value = response.data;
  } else {
    if (!importForm.value.jsonData) {
      result.value = { success: false, error: '请输入JSON数据' };
      return;
    }
    let jsonData;
    try {
      jsonData = JSON.parse(importForm.value.jsonData);
    } catch {
      result.value = { success: false, error: 'JSON格式错误' };
      return;
    }
    const response = await importTestCasesJson({
      project: importForm.value.projectId,
      data: jsonData
    });
    result.value = response.data;
  }
  if (result.value.success) {
    emit('success');
  }
};

const downloadFile = () => {
  if (result.value.download_url) {
    const a = document.createElement('a');
    a.href = result.value.download_url;
    a.download = result.value.filename || 'testcases.xlsx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
};

const handleCancel = () => {
  isVisible.value = false;
  emit('close');
};
</script>

<style scoped>
.import-export-form {
  padding: 20px 0;
}

.file-name {
  margin-left: 10px;
  color: #666;
}

.result-section {
  margin-top: 10px;
}

.success-message,
.error-message {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 4px;
}

.success-message {
  background: #f0fdf4;
  color: #166534;
}

.error-message {
  background: #fef2f2;
  color: #991b1b;
}

.success-icon,
.error-icon {
  font-size: 20px;
  margin-right: 10px;
}

.download-link {
  margin-top: 10px;
}

.error-list {
  margin-top: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.error-list ul {
  margin: 0;
  padding: 10px;
  background: #fffbeb;
  border-radius: 4px;
}

.error-list li {
  list-style: none;
  padding: 4px 0;
  color: #92400e;
}
</style>