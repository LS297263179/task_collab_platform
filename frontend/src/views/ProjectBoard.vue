<template>
  <div v-loading="loading">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>{{ store.currentProject?.name || '项目看板' }}</h2>
      <div style="display: flex; gap: 8px">
        <el-button @click="$router.push(`/project/${route.params.id}/dashboard`)">数据看板</el-button>
        <el-button @click="showAuditDialog = true">审计日志</el-button>
        <el-button @click="showTagDialog = true">标签管理</el-button>
        <el-button @click="showMemberDialog = true">成员管理</el-button>
        <el-button type="primary" @click="openCreateTask">+ 新建任务</el-button>
      </div>
    </div>

    <!-- Search / Filter bar -->
    <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center">
      <el-input v-model="filters.keyword" placeholder="搜索标题/描述..." clearable style="width: 200px" @clear="applyFilters" @keyup.enter="applyFilters" />
      <el-select v-model="filters.priority" placeholder="优先级" clearable style="width: 100px" @change="applyFilters">
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="严重程度" clearable style="width: 100px" @change="applyFilters">
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
      <el-select v-model="filters.assignee_id" placeholder="负责人" clearable style="width: 120px" @change="applyFilters">
        <el-option v-for="m in members" :key="m.user.id" :label="m.user.username" :value="m.user.id" />
      </el-select>
      <el-button @click="resetFilters" size="small">重置</el-button>
    </div>

    <!-- Overdue stats -->
    <div v-if="overdueTasks.length" style="margin-bottom: 16px">
      <el-alert :title="`有 ${overdueTasks.length} 个任务已过期`" type="warning" :closable="false" show-icon />
    </div>

    <!-- Kanban Board -->
    <div class="kanban">
      <div v-for="col in columns" :key="col.key" class="kanban-column">
        <div class="column-header" :style="{ borderTop: `3px solid ${col.color}` }">
          <span>{{ col.label }}</span>
          <el-tag size="small" type="info">{{ board[col.key]?.length || 0 }}</el-tag>
        </div>
        <draggable
          class="column-body"
          :list="board[col.key]"
          :group="{ name: 'tasks', pull: true, put: true }"
          :sort="true"
          item-key="id"
          animation="200"
          ghost-class="drag-ghost"
          @end="onDragEnd($event, col.key)"
        >
          <template #item="{ element: task }">
            <div class="task-card" :class="{ 'task-overdue': isOverdue(task) }"
                 @click="openTaskDetail(task)">
              <!-- Tags -->
              <div v-if="getTaskTags(task.id).length" class="task-tags">
                <span v-for="tag in getTaskTags(task.id)" :key="tag.id"
                      class="task-tag-badge"
                      :style="{ background: tag.color }"
                      :title="tag.name">{{ tag.name }}</span>
              </div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 8px">
                <el-tag :type="priorityType(task.priority)" size="small">{{ priorityLabel(task.priority) }}</el-tag>
                <el-tag :type="severityType(task.severity)" size="small" effect="dark">{{ severityLabel(task.severity) }}</el-tag>
              </div>
              <p class="task-title">{{ task.title }}</p>
              <p class="task-desc">{{ task.description?.slice(0, 60) || '' }}</p>
              <div style="margin-top: 8px; display: flex; justify-content: space-between; align-items: center">
                <span class="assignee">{{ task.assignee_id ? getUserName(task.assignee_id) : '未分配' }}</span>
                <el-button size="small" text type="danger" @click.stop="deleteTask(task)">删除</el-button>
              </div>
            </div>
          </template>
        </draggable>
        <el-empty v-if="!board[col.key]?.length" description="暂无任务" :image-size="60" />
      </div>
    </div>

    <!-- Create/Edit Bug Dialog -->
    <el-dialog v-model="showTaskDialog" :title="editingTask ? '编辑 Bug' : '新建 Bug'" width="600px">
      <el-form :model="taskForm" label-width="90px">
        <el-form-item label="标题">
          <el-input v-model="taskForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.description" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="复现步骤">
          <el-input v-model="taskForm.reproduction_steps" type="textarea" rows="4" placeholder="1. 打开页面&#10;2. 点击按钮&#10;3. 观察异常" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="taskForm.priority" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="urgent" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="严重程度">
              <el-select v-model="taskForm.severity" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="urgent" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="环境信息">
          <el-input v-model="taskForm.environment" placeholder="例如: Chrome 120 / Windows 11 / v2.3.1" />
        </el-form-item>
        <el-form-item label="关联 Commit">
          <el-input v-model="taskForm.commit_hash" placeholder="Git commit hash (可选)" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="taskForm.status" style="width: 100%">
            <el-option v-for="c in columns" :key="c.key" :label="c.label" :value="c.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="taskForm.assignee_id" placeholder="选择负责人" style="width: 100%" clearable>
            <el-option v-for="m in members" :key="m.user.id" :label="m.user.username" :value="m.user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="taskForm.due_date" type="date" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>

    <!-- Bug Detail Dialog -->
    <el-dialog v-model="showDetailDialog" title="Bug 详情" width="650px">
      <div v-if="selectedTask">
        <h3>{{ selectedTask.title }}</h3>
        <p style="color: #666; margin: 8px 0">{{ selectedTask.description || '暂无描述' }}</p>
        <div style="display: flex; gap: 8px; margin: 16px 0; flex-wrap: wrap">
          <el-tag :type="priorityType(selectedTask.priority)">{{ priorityLabel(selectedTask.priority) }}</el-tag>
          <el-tag :type="severityType(selectedTask.severity)" effect="dark">{{ severityLabel(selectedTask.severity) }}</el-tag>
          <el-tag>{{ statusLabel(selectedTask.status) }}</el-tag>
          <span style="color: #999; line-height: 22px">负责人: {{ selectedTask.assignee_id ? getUserName(selectedTask.assignee_id) : '未分配' }}</span>
        </div>

        <!-- Reproduction steps -->
        <div v-if="selectedTask.reproduction_steps" style="margin: 16px 0">
          <strong>复现步骤：</strong>
          <pre style="margin-top: 8px; padding: 12px; background: #f5f7fa; border-radius: 4px; white-space: pre-wrap; font-size: 13px">{{ selectedTask.reproduction_steps }}</pre>
        </div>

        <!-- Environment -->
        <div v-if="selectedTask.environment" style="margin: 16px 0">
          <strong>环境信息：</strong> <el-tag size="small" type="info">{{ selectedTask.environment }}</el-tag>
        </div>

        <!-- Commit hash -->
        <div v-if="selectedTask.commit_hash" style="margin: 16px 0">
          <strong>Commit：</strong>
          <el-link :href="`https://github.com/LS297263179/task_collab_platform/commit/${selectedTask.commit_hash}`"
                   target="_blank" type="warning">{{ selectedTask.commit_hash.slice(0, 7) }}</el-link>
        </div>

        <!-- Related bugs -->
        <div style="margin: 16px 0">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px">
            <strong>关联 Bug：</strong>
          <div style="display: flex; align-items: center; gap: 8px">
            <el-select v-model="linkTargetId" placeholder="搜索关联 Bug" style="width: 180px" clearable filterable size="small">
              <el-option v-for="t in availableLinkTargets" :key="t.id" :label="`#${t.id} ${t.title}`" :value="t.id" />
            </el-select>
            <el-button size="small" type="primary" @click="handleLinkBug">关联</el-button>
          </div>
          </div>
          <div v-if="relatedBugs.length" style="display: flex; flex-wrap: wrap; gap: 8px">
            <el-tag v-for="rb in relatedBugs" :key="rb.id" closable @close="handleUnlinkBug(rb.id)"
                    :type="statusTagType(rb.status)" size="small" style="cursor: default">
              #{{ rb.id }} {{ rb.title }} ({{ statusLabel(rb.status) }})
            </el-tag>
          </div>
          <span v-else style="color: #999; font-size: 13px">暂无关联 Bug</span>
        </div>

        <!-- Tags section -->
        <div style="margin: 16px 0">
          <strong>标签：</strong>
          <span v-if="getTaskTags(selectedTask.id).length" style="margin-right: 8px">
            <el-tag
              v-for="tag in getTaskTags(selectedTask.id)"
              :key="tag.id"
              :style="{ background: tag.color, color: '#fff', border: 'none', marginRight: '4px' }"
              closable
              @close="handleRemoveTag(tag.id)"
            >
              {{ tag.name }}
            </el-tag>
          </span>
          <el-select v-model="selectedTagId" placeholder="添加标签" style="width: 150px" clearable size="small" @change="handleAddTag">
            <el-option v-for="tag in projectTags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </div>

        <!-- Attachments section -->
        <div style="margin: 16px 0">
          <strong>附件：</strong>
          <el-upload
            action="/api/attachments"
            :show-file-list="false"
            :http-request="(opt) => handleUpload(opt.file)"
            :limit="5"
          >
            <el-button size="small" type="primary">上传附件</el-button>
          </el-upload>
          <div v-if="attachments.length" style="margin-top: 8px">
            <div v-for="att in attachments" :key="att.id"
                 style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 13px">
              <el-link :href="`/api/attachments/files/${att.filename}`" target="_blank" type="primary">{{ att.original_name }}</el-link>
              <span style="color: #999; margin: 0 8px">{{ formatFileSize(att.file_size) }}</span>
              <el-button size="small" text type="danger" @click="handleDeleteAttachment(att)">删除</el-button>
            </div>
          </div>
        </div>

        <el-divider>评论区</el-divider>
        <div class="comments">
          <div v-for="c in comments" :key="c.id" class="comment">
            <strong>{{ c.user?.username || '未知' }}</strong>
            <span style="color: #999; margin-left: 8px; font-size: 12px">{{ c.created_at }}</span>
            <p style="margin-top: 4px">{{ c.content }}</p>
          </div>
        </div>
        <el-input v-model="commentText" placeholder="输入评论..." @keydown.enter="sendComment" style="margin-top: 12px">
          <template #append>
            <el-button @click="sendComment">发送</el-button>
          </template>
        </el-input>
      </div>
    </el-dialog>

    <!-- Member Management Dialog -->
    <el-dialog v-model="showMemberDialog" title="成员管理" width="500px">
      <div style="margin-bottom: 12px">
        <el-input v-model="searchKeyword" placeholder="搜索用户名或邮箱..." style="width: 70%" @keyup.enter="handleSearch" />
        <el-button type="primary" @click="handleSearch" :loading="searching" style="margin-left: 8px">搜索</el-button>
      </div>
      <div v-if="searchResults.length" style="margin-bottom: 16px">
        <div v-for="u in searchResults" :key="u.id" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0">
          <span>{{ u.username }} ({{ u.email }})</span>
          <el-button size="small" @click="handleAddMember(u.id)">添加</el-button>
        </div>
      </div>
      <el-empty v-else-if="searchKeyword && searchResults.length === 0 && !searching" :image-size="60" description="未找到匹配的用户，请先让对方注册账号" />
      <h4>当前成员</h4>
      <div v-for="m in members" :key="m.id" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0">
        <span>{{ m.user.username }} <el-tag size="small">{{ m.role }}</el-tag></span>
      </div>
    </el-dialog>

    <!-- Tag Management Dialog -->
    <el-dialog v-model="showTagDialog" title="标签管理" width="500px">
      <div style="margin-bottom: 12px; display: flex; gap: 8px">
        <el-input v-model="newTagName" placeholder="标签名称" style="width: 120px" />
        <el-color-picker v-model="newTagColor" />
        <el-button type="primary" @click="handleCreateTag">创建</el-button>
      </div>
      <div v-for="tag in projectTags" :key="tag.id"
           style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0">
        <el-tag :style="{ background: tag.color, color: '#fff', border: 'none' }">{{ tag.name }}</el-tag>
      </div>
      <el-empty v-if="!projectTags.length" :image-size="60" description="暂无标签" />
    </el-dialog>

    <!-- Audit Log Dialog -->
    <el-dialog v-model="showAuditDialog" title="审计日志" width="650px">
      <el-timeline>
        <el-timeline-item v-for="log in auditLogs" :key="log.id" :timestamp="log.created_at" placement="top">
          <el-card :shadow="isImportantChange(log.changes) ? 'always' : 'hover'"
                   :style="isImportantChange(log.changes) ? { border: '1px solid #f56c6c' } : {}">
            <p><strong>{{ log.user?.username || '未知' }}</strong>
              <el-tag :type="auditActionType(log.action)" size="small" style="margin: 0 8px">{{ auditActionLabel(log.action) }}</el-tag>
              {{ log.entity_type }} #{{ log.entity_id }}
            </p>
            <div v-if="log.changes" style="margin-top: 6px">
              <span v-for="(val, key) in log.changes" :key="key"
                    :style="isCriticalField(key) ? { color: '#f56c6c', fontWeight: 'bold', fontSize: '12px' } : { color: '#666', fontSize: '12px' }"
                    style="margin-right: 12px">
                {{ fieldName(key) }}: {{ val }}
              </span>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-if="!auditLogs.length" :image-size="60" description="暂无审计记录" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import draggable from 'vuedraggable'
