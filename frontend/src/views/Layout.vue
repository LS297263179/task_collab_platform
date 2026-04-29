<template>
  <el-container style="min-height: 100vh">
    <el-aside width="240px" style="background: #fff; border-right: 1px solid #e8e8e8">
      <div class="logo">Task Collab</div>
      <el-menu :default-active="activeMenu" router>
        <el-menu-item index="/">首页</el-menu-item>
      </el-menu>
      <div class="section-title">我的项目</div>
      <el-menu>
        <el-menu-item v-for="p in store.projects" :key="p.id" :index="`/project/${p.id}/board`"
          style="padding-left: 20px">
          <span :style="{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: p.cover_color, marginRight: '8px' }"></span>
          {{ p.name }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e8e8e8; display: flex; align-items: center; justify-content: space-between">
        <span style="font-weight: 600; font-size: 16px">任务协作平台</span>
        <div style="display: flex; align-items: center; gap: 12px">
          <span v-if="authStore.user">{{ authStore.user.username }}</span>
          <el-button size="small" @click="authStore.logout(); router.push('/login')">退出</el-button>
        </div>
      </el-header>
      <el-main style="background: #f5f7fa">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '../stores/project'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

onMounted(async () => {
  await authStore.fetchUser()
  await store.fetchProjects()
})
</script>

<style scoped>
.logo { padding: 20px; font-size: 18px; font-weight: bold; color: #667eea; border-bottom: 1px solid #e8e8e8; }
.section-title { padding: 12px 20px 4px; font-size: 12px; color: #999; text-transform: uppercase; }
</style>
