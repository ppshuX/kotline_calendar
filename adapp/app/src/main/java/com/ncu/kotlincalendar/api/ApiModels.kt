package com.ncu.kotlincalendar.api

/**
 * API 数据模型（与后端对应）
 */

// 农历信息
data class LunarResponse(
    val lunar_date: String,      // "农历2025年十月初六"
    val year: Int,               // 2025
    val month: String,           // "十月"
    val day: String,             // "初六"
    val zodiac: String,          // "蛇"
    val solar_date: String       // "2025-11-05"
)

// 日历订阅响应
data class CalendarFeedResponse(
    val ics: String,             // iCalendar 格式内容
    val events_count: Int        // 事件数量
)

// 事件响应（用于云端同步，可选功能）
data class EventResponse(
    val id: Long,
    val title: String,
    val description: String,
    val date_time: String,       // ISO 格式：2025-11-06T14:00:00
    val reminder_minutes: Int,
    val created_at: String,
    val updated_at: String
)

