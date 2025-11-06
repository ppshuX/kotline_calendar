<template>
  <el-dialog
    v-model="dialogVisible"
    title="📋 日程详情"
    width="500px"
  >
    <div v-if="event" class="event-detail">
      <p><strong>📝 标题：</strong>{{ event.title }}</p>
      <p><strong>🕒 时间：</strong>{{ formatDateTime(event.date_time) }}</p>
      <p v-if="event.description">
        <strong>💬 描述：</strong>{{ event.description }}
      </p>
      <p v-if="event.reminder_minutes > 0">
        <strong>⏰ 提醒：</strong>提前 {{ getReminderText(event.reminder_minutes) }}
      </p>
      <p v-if="lunarDate">
        <strong>🏮 农历：</strong>{{ lunarDate }}
      </p>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="warning" @click="handleEdit">编辑</el-button>
      <el-button type="danger" @click="handleDelete">删除</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  event: Object,
  lunarDate: String
})

const emit = defineEmits(['update:visible', 'edit', 'delete'])

// 本地 visible 状态
const dialogVisible = ref(props.visible)

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
})

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 编辑
const handleEdit = () => {
  emit('edit', props.event)
  dialogVisible.value = false
}

// 删除
const handleDelete = () => {
  emit('delete', props.event)
  dialogVisible.value = false
}

// 关闭
const handleClose = () => {
  dialogVisible.value = false
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  const d = new Date(dateTime)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  return `${year}年${month}月${day}日 ${hour}:${minute}`
}

// 获取提醒文本
const getReminderText = (minutes) => {
  if (minutes === 0) return '不提醒'
  if (minutes < 60) return `${minutes}分钟`
  if (minutes < 1440) return `${minutes / 60}小时`
  return `${minutes / 1440}天`
}
</script>

<style scoped>
.event-detail p {
  margin: 10px 0;
  line-height: 1.6;
}
</style>

