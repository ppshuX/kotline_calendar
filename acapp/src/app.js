// KotlinCalendar - AcWing App
// 纯 Vue3 CDN 方案，无构建工具

// 解构 Vue3 全局 API
const { createApp, ref, computed, onMounted, reactive } = Vue;

// 导出 Calendar 类（AcWing 平台要求）
class Calendar {
  constructor(parent) {
    this.parent = parent; // AcWing 传入的容器
    this.app = null;
    this.init();
  }

  init() {
    // 创建 Vue 应用
    this.app = createApp({
      setup() {
        // 响应式数据
        const state = reactive({
          events: [],
          loading: false,
          currentDate: new Date(),
          showDialog: false,
          selectedEvent: null,
        });

        // 计算属性
        const currentMonth = computed(() => {
          const year = state.currentDate.getFullYear();
          const month = state.currentDate.getMonth() + 1;
          return `${year}年${month}月`;
        });

        const calendarDays = computed(() => {
          const year = state.currentDate.getFullYear();
          const month = state.currentDate.getMonth();
          
          // 获取当月第一天和最后一天
          const firstDay = new Date(year, month, 1);
          const lastDay = new Date(year, month + 1, 0);
          
          // 获取当月第一天是星期几（0-6）
          const firstDayWeek = firstDay.getDay();
          
          // 生成日历数组
          const days = [];
          
          // 填充上月的日期
          for (let i = 0; i < firstDayWeek; i++) {
            days.push({ date: null, disabled: true });
          }
          
          // 填充当月的日期
          for (let i = 1; i <= lastDay.getDate(); i++) {
            days.push({
              date: i,
              disabled: false,
              isToday: isToday(year, month, i),
            });
          }
          
          return days;
        });

        // 方法
        const isToday = (year, month, date) => {
          const today = new Date();
          return (
            today.getFullYear() === year &&
            today.getMonth() === month &&
            today.getDate() === date
          );
        };

        const prevMonth = () => {
          state.currentDate = new Date(
            state.currentDate.getFullYear(),
            state.currentDate.getMonth() - 1,
            1
          );
        };

        const nextMonth = () => {
          state.currentDate = new Date(
            state.currentDate.getFullYear(),
            state.currentDate.getMonth() + 1,
            1
          );
        };

        const fetchEvents = async () => {
          state.loading = true;
          try {
            const response = await fetch(
              'https://app7626.acapp.acwing.com.cn/api/events/'
            );
            const data = await response.json();
            state.events = data.results || data || [];
          } catch (error) {
            console.error('获取日程失败:', error);
          } finally {
            state.loading = false;
          }
        };

        const openEventDialog = (event = null) => {
          state.selectedEvent = event;
          state.showDialog = true;
        };

        const closeDialog = () => {
          state.showDialog = false;
          state.selectedEvent = null;
        };

        const deleteEvent = async (id) => {
          if (!confirm('确定删除这个日程吗？')) return;
          
          try {
            await fetch(
              `https://app7626.acapp.acwing.com.cn/api/events/${id}/`,
              { method: 'DELETE' }
            );
            await fetchEvents();
          } catch (error) {
            console.error('删除失败:', error);
          }
        };

        // 生命周期
        onMounted(() => {
          fetchEvents();
        });

        return {
          state,
          currentMonth,
          calendarDays,
          prevMonth,
          nextMonth,
          fetchEvents,
          openEventDialog,
          closeDialog,
          deleteEvent,
        };
      },

      // 模板（字符串模板）
      template: `
        <div class="kc-calendar">
          <!-- 头部 -->
          <div class="kc-header">
            <button class="kc-btn" @click="prevMonth">◀ 上月</button>
            <h2 class="kc-title">{{ currentMonth }}</h2>
            <button class="kc-btn" @click="nextMonth">下月 ▶</button>
          </div>

          <!-- 日历网格 -->
          <div class="kc-grid">
            <!-- 星期标题 -->
            <div class="kc-week-header">日</div>
            <div class="kc-week-header">一</div>
            <div class="kc-week-header">二</div>
            <div class="kc-week-header">三</div>
            <div class="kc-week-header">四</div>
            <div class="kc-week-header">五</div>
            <div class="kc-week-header">六</div>

            <!-- 日期 -->
            <div
              v-for="(day, index) in calendarDays"
              :key="index"
              class="kc-day"
              :class="{
                'kc-day--disabled': day.disabled,
                'kc-day--today': day.isToday
              }"
            >
              {{ day.date }}
            </div>
          </div>

          <!-- 日程列表 -->
          <div class="kc-events">
            <div class="kc-events-header">
              <h3>日程列表</h3>
              <button class="kc-btn kc-btn--primary" @click="openEventDialog()">
                ➕ 添加日程
              </button>
            </div>

            <div v-if="state.loading" class="kc-loading">
              加载中...
            </div>

            <div v-else-if="state.events.length === 0" class="kc-empty">
              暂无日程
            </div>

            <div
              v-else
              v-for="event in state.events"
              :key="event.id"
              class="kc-event-item"
            >
              <div class="kc-event-content">
                <h4>{{ event.title }}</h4>
                <p>{{ event.start_time }} - {{ event.end_time }}</p>
                <p v-if="event.location">📍 {{ event.location }}</p>
              </div>
              <div class="kc-event-actions">
                <button
                  class="kc-btn kc-btn--small"
                  @click="openEventDialog(event)"
                >
                  编辑
                </button>
                <button
                  class="kc-btn kc-btn--small kc-btn--danger"
                  @click="deleteEvent(event.id)"
                >
                  删除
                </button>
              </div>
            </div>
          </div>

          <!-- 简单对话框（演示用） -->
          <div v-if="state.showDialog" class="kc-dialog-overlay" @click="closeDialog">
            <div class="kc-dialog" @click.stop>
              <h3>{{ state.selectedEvent ? '编辑日程' : '添加日程' }}</h3>
              <p>对话框功能待实现...</p>
              <button class="kc-btn" @click="closeDialog">关闭</button>
            </div>
          </div>
        </div>
      `,
    });

    // 挂载到容器
    this.app.mount(this.parent);
  }

  // 销毁方法（AcWing 平台可能调用）
  destroy() {
    if (this.app) {
      this.app.unmount();
      this.parent.innerHTML = '';
    }
  }

  // 调整大小（AcWing 平台可能调用）
  resize() {
    // 响应式布局自动适应
    console.log('resize called');
  }
}

// 导出到全局（浏览器环境）
if (typeof window !== 'undefined') {
  window.Calendar = Calendar;
}

