import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
api.interceptors.request.use(
    config => {
        console.log('发送请求:', config.url)
        return config
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
api.interceptors.response.use(
    response => {
        console.log('收到响应:', response.data)
        return response.data
    },
    error => {
        console.error('响应错误:', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

// 日程 API
export const eventAPI = {
    // 获取所有日程
    async getAll() {
        const response = await api.get('/events/')
        // Django REST Framework 分页格式：{ count, next, previous, results }
        // 返回 results 数组
        return response.results || response || []
    },

    // 创建日程
    create(data) {
        return api.post('/events/', data)
    },

    // 更新日程
    update(id, data) {
        return api.put(`/events/${id}/`, data)
    },

    // 删除日程
    delete(id) {
        return api.delete(`/events/${id}/`)
    }
}

// 农历 API
export const lunarAPI = {
    // 获取农历日期
    getLunarDate(date) {
        return api.get('/lunar/', { params: { date } })
    }
}

// 公开日历 API
export const calendarAPI = {
    // 获取公开日历列表
    getAll() {
        return api.get('/calendars/')
    },

    // 获取日历订阅
    getFeed(slug) {
        return api.get(`/calendars/${slug}/feed/`)
    }
}

export default api

