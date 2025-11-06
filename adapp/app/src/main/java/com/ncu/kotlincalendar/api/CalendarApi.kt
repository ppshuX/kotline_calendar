package com.ncu.kotlincalendar.api

import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * 日历 API 接口定义
 */
interface CalendarApi {
    
    /**
     * 获取农历日期
     * @param date 公历日期，格式：2025-11-05
     */
    @GET("lunar/")
    suspend fun getLunarDate(@Query("date") date: String): LunarResponse
    
    /**
     * 获取日历订阅内容
     * @param slug 日历标识，如：china-holidays
     */
    @GET("calendars/{slug}/feed/")
    suspend fun getCalendarFeed(@Path("slug") slug: String): CalendarFeedResponse
    
    // 以下是云端同步功能的 API（可选）
    // @GET("events/")
    // suspend fun getEvents(): List<EventResponse>
    
    // @POST("events/")
    // suspend fun createEvent(@Body event: EventResponse): EventResponse
}

