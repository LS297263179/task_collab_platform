import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const currentProject = ref(null)

  async function fetchProjects() {
    projects.value = await api.get('/projects')
  }

  async function createProject(data) {
    const project = await api.post('/projects', data)
    projects.value.push(project)
    return project
  }

  async function deleteProject(id) {
    await api.delete(`/projects/${id}`)
    projects.value = projects.value.filter((p) => p.id !== id)
  }

  async function fetchProject(id) {
    currentProject.value = await api.get(`/projects/${id}`)
  }

  async function fetchTasks(projectId) {
    return await api.get(`/tasks/project/${projectId}`)
  }

  async function createTask(data) {
    return await api.post('/tasks', data)
  }

  async function updateTask(id, data) {
    return await api.put(`/tasks/${id}`, data)
  }

  async function deleteTask(id) {
    await api.delete(`/tasks/${id}`)
  }

  async function fetchComments(taskId) {
    return await api.get(`/comments/task/${taskId}`)
  }

  async function addComment(taskId, content) {
    return await api.post('/comments', { task_id: taskId, content })
  }

  async function fetchMembers(projectId) {
    return await api.get(`/projects/${projectId}/members`)
  }

  async function addMember(projectId, userId) {
    return await api.post(`/projects/${projectId}/members/${userId}`)
  }

  async function searchUsers(keyword) {
    return await api.get(`/auth/search?keyword=${keyword}`)
  }

  async function fetchTags(projectId) {
    return await api.get(`/tags/project/${projectId}`)
  }

  async function createTag(projectId, name, color) {
    return await api.post(`/tags/project/${projectId}`, { name, color })
  }

  async function addTagToTask(taskId, tagId) {
    return await api.post(`/tags/${taskId}/${tagId}`)
  }

  async function removeTagFromTask(taskId, tagId) {
    return await api.delete(`/tags/${taskId}/${tagId}`)
  }

  async function uploadAttachment(taskId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return await api.post(`/attachments/task/${taskId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  }

  async function fetchAttachments(taskId) {
    return await api.get(`/attachments/task/${taskId}`)
  }

  async function deleteAttachment(attachmentId) {
    await api.delete(`/attachments/${attachmentId}`)
  }

  async function fetchDashboard(projectId) {
    return await api.get(`/projects/${projectId}/dashboard`)
  }

  async function fetchAuditLogs(projectId, limit = 50) {
    return await api.get(`/projects/${projectId}/audit?limit=${limit}`)
  }

  return {
    projects, currentProject,
    fetchProjects, createProject, deleteProject,
    fetchProject, fetchTasks, createTask, updateTask, deleteTask,
    fetchComments, addComment, fetchMembers, addMember, searchUsers,
    fetchTags, createTag, addTagToTask, removeTagFromTask,
    uploadAttachment, fetchAttachments, deleteAttachment,
    fetchDashboard, fetchAuditLogs,
  }
})