import { useProjectStore } from '../stores/project'

const route = useRoute()
const store = useProjectStore()
const loading = ref(false)
const tasks = ref([])
const members = ref([])
const comments = ref([])
const commentText = ref('')
const projectTags = ref([])
const taskTagMap = ref({})
const attachments = ref([])
const auditLogs = ref([])

// Filters
const filters = reactive({ keyword: '', priority: '', severity: '', assignee_id: '' })

function applyFilters() {
  const keyword = filters.keyword.toLowerCase()
  const filtered = tasks.value.filter(t => {
    if (keyword && !t.title.toLowerCase().includes(keyword) && !t.description.toLowerCase().includes(keyword)) return false
    if (filters.priority && t.priority !== filters.priority) return false
    if (filters.severity && t.severity !== filters.severity) return false
    if (filters.assignee_id && t.assignee_id != filters.assignee_id) return false
    return true
  })
  for (const col of columns) board[col.key] = filtered.filter(t => t.status === col.key)
}

function resetFilters() {
  Object.assign(filters, { keyword: '', priority: '', severity: '', assignee_id: '' })
  syncBoardFromTasks()
}

const columns = [
  { key: 'todo', label: '待办', color: '#909399' },
  { key: 'in_progress', label: '进行中', color: '#409EFF' },
  { key: 'review', label: '审核中', color: '#E6A23C' },
  { key: 'done', label: '已完成', color: '#67C23A' },
]

