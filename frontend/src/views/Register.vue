<template>
  <div class="auth-page">
    <el-card class="auth-card" shadow="hover">
      <h2>注册账号</h2>
      <el-form :model="form" @submit.prevent="handleRegister" style="margin-top: 24px">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" type="email" placeholder="邮箱" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" @click="handleRegister" :loading="loading">
          注册
        </el-button>
      </el-form>
      <p class="link">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: '', email: '', password: '' })
const loading = ref(false)

async function handleRegister() {
  if (!form.username || !form.email || !form.password) return ElMessage.warning('请填写完整信息')
  loading.value = true
  try {
    await auth.register(form.username, form.email, form.password)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.auth-card { width: 400px; padding: 20px; }
.auth-card h2 { text-align: center; color: #333; }
.link { text-align: center; margin-top: 16px; color: #666; }
.link a { color: #667eea; text-decoration: none; }
</style>
