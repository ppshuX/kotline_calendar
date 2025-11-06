<template>
  <div class="calendar-page">
    <!-- 导航栏 -->
    <NavBar 
      @login="handleLogin"
      @register="handleRegister"
      @logout="handleLogout"
      @subscribe="handleSubscribe"
    />
    
    <!-- 主内容卡片 -->
    <ContentField>
      <!-- 工具栏 -->
      <div class="text-center mb-4">
        <Toolbar 
          @add="openAddDialog" 
          @refresh="loadEvents" 
          @testLunar="testLunar" 
        />
      </div>
      
      <!-- 两栏布局：桌面左右，移动端上下 -->
      <div class="row g-3">
        <!-- 左侧：日历（缩小到 80%，用 col-lg-6.5 约等于 54%） -->
        <div class="col-lg-6 col-12">
          <div class="calendar-wrapper">
            <FullCalendar :options="calendarOptions" />
          </div>
        </div>
        
        <!-- 右侧（桌面）/下方（移动）：日程列表 -->
        <div class="col-lg-6 col-12">
          <div class="events-sidebar">
            <div class="sidebar-header text-center mb-3">
              <h4>📋 日程列表</h4>
              <el-tag type="info" size="large">共 {{ eventsList.length }} 个</el-tag>
            </div>
            
            <div class="events-list">
              <!-- 日程卡片 -->
              <div 
                v-for="event in eventsList" 
                :key="event.id"
                class="event-item card mb-3 border-start border-primary border-4"
                @click="handleEventClick({ event: { extendedProps: event } })"
              >
                <div class="card-body p-3">
                  <div class="event-time text-muted small mb-2">
                    🕒 {{ formatEventTime(event.date_time) }}
                  </div>
                  <h6 class="event-title fw-bold mb-1">{{ event.title }}</h6>
                  <p class="event-desc text-secondary small mb-0 text-truncate" v-if="event.description">
                    {{ event.description }}
                  </p>
                </div>
              </div>
              
              <!-- 空状态 -->
              <div v-if="eventsList.length === 0" class="text-center py-5">
                <p class="text-muted mb-3">📭 暂无日程</p>
                <el-button type="primary" size="small" @click="openAddDialog">
                  ➕ 添加第一个日程
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ContentField>
    
    <!-- 添加/编辑日程对话框组件 -->
    <EventDialog
      v-model:visible="showAddDialog"
      :event="editingEvent"
      @save="saveEvent"
    />
    
    <!-- 查看日程详情对话框组件 -->
    <EventDetail
      v-model:visible="showDetailDialog"
      :event="selectedEvent"
      :lunar-date="lunarDateText"
      @edit="editEvent"
      @delete="deleteEvent"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import { eventAPI, lunarAPI } from '../api'

// 引入组件
import NavBar from '../components/NavBar.vue'
import ContentField from '../components/ContentField.vue'
import Toolbar from '../components/Toolbar.vue'
import EventDialog from '../components/EventDialog.vue'
import EventDetail from '../components/EventDetail.vue'

// 日历配置
const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'zh-cn',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek,dayGridDay'
  },
  buttonText: {
    today: '今天',
    month: '月',
    week: '周',
    day: '日'
  },
  events: [],
  editable: true,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  weekends: true,
  dateClick: handleDateClick,
  eventClick: handleEventClick,
})

// 对话框状态
const showAddDialog = ref(false)
const showDetailDialog = ref(false)

// 选中的事件和编辑中的事件
const selectedEvent = ref(null)
const editingEvent = ref(null)
const lunarDateText = ref('')

// 日程列表（用于侧边栏显示）
const eventsList = ref([])

// 加载日程
async function loadEvents() {
  try {
    const events = await eventAPI.getAll()
    console.log('✅ 加载的日程:', events)
    
    // 保存到列表（用于侧边栏）
    eventsList.value = events.sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
    
    // 转换为 FullCalendar 格式
    calendarOptions.value.events = events.map(event => ({
      id: event.id,
      title: event.title,
      start: event.date_time,
      extendedProps: {
        description: event.description,
        reminder_minutes: event.reminder_minutes,
        ...event
      }
    }))
    
    ElMessage.success(`✅ 加载了 ${events.length} 个日程`)
  } catch (error) {
    console.error('❌ 加载失败:', error)
    ElMessage.error('❌ 加载失败: ' + error.message)
  }
}

