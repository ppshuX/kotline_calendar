<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '✏️ 编辑日程' : '➕ 添加日程'"
    width="500px"
    @close="handleClose"
  >
    <el-form :model="formData" label-width="100px">
      <el-form-item label="标题">
        <el-input v-model="formData.title" placeholder="请输入日程标题" />
      </el-form-item>
      
      <el-form-item label="日期时间">
        <el-date-picker
          v-model="formData.dateTime"
          type="datetime"
          placeholder="选择日期时间"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="描述">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入日程描述（可选）"
        />
      </el-form-item>
      
      <el-form-item label="提前提醒">
        <el-select v-model="formData.reminderMinutes" placeholder="选择提醒时间">
          <el-option label="不提醒" :value="0" />
          <el-option label="提前5分钟" :value="5" />
          <el-option label="提前15分钟" :value="15" />
          <el-option label="提前30分钟" :value="30" />
          <el-option label="提前1小时" :value="60" />
          <el-option label="提前1天" :value="1440" />
        </el-select>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: Boolean,
  event: Object
})

const emit = defineEmits(['update:visible', 'save'])

// 本地 visible 状态
const dialogVisible = ref(props.visible)

// 表单数据
const formData = ref({
  title: '',
  description: '',
  dateTime: new Date(),
  reminderMinutes: 0
})

// 是否编辑模式
const isEdit = ref(false)

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    // 打开对话框时初始化数据
    if (props.event) {
      // 编辑模式
      isEdit.value = true
      formData.value = {
        title: props.event.title,
        description: props.event.description,
        dateTime: new Date(props.event.date_time),
        reminderMinutes: props.event.reminder_minutes
      }
    } else {
      // 新增模式
      isEdit.value = false
      resetForm()
    }
  }
})

// 监听对话框关闭
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 保存
const handleSave = () => {
  if (!formData.value.title) {
    ElMessage.warning('请输入标题')
    return
  }
  
  const data = {
    id: props.event?.id,
    title: formData.value.title,
    description: formData.value.description,
    date_time: formatDateTime(formData.value.dateTime),
    reminder_minutes: formData.value.reminderMinutes
  }
  
  emit('save', data)
  handleClose()
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    dateTime: new Date(),
    reminderMinutes: 0
  }
}

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toISOString().slice(0, 19)
}
</script>

<style scoped>
</style>

