<template>
  <section>
    <div class="page-header">
      <h2>通知配置</h2>
      <el-button type="primary" @click="openCreateDialog">新增配置</el-button>
    </div>

    <el-table :data="configs" border>
      <el-table-column prop="name" label="配置名称" />
      <el-table-column prop="type" label="通知类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.type === 'dingtalk' ? 'primary' : 'success'">
            {{ row.type === 'dingtalk' ? '钉钉' : '邮件' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="webhook_url" label="Webhook地址" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-switch :model-value="row.is_active" disabled />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button text type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-button text type="info" @click="handleTest(row)">测试</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editingConfig ? '编辑配置' : '新增配置'" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="配置名称" required>
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="通知类型" required>
          <el-select v-model="form.type">
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="邮件" value="email" />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook地址">
          <el-input v-model="form.webhook_url" placeholder="请输入钉钉机器人Webhook地址" />
        </el-form-item>
        <el-form-item label="访问令牌">
          <el-input v-model="form.access_token" placeholder="请输入访问令牌（可选）" />
        </el-form-item>
        <el-form-item label="密钥">
          <el-input v-model="form.secret" placeholder="请输入密钥（可选）" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup>import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { createNotificationConfig, deleteNotificationConfig, getNotificationConfigs, testNotificationConfig, updateNotificationConfig } from "../../api/notifications";
const configs = ref([]);
const total = ref(0);
const dialogVisible = ref(false);
const editingConfig = ref(null);
const query = reactive({ page: 1, page_size: 20 });
const form = reactive({
 name: "",
 type: "dingtalk",
 webhook_url: "",
 access_token: "",
 secret: "",
 is_active: true
});
onMounted(loadConfigs);
async function loadConfigs() {
 const data = await getNotificationConfigs(query);
 configs.value = data.results || [];
 total.value = data.count || 0;
}
function openCreateDialog() {
 editingConfig.value = null;
 form.name = "";
 form.type = "dingtalk";
 form.webhook_url = "";
 form.access_token = "";
 form.secret = "";
 form.is_active = true;
 dialogVisible.value = true;
}
function openEditDialog(row) {
 editingConfig.value = row;
 form.name = row.name;
 form.type = row.type;
 form.webhook_url = row.webhook_url || "";
 form.access_token = row.access_token || "";
 form.secret = row.secret || "";
 form.is_active = row.is_active;
 dialogVisible.value = true;
}
function handleClose() {
 dialogVisible.value = false;
}
async function handleSubmit() {
 if (!form.name) {
 ElMessage.warning("请输入配置名称");
 return;
 }
 if (!form.webhook_url && form.type === "dingtalk") {
 ElMessage.warning("请输入Webhook地址");
 return;
 }
 try {
 if (editingConfig.value) {
 await updateNotificationConfig(editingConfig.value.id, form);
 }
 else {
 await createNotificationConfig(form);
 }
 ElMessage.success("保存成功");
 dialogVisible.value = false;
 loadConfigs();
 }
 catch (error) {
 ElMessage.error("保存失败：" + (error.message || "未知错误"));
 }
}
async function handleTest(row) {
 if (row.type !== "dingtalk") {
 ElMessage.warning("暂不支持该类型的测试");
 return;
 }
 try {
 const result = await testNotificationConfig(row.id);
 if (result.success) {
 ElMessage.success("测试发送成功，请检查钉钉群消息");
 }
 else {
 ElMessage.error("测试发送失败：" + result.message);
 }
 }
 catch (error) {
 ElMessage.error("测试失败：" + (error.message || "未知错误"));
 }
}
async function handleDelete(row) {
 await ElMessageBox.confirm(`确认删除配置 ${row.name}？`, "删除确认", { type: "warning" });
 await deleteNotificationConfig(row.id);
 ElMessage.success("删除成功");
 loadConfigs();
}
function handlePageChange(page) {
 query.page = page;
 loadConfigs();
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

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>