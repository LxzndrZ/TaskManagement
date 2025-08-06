<!-- filepath: c:\Users\Jamaico Magayo\flask\frontend\src\components\Dashboard.vue -->
<template>
  <div>
    <h2>Dashboard</h2>
    <form @submit.prevent="addTask">
      <input v-model="newTask" placeholder="New Task" required />
      <button type="submit">Add Task</button>
    </form>
    <ul>
      <li v-for="task in tasks" :key="task.id">
        <input type="checkbox" v-model="task.completed" @change="updateTask(task)" />
        <span :style="{ textDecoration: task.completed ? 'line-through' : 'none' }">{{ task.title }}</span>
        <button @click="deleteTask(task.id)">Delete</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tasks = ref([])
const newTask = ref('')

const fetchTasks = async () => {
  const token = localStorage.getItem('token')
  const res = await axios.get('http://localhost:5000/api/tasks', {
    headers: { Authorization: `Bearer ${token}` }
  })
  tasks.value = res.data
}

const addTask = async () => {
  const token = localStorage.getItem('token')
  await axios.post('http://localhost:5000/api/tasks', { title: newTask.value }, {
    headers: { Authorization: `Bearer ${token}` }
  })
  newTask.value = ''
  fetchTasks()
}

const updateTask = async (task) => {
  const token = localStorage.getItem('token')
  await axios.put(`http://localhost:5000/api/tasks/${task.id}`, task, {
    headers: { Authorization: `Bearer ${token}` }
  })
  fetchTasks()
}

const deleteTask = async (id) => {
  const token = localStorage.getItem('token')
  await axios.delete(`http://localhost:5000/api/tasks/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  fetchTasks()
}

onMounted(fetchTasks)
</script>