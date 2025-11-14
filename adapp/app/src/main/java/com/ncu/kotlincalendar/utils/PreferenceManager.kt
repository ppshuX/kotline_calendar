package com.ncu.kotlincalendar.utils

import android.content.Context
import android.content.SharedPreferences

/**
 * SharedPreferences管理器
 * 负责存储用户偏好设置和认证信息
 */
object PreferenceManager {
    
    private const val PREF_NAME = "ralendar_prefs"
    
    // Keys
    private const val KEY_USE_CLOUD_MODE = "use_cloud_mode"
    private const val KEY_ACCESS_TOKEN = "access_token"
    private const val KEY_REFRESH_TOKEN = "refresh_token"
    private const val KEY_USER_ID = "user_id"
    private const val KEY_USERNAME = "username"
    private const val KEY_USER_EMAIL = "user_email"
    
    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    }
    
    /**
     * 是否使用云端模式
     */
    fun isCloudMode(context: Context): Boolean {
        return getPrefs(context).getBoolean(KEY_USE_CLOUD_MODE, false)
    }
    
    fun setCloudMode(context: Context, enabled: Boolean) {
        getPrefs(context).edit().putBoolean(KEY_USE_CLOUD_MODE, enabled).apply()
    }
    
    /**
     * Token管理
     */
    fun getAccessToken(context: Context): String? {
        return getPrefs(context).getString(KEY_ACCESS_TOKEN, null)
    }
    
    fun saveTokens(context: Context, accessToken: String, refreshToken: String) {
        getPrefs(context).edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .apply()
    }
    
    fun saveAccessToken(context: Context, accessToken: String) {
        getPrefs(context).edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .apply()
    }
    
    fun saveRefreshToken(context: Context, refreshToken: String) {
        getPrefs(context).edit()
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .apply()
    }
    
    fun clearTokens(context: Context) {
        getPrefs(context).edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_REFRESH_TOKEN)
            .apply()
    }
    
    /**
     * 用户信息管理
     */
    fun saveUserInfo(context: Context, userId: Long, username: String, email: String?) {
        getPrefs(context).edit()
            .putLong(KEY_USER_ID, userId)
            .putString(KEY_USERNAME, username)
            .putString(KEY_USER_EMAIL, email)
            .apply()
    }
    
    fun getUserInfo(context: Context): Triple<Long, String, String?>? {
        val prefs = getPrefs(context)
        val userId = prefs.getLong(KEY_USER_ID, -1)
        if (userId == -1L) return null
        
        val username = prefs.getString(KEY_USERNAME, "") ?: ""
        val email = prefs.getString(KEY_USER_EMAIL, null)
        return Triple(userId, username, email)
    }
    
    fun clearUserInfo(context: Context) {
        getPrefs(context).edit()
            .remove(KEY_USER_ID)
            .remove(KEY_USERNAME)
            .remove(KEY_USER_EMAIL)
            .apply()
    }
    
    /**
     * 是否已登录
     */
    fun isLoggedIn(context: Context): Boolean {
        return getAccessToken(context) != null
    }
    
    /**
     * 退出登录（清除所有认证信息）
     */
    fun logout(context: Context) {
        clearTokens(context)
        clearUserInfo(context)
        setCloudMode(context, false)
    }
}

