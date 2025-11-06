package com.ncu.kotlincalendar.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Retrofit 客户端（单例）
 */
object RetrofitClient {
    
    // 后端 API 地址
    // 开发环境（模拟器）：http://10.0.2.2:8000/api/
    // 生产环境（云服务器）：https://app7626.acapp.acwing.com.cn/api/
    private const val BASE_URL = "https://app7626.acapp.acwing.com.cn/api/"
    
    // 日志拦截器（调试用）
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    // OkHttp 客户端
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    // Retrofit 实例
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    // API 接口实例
    val api: CalendarApi by lazy {
        retrofit.create(CalendarApi::class.java)
    }
}