// Reactive board: each column has its own array so vuedraggable can mutate in place
const board = reactive({
  todo: [],
  in_progress: [],
  review: [],
  done: [],
})

function syncBoardFromTasks() {
  for (const col of columns) board[col.key] = []
  for (const t of tasks.value) {
    if (board[t.status]) board[t.status].push(t)
  }
}

// Overdue tasks
const overdueTasks = computed(() => {
  const now = new Date()
  return tasks.value.filter(t =>
    t.due_date && new Date(t.due_date) < now && t.status !== 'done'
  )
})

function isOverdue(task) {
  if (!task.due_date || task.status === 'done') return false
  return new Date(task.due_date) < new Date()
}

// Task tag helpers
function getTaskTags(taskId) {
  return (taskTagMap.value[taskId] || []).map(tid => projectTags.value.find(t => t.id === tid)).filter(Boolean)
}

function mapTagsToTask(taskId, tagIds) {
  taskTagMap.value[taskId] = tagIds
}

async function loadTaskTags() {
  const projectId = Number(route.params.id)
  const tags = await store.fetchTags(projectId)
  projectTags.value = tags

  // Build task -> tags map
  const map = {}
  for (const tag of tags) {
    // The backend returns tags on the task via task.tags relationship
    // but we fetch separately; for now build from tags we have
    if (tag.task_tags) {
      for (const tt of tag.task_tags) {
        if (!map[tt.task_id]) map[tt.task_id] = []
        map[tt.task_id].push(tag.id)
      }
    }
  }
  taskTagMap.value = map
}

