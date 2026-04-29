<template>
  <el-container style="min-height: 100vh">
    <el-aside width="240px" style="background: #fff; border-right: 1px solid #e8e8e8">
      <div class="logo">Bug Tracker</div>
      <el-menu :default-active="activeMenu" router>
        <el-menu-item index="/">首页</el-menu-item>
      </el-menu>
      <div class="section-title">项目</div>
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
        <span style="font-weight: 600; font-size: 16px">Bug 追踪系统</span>
        <div style="display: flex; align-items: center; gap: 12px">
          <!-- Notification bell -->
          <el-popover trigger="click" width="360" @show="loadNotifications">
            <template #reference>
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
                <el-button text @click="loadNotifications">
                  <el-icon :size="20"><Bell /></el-icon>
                </el-button>
              </el-badge>
            </template>
            <div style="max-height: 400px; overflow-y: auto">
              <div v-if="notifications.length">
                <div v-for="n in notifications" :key="n.id"
                     :style="{ padding: '10px 0', borderBottom: '1px solid #f0f0f0', opacity: n.is_read ? 0.6 : 1 }"
                     @click="handleNotifClick(n)">
                  <p style="margin: 0; font-size: 13px">{{ n.message }}</p>
                  <span style="font-size: 11px; color: #999">{{ n.created_at }}</span>
                </div>
              </div>
              <el-empty v-else :image-size="40" description="暂无通知" />
              <div v-if="notifications.length" style="margin-top: 8px; text-align: right">
                <el-button text size="small" @click="handleMarkAllRead">全部已读</el-button>
              </div>
            </div>
          </el-popover>
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
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import { useProjectStore } from '../stores/project'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
const notifications = ref([])
const unreadCount = ref(0)

async function loadNotifications() {
  notifications.value = await store.fetchNotifications()
  const count = await store.fetchUnreadCount()
  unreadCount.value = count.unread_count
}

async function handleNotifClick(n) {
  if (!n.is_read) {
    await store.markNotificationRead(n.id)
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
  if (n.task_id) {
    router.push(`/project/${n.task_id}/board`)
  }
  notifications.value.find(x => x.id === n.id).is_read = true
}

async function handleMarkAllRead() {
  await store.markAllNotificationsRead()
  unreadCount.value = 0
  notifications.value.forEach(n => n.is_read = true)
}

onMounted(async () => {
  await authStore.fetchUser()
  await store.fetchProjects()
})
</script>

<style scoped>
.logo { padding: 20px; font-size: 18px; font-weight: bold; color: #f56c6c; border-bottom: 1px solid #e8e8e8; }
.section-title { padding: 12px 20px 4px; font-size: 12px; color: #999; text-transform: uppercase; }
.notification-badge { cursor: pointer; }
</style>
