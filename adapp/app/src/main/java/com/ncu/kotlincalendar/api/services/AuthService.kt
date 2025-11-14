package com.ncu.kotlincalendar.api.services

import com.ncu.kotlincalendar.api.models.AuthResponse
import com.ncu.kotlincalendar.api.models.QQLoginRequest
import com.ncu.kotlincalendar.api.models.QQLoginUrlResponse
import retrofit2.Response
import retrofit2.http.*

/**
 * 认证API服务
 */
interface AuthService {
    
    /**
     * 获取QQ登录授权URL
     */
    @GET("auth/qq/login/")
    suspend fun getQQLoginUrl(): Response<QQLoginUrlResponse>
    
    /**
     * QQ登录（使用code）
     */
    @POST("auth/qq/callback/")
    suspend fun qqLogin(
        @Body request: QQLoginRequest
    ): Response<AuthResponse>
    
    /**
     * 验证当前用户
     */
    @GET("auth/me/")
    suspend fun getCurrentUser(
        @Header("Authorization") authorization: String
    ): Response<com.ncu.kotlincalendar.api.models.UserInfo>
}