async function handleAddTag(tagId) {
  if (!tagId || !selectedTask.value) return
  try {
    await store.addTagToTask(selectedTask.value.id, tagId)
    if (!taskTagMap.value[selectedTask.value.id]) taskTagMap.value[selectedTask.value.id] = []
    taskTagMap.value[selectedTask.value.id].push(tagId)
    ElMessage.success('标签已添加')
  } catch (e) {
    ElMessage.error(e.detail || '添加失败')
  }
}

async function handleRemoveTag(tagId) {
  if (!selectedTask.value) return
  try {
    await store.removeTagFromTask(selectedTask.value.id, tagId)
    if (taskTagMap.value[selectedTask.value.id]) {
      taskTagMap.value[selectedTask.value.id] = taskTagMap.value[selectedTask.value.id].filter(id => id !== tagId)
    }
    ElMessage.success('标签已移除')
  } catch (e) {
    ElMessage.error(e.detail || '移除失败')
  }
}

const selectedTagId = ref(null)
const relatedBugs = ref([])
const linkTargetId = ref(null)
const availableLinkTargets = ref([])

async function loadRelatedBugs(taskId) {
  try {
    relatedBugs.value = await store.fetchRelatedBugs(taskId)
  } catch {
    relatedBugs.value = []
  }
  // Available targets: all bugs in same project except current
  availableLinkTargets.value = tasks.value.filter(t => t.id !== taskId && t.project_id === Number(route.params.id))
}

