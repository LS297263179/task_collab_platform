<template>
  <div v-loading="loading">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>{{ store.currentProject?.name || '' }} - 数据看板</h2>
      <el-button @click="$router.push(`/project/${route.params.id}/board`)">返回看板</el-button>
    </div>

    <!-- Stats overview cards -->
    <el-row :gutter="16" style="margin-bottom: 24px">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总任务数" :value="dashboard?.task_stats.total || 0" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已完成 (本周)" :value="dashboard?.task_stats.completed_this_week || 0" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="逾期任务" :value="dashboard?.task_stats.overdue || 0" />
          <template #suffix>
            <span v-if="(dashboard?.task_stats.overdue || 0) > 0" style="color: #f56c6c">!</span>
          </template>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="团队成员" :value="dashboard?.member_workloads?.length || 0" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Status & Priority charts -->
    <el-row :gutter="16" style="margin-bottom: 24px">
      <el-col :span="12">
        <el-card header="任务状态分布">
          <div ref="statusChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="任务优先级分布">
          <div ref="priorityChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Member workload table -->
    <el-card header="成员工作量">
      <el-table :data="dashboard?.member_workloads || []" stripe>
        <el-table-column prop="username" label="成员" />
        <el-table-column prop="total_tasks" label="总计" sortable />
        <el-table-column prop="todo" label="待办" />
        <el-table-column prop="in_progress" label="进行中" />
        <el-table-column prop="review" label="审核中" />
        <el-table-column prop="done" label="已完成" />
        <el-table-column prop="overdue" label="逾期">
          <template #default="{ row }">
            <span v-if="row.overdue > 0" style="color: #f56c6c">{{ row.overdue }}</span>
            <span v-else>{{ row.overdue }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '../stores/project'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const loading = ref(false)
const dashboard = ref(null)
const statusChartRef = ref(null)
const priorityChartRef = ref(null)

async function loadData() {
  loading.value = true
  try {
    await store.fetchProject(route.params.id)
    dashboard.value = await store.fetchDashboard(route.params.id)
    await nextTick()
    renderCharts()
  } catch {
    ElMessage.error('加载数据看板失败')
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  if (!dashboard.value) return
  const stats = dashboard.value.task_stats

  // Status pie chart
  if (statusChartRef.value) {
    const chart = echarts.init(statusChartRef.value)
    const statusLabels = { todo: '待办', in_progress: '进行中', review: '审核中', done: '已完成' }
    const statusColors = { todo: '#909399', in_progress: '#409EFF', review: '#E6A23C', done: '#67C23A' }
    const data = Object.entries(stats.by_status || {}).map(([k, v]) => ({
      name: statusLabels[k] || k, value: v, itemStyle: { color: statusColors[k] || '#ccc' }
    }))
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        label: { show: true, formatter: '{b}: {c} ({d}%)' },
        data,
      }],
    })
  }

  // Priority bar chart
  if (priorityChartRef.value) {
    const chart = echarts.init(priorityChartRef.value)
    const priorityLabels = { low: '低', medium: '中', high: '高', urgent: '紧急' }
    const priorityColors = { low: '#909399', medium: '#409EFF', high: '#E6A23C', urgent: '#F56C6C' }
    const keys = ['low', 'medium', 'high', 'urgent']
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: keys.map(k => priorityLabels[k]) },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: keys.map(k => ({
          value: (stats.by_priority || {})[k] || 0,
          itemStyle: { color: priorityColors[k] }
        })),
      }],
    })
  }
}

onMounted(loadData)
watch(() => route.params.id, loadData)
</script>
