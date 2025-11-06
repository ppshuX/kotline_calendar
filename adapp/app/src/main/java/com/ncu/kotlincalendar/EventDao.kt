package com.ncu.kotlincalendar

import androidx.room.*

/**
 * 日程数据访问对象（类似 Django 的 Manager）
 */
@Dao
interface EventDao {
    
    // 查询所有日程（简化版，不用 Flow）
    @Query("SELECT * FROM events ORDER BY dateTime ASC")
    suspend fun getAllEvents(): List<Event>
    
    // 插入日程
    @Insert
    suspend fun insert(event: Event): Long
    
    // 更新日程
    @Update
    suspend fun update(event: Event)
    
    // 删除日程
    @Delete
    suspend fun delete(event: Event)
}