async function handleLinkBug() {
  if (!linkTargetId.value || !selectedTask.value) return
  try {
    await store.linkBugs(selectedTask.value.id, linkTargetId.value)
    ElMessage.success('关联成功')
    await loadRelatedBugs(selectedTask.value.id)
    linkTargetId.value = null
  } catch (e) {
    const msg = e.detail || e.message || '关联失败'
    ElMessage.error(msg)
  }
}

async function handleUnlinkBug(targetId) {
  if (!selectedTask.value) return
  try {
    await store.unlinkBugs(selectedTask.value.id, targetId)
    ElMessage.success('已解除关联')
    await loadRelatedBugs(selectedTask.value.id)
  } catch (e) {
    ElMessage.error(e.detail || '解除失败')
  }
}

function statusTagType(s) {
  return { todo: 'info', in_progress: '', review: 'warning', done: 'success' }[s] || 'info'
}

// Tag creation
const showTagDialog = ref(false)
const newTagName = ref('')
const newTagColor = ref('#888888')

const showAuditDialog = ref(false)

function auditActionType(action) {
  return { create: 'success', update: 'warning', delete: 'danger' }[action] || 'info'
}
function auditActionLabel(action) {
  return { create: '创建', update: '修改', delete: '删除' }[action] || action
}
function isCriticalField(key) {
  return ['severity', 'priority', 'status', 'assignee_id'].includes(key)
}
function isImportantChange(changes) {
  if (!changes) return false
  return Object.keys(changes).some(k => isCriticalField(k))
}
function fieldName(key) {
  return { severity: '严重程度', priority: '优先级', status: '状态', assignee_id: '负责人', title: '标题', linked_to: '关联Bug' }[key] || key
}
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function handleUpload(file) {
  if (!selectedTask.value) return
  try {
    const att = await store.uploadAttachment(selectedTask.value.id, file)
    attachments.value.unshift(att)
    ElMessage.success('上传成功')
  } catch (e) {
    ElMessage.error(e.detail || '上传失败')
  }
}

async function handleDeleteAttachment(att) {
  try {
    await store.deleteAttachment(att.id)
    attachments.value = attachments.value.filter(a => a.id !== att.id)
    ElMessage.success('已删除')
  } catch (e) {
    ElMessage.error(e.detail || '删除失败')
  }
}

async function loadAttachmentsForTask(taskId) {
  attachments.value = await store.fetchAttachments(taskId)
}

async function loadAuditLogs() {
  const projectId = Number(route.params.id)
  auditLogs.value = await store.fetchAuditLogs(projectId)
}

async function handleCreateTag() {
  if (!newTagName.value) return ElMessage.warning('请输入标签名称')
  try {
    const tag = await store.createTag(Number(route.params.id), newTagName.value, newTagColor.value)
    projectTags.value.push(tag)
    ElMessage.success('标签已创建')
    newTagName.value = ''
    newTagColor.value = '#888888'
  } catch (e) {
    ElMessage.error(e.detail || '创建失败')
  }
}

// Drag & Drop
async function onDragEnd(evt, newStatus) {
  const task = evt.item?.__draggable_context?.element || evt.moved?.element
  if (!task) return

  if (evt.moved) {
    // Cross-column move: update status
    const oldIndex = evt.moved.oldIndex
    const newIndex = evt.moved.newIndex
    // The element might still have old status at this point
    try {
      await store.updateTask(task.id, { status: newStatus })
      task.status = newStatus
      ElMessage.success(`任务已移至「${columns.find(c => c.key === newStatus)?.label}」`)
    } catch {
      ElMessage.error('状态更新失败')
      await loadProject()
    }
  } else if (evt.sortable && evt.oldIndex !== evt.newIndex) {
    // In-column sort: update positions
    const tasksInCol = board[newStatus]
    try {
      const updates = tasksInCol.map((t, i) => store.updateTask(t.id, { position: i }))
      await Promise.all(updates)
    } catch {
      ElMessage.error('排序更新失败')
      await loadProject()
    }
  }
}

// Task dialog
const showTaskDialog = ref(false)
const editingTask = ref(null)
const taskForm = reactive({
  title: '', description: '', priority: 'medium', severity: 'medium', status: 'todo',
  assignee_id: null, due_date: null, project_id: null,
  reproduction_steps: '', environment: '', commit_hash: '',
})

// Detail dialog
const showDetailDialog = ref(false)
const selectedTask = ref(null)

// Member dialog
const showMemberDialog = ref(false)
const searchKeyword = ref('')
const searchResults = ref([])
const searching = ref(false)

const memberMap = computed(() => {
  const m = {}
  for (const member of members.value) m[member.user.id] = member.user.username
  return m
})

