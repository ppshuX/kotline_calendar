/**
 * Events Module - 事件数据管理
 */

const state = {
    events: [],
    loading: false,
    currentDate: new Date(),
}

const mutations = {
    SET_EVENTS(state, events) {
        // 确保events始终是数组
        state.events = Array.isArray(events) ? events : []
    },

    SET_LOADING(state, loading) {
        state.loading = loading
    },

    SET_CURRENT_DATE(state, date) {
        state.currentDate = date
    },

    ADD_EVENT(state, event) {
        state.events.push(event)
    },

    UPDATE_EVENT(state, updatedEvent) {
        const index = state.events.findIndex(e => e.id === updatedEvent.id)
        if (index !== -1) {
            state.events.splice(index, 1, updatedEvent)
        }
    },

    DELETE_EVENT(state, eventId) {
        state.events = state.events.filter(e => e.id !== eventId)
    },
}

const actions = {
    /**
     * 获取事件列表
     */
    async fetchEvents({ commit, rootState }) {
        commit('SET_LOADING', true)
        try {
            const headers = { 'Content-Type': 'application/json' }
            if (rootState.user.accessToken) {
                headers['Authorization'] = `Bearer ${rootState.user.accessToken}`
            } else {
                // 未登录，清空事件列表
                commit('SET_EVENTS', [])
                commit('SET_LOADING', false)
                return
            }

            const response = await fetch('https://app7626.acapp.acwing.com.cn/api/events/', {
                headers
            })
            
            if (!response.ok) {
                // 请求失败（如401），清空事件列表
                console.warn('获取事件失败:', response.status)
                commit('SET_EVENTS', [])
                commit('SET_LOADING', false)
                return
            }
            
            const data = await response.json()
            const events = Array.isArray(data) ? data : (data.results || [])
            commit('SET_EVENTS', events)
        } catch (error) {
            console.error('获取事件失败:', error)
            commit('SET_EVENTS', [])
        } finally {
            commit('SET_LOADING', false)
        }
    },

    /**
     * 创建事件
     */
    async createEvent({ dispatch, rootState }, eventData) {
        try {
            const headers = { 'Content-Type': 'application/json' }
            if (rootState.user.accessToken) {
                headers['Authorization'] = `Bearer ${rootState.user.accessToken}`
            }

            const response = await fetch('https://app7626.acapp.acwing.com.cn/api/events/', {
                method: 'POST',
                headers,
                body: JSON.stringify(eventData),
            })
            if (response.ok) {
                await dispatch('fetchEvents') // 重新获取列表
                return true
            }
            return false
        } catch (error) {
            console.error('创建事件失败:', error)
            return false
        }
    },

    /**
     * 更新事件
     */
    async updateEvent({ dispatch, rootState }, { id, eventData }) {
        try {
            const headers = { 'Content-Type': 'application/json' }
            if (rootState.user.accessToken) {
                headers['Authorization'] = `Bearer ${rootState.user.accessToken}`
            }

            const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/events/${id}/`, {
                method: 'PUT',
                headers,
                body: JSON.stringify(eventData),
            })
            if (response.ok) {
                await dispatch('fetchEvents')
                return true
            }
            return false
        } catch (error) {
            console.error('更新事件失败:', error)
            return false
        }
    },

    /**
     * 删除事件
     */
    async deleteEvent({ dispatch, rootState }, eventId) {
        try {
            const headers = {}
            if (rootState.user.accessToken) {
                headers['Authorization'] = `Bearer ${rootState.user.accessToken}`
            }

            const response = await fetch(`https://app7626.acapp.acwing.com.cn/api/events/${eventId}/`, {
                method: 'DELETE',
                headers,
            })
            if (response.ok) {
                await dispatch('fetchEvents')
                return true
            }
            return false
        } catch (error) {
            console.error('删除事件失败:', error)
            return false
        }
    },
}

const getters = {
    /**
     * 事件数量（只统计用户创建的日程，不包括节日）
     */
    eventCount: (state) => {
        return state.events.filter(event => !event.is_public_calendar).length
    },

    /**
     * 根据 ID 获取事件
     */
    getEventById: (state) => (id) => {
        return state.events.find(e => e.id === id)
    },

    /**
     * 按月份过滤事件
     */
    eventsByMonth: (state) => (year, month) => {
        return state.events.filter(event => {
            const eventDate = new Date(event.start_time)
            return eventDate.getFullYear() === year && eventDate.getMonth() === month
        })
    },
}

export default {
    state,
    mutations,
    actions,
    getters,
}