// 打开添加对话框
function openAddDialog() {
  editingEvent.value = null
  showAddDialog.value = true
}

// 点击日期
function handleDateClick(arg) {
  // 创建一个带有选中日期的临时事件
  editingEvent.value = {
    date_time: arg.dateStr
  }
  showAddDialog.value = true
}

// 点击事件
async function handleEventClick(clickInfo) {
  selectedEvent.value = clickInfo.event.extendedProps
  
  // 获取农历信息
  try {
    const dateStr = formatDate(clickInfo.event.start)
    const lunar = await lunarAPI.getLunarDate(dateStr)
    lunarDateText.value = `${lunar.lunar_date} ${lunar.zodiac}年`
  } catch (error) {
    console.error('获取农历失败:', error)
    lunarDateText.value = ''
  }
  
  showDetailDialog.value = true
}

// 保存日程
async function saveEvent(data) {
  try {
    if (data.id) {
      // 更新
      await eventAPI.update(data.id, data)
      ElMessage.success('✅ 更新成功')
    } else {
      // 创建
      await eventAPI.create(data)
      ElMessage.success('✅ 添加成功')
    }
    
    loadEvents()
  } catch (error) {
    console.error('❌ 保存失败:', error)
    ElMessage.error('❌ 保存失败: ' + error.message)
  }
}

// 编辑事件
function editEvent(event) {
  editingEvent.value = event
  showAddDialog.value = true
}

// 删除事件
async function deleteEvent(event) {
  try {
    await eventAPI.delete(event.id)
    ElMessage.success('🗑️ 删除成功')
    loadEvents()
  } catch (error) {
    console.error('❌ 删除失败:', error)
    ElMessage.error('❌ 删除失败: ' + error.message)
  }
}

// 测试农历
async function testLunar() {
  try {
    const today = formatDate(new Date())
    const lunar = await lunarAPI.getLunarDate(today)
    ElMessage.success(`🏮 今天是${lunar.lunar_date} ${lunar.zodiac}年`)
  } catch (error) {
    console.error('❌ 测试失败:', error)
    ElMessage.error('❌ 测试失败: ' + error.message)
  }
}

// 格式化日期
function formatDate(date) {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化事件时间（用于列表）
function formatEventTime(dateTime) {
  if (!dateTime) return ''
  const d = new Date(dateTime)
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  const weekday = weekdays[d.getDay()]
  return `${month}月${day}日 周${weekday} ${hour}:${minute}`
}

// NavBar 事件处理
function handleLogin() {
  ElMessage.info('🔑 登录功能开发中...')
}

function handleRegister() {
  ElMessage.info('✍️ 注册功能开发中...')
}

function handleLogout() {
  ElMessage.info('🚪 退出功能开发中...')
}

function handleSubscribe() {
  ElMessage.info('📡 订阅功能开发中...')
}

// 组件挂载时加载数据
onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.calendar-wrapper, .events-sidebar {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
}

.events-sidebar {
  max-height: 700px;
  overflow-y: auto;
}

.event-item {
  cursor: pointer;
  transition: all 0.3s;
}

.event-item:hover {
  transform: translateX(8px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3) !important;
  background: #f8f9ff !important;
}

:deep(.fc-button) {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  border: none !important;
  cursor: pointer !important;
}

:deep(.fc-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

:deep(.fc-daygrid-day) { cursor: pointer !important; }
:deep(.fc-daygrid-day:hover) { background-color: #f5f7fa !important; }
:deep(.fc-daygrid-day-frame) { min-height: 80px; }
:deep(.fc-daygrid-day-number) { cursor: pointer !important; padding: 8px; z-index: 3; }
:deep(.fc-daygrid-day-events) { margin-top: 28px !important; z-index: 1; }

:deep(.fc-event) {
  cursor: pointer !important;
  border-radius: 6px;
  padding: 3px 8px;
  margin: 3px 2px !important;
  font-size: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
}

:deep(.fc-event:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5) !important;
}

:deep(.fc-event-title) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.fc-day-today) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
}

:deep(.fc-day-today .fc-daygrid-day-number) {
  color: #667eea;
  font-weight: bold;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 4px; }

@media (max-width: 992px) {
  .events-sidebar { max-height: 400px; }
}

@media (max-width: 768px) {
  .calendar-wrapper, .events-sidebar { padding: 15px; }
  :deep(.fc-button) { font-size: 12px; }
}
</style>