function getUserName(id) { return memberMap.value[id] || '未知' }

function priorityType(p) {
  const map = { low: 'info', medium: '', high: 'warning', urgent: 'danger' }
  return map[p] || ''
}
function priorityLabel(p) { return { low: '低', medium: '中', high: '高', urgent: '紧急' }[p] || p }
function severityType(p) { return { low: 'info', medium: '', high: 'warning', urgent: 'danger' }[p] || '' }
function severityLabel(p) { return { low: 'P4-低', medium: 'P3-中', high: 'P2-高', urgent: 'P1-紧急' }[p] || p }
function statusLabel(s) { return { todo: '待办', in_progress: '进行中', review: '审核中', done: '已完成' }[s] || s }
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }

async function loadProject() {
  const id = route.params.id
  loading.value = true
  try {
    await store.fetchProject(id)
    tasks.value = await store.fetchTasks(id)
    members.value = await store.fetchMembers(id)
    await loadTaskTags()
    resetFilters()  // Sync board and clear filters
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function openCreateTask() {
  editingTask.value = null
  Object.assign(taskForm, {
    title: '', description: '', priority: 'medium', severity: 'medium', status: 'todo',
    assignee_id: null, due_date: null, project_id: Number(route.params.id),
    reproduction_steps: '', environment: '', commit_hash: '',
  })
  showTaskDialog.value = true
}

function openTaskDetail(task) {
  selectedTask.value = task
  selectedTagId.value = null
  showDetailDialog.value = true
  loadComments(task.id)
  loadAttachmentsForTask(task.id)
  loadRelatedBugs(task.id)
}

async function saveTask() {
  if (!taskForm.title) return ElMessage.warning('请输入标题')
  try {
    if (editingTask.value) {
      await store.updateTask(editingTask.value.id, taskForm)
    } else {
      await store.createTask({ ...taskForm })
    }
    ElMessage.success('保存成功')
    showTaskDialog.value = false
    await loadProject()
  } catch (e) {
    ElMessage.error(e.detail || '保存失败')
  }
}

async function deleteTask(task) {
  try {
    await ElMessageBox.confirm(`确定删除「${task.title}」？`, '确认', { type: 'warning' })
    await store.deleteTask(task.id)
    ElMessage.success('已删除')
    await loadProject()
  } catch {}
}

async function loadComments(taskId) {
  comments.value = await store.fetchComments(taskId)
}

async function sendComment() {
  if (!commentText.value.trim() || !selectedTask.value) return
  await store.addComment(selectedTask.value.id, commentText.value)
  commentText.value = ''
  await loadComments(selectedTask.value.id)
}

async function handleSearch() {
  if (!searchKeyword.value) return
  searching.value = true
  try {
    searchResults.value = await store.searchUsers(searchKeyword.value)
  } catch {} finally {
    searching.value = false
  }
}

async function handleAddMember(userId) {
  try {
    await store.addMember(Number(route.params.id), userId)
    ElMessage.success('添加成功')
    members.value = await store.fetchMembers(Number(route.params.id))
  } catch (e) {
    ElMessage.error(e.detail || '添加失败')
  }
}

onMounted(loadProject)
watch(() => route.params.id, loadProject)
watch(showAuditDialog, (val) => { if (val) loadAuditLogs() })
</script>

<style scoped>
.kanban { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; min-height: 500px; }
.kanban-column { background: #f0f2f5; border-radius: 8px; overflow: hidden; }
.column-header { padding: 12px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; background: #fff; }
.column-body { padding: 8px; min-height: 100px; }
.task-card { background: #fff; padding: 12px; border-radius: 6px; margin-bottom: 8px; cursor: pointer; transition: box-shadow 0.2s; border-left: 3px solid transparent; }
.task-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.task-overdue { border-left-color: #f56c6c; background: #fef0f0; }
.task-overdue:hover { box-shadow: 0 2px 12px rgba(245,108,108,0.2); }
.task-tags { margin-bottom: 6px; }
.task-tag-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
  color: #fff;
  margin-right: 4px;
  line-height: 1.4;
}
.drag-ghost { opacity: 0.4; background: #e8e8e8; }
.task-title { font-weight: 500; font-size: 14px; }
.task-desc { color: #888; font-size: 12px; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.assignee { font-size: 12px; color: #666; }
.comments { max-height: 300px; overflow-y: auto; }
.comment { padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
@media (max-width: 768px) { .kanban { grid-template-columns: 1fr; } }
</style>
