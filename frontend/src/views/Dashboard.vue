<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>我的项目</h2>
      <el-button type="primary" @click="showCreate = true">+ 新建项目</el-button>
    </div>

    <el-empty v-if="store.projects.length === 0" description="还没有项目，创建一个吧" />

    <el-row :gutter="16">
      <el-col v-for="project in store.projects" :key="project.id" :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="project-card" @click="router.push(`/project/${project.id}/board`)" style="cursor: pointer">
          <div class="cover" :style="{ background: project.cover_color }"></div>
          <h3 style="margin-top: 12px">{{ project.name }}</h3>
          <p style="color: #888; font-size: 13px; margin-top: 4px">{{ project.description || '暂无描述' }}</p>
          <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center">
            <el-tag size="small" type="info">{{ project.members?.length || 1 }} 人</el-tag>
            <el-button size="small" text type="danger" @click.stop="handleDelete(project.id)">删除</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showCreate" title="新建项目" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="输入项目名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="封面颜色">
          <el-color-picker v-model="form.cover_color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '../stores/project'

const router = useRouter()
const store = useProjectStore()
const showCreate = ref(false)
const form = reactive({ name: '', description: '', cover_color: '#4A90D9' })

async function handleCreate() {
  if (!form.name) return ElMessage.warning('请输入项目名称')
  try {
    await store.createProject(form)
    ElMessage.success('创建成功')
    showCreate.value = false
    Object.assign(form, { name: '', description: '', cover_color: '#4A90D9' })
  } catch (e) {
    ElMessage.error(e.detail || '创建失败')
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定删除该项目？', '确认', { type: 'warning' })
    await store.deleteProject(id)
    ElMessage.success('已删除')
  } catch {}
}
</script>

<style scoped>
.project-card .cover { height: 80px; border-radius: 4px; }
h2 { color: #333; }
</style>
