package com.ncu.kotlincalendar.api.models

import com.google.gson.annotations.SerializedName

/**
 * 云端事件数据模型（与后端API对应）
 */
data class CloudEvent(
    @SerializedName("id")
    val id: Long? = null,
    
    @SerializedName("title")
    val title: String,
    
    @SerializedName("description")
    val description: String = "",
    
    @SerializedName("start_time")
    val startTime: String,  // ISO 8601格式: "2025-11-14T14:00:00+08:00"
    
    @SerializedName("end_time")
    val endTime: String? = null,
    
    @SerializedName("location")
    val location: String = "",
    
    @SerializedName("reminder_minutes")
    val reminderMinutes: Int = 0,
    
    @SerializedName("map_url")
    val mapUrl: String? = null,
    
    @SerializedName("is_public_calendar")
    val isPublicCalendar: Boolean = false,
    
    @SerializedName("created_at")
    val createdAt: String? = null,
    
    @SerializedName("updated_at")
    val updatedAt: String? = null
)

/**
 * 云端事件列表响应
 */
data class CloudEventListResponse(
    @SerializedName("count")
    val count: Int,
    
    @SerializedName("next")
    val next: String?,
    
    @SerializedName("previous")
    val previous: String?,
    
    @SerializedName("results")
    val results: List<CloudEvent>
)

/**
 * 认证响应
 */
data class AuthResponse(
    @SerializedName("access")
    val access: String? = null,
    
    @SerializedName("refresh")
    val refresh: String? = null,
    
    @SerializedName("user")
    val user: UserInfo? = null
)

/**
 * 用户信息
 */
data class UserInfo(
    @SerializedName("id")
    val id: Long,
    
    @SerializedName("username")
    val username: String,
    
    @SerializedName("email")
    val email: String? = null
)

/**
 * QQ登录请求
 */
data class QQLoginRequest(
    @SerializedName("code")
    val code: String
)

/**
 * QQ登录URL响应
 */
data class QQLoginUrlResponse(
    @SerializedName("apply_code_url")
    val applyCodeUrl: String
)

