# Android端QQ登录集成指南

## 一、更换应用图标

### 方法：使用Android Studio Image Asset工具

1. 在Android Studio中打开项目
2. 右键点击 `app` → `New` → `Image Asset`
3. 选择 `Launcher Icons (Adaptive and Legacy)`
4. 在 `Foreground Layer` 选择 `Image` → 浏览选择 `web_frontend/public/logo.png`
5. 调整图标的缩放和位置
6. 点击 `Next` → `Finish`

这将自动生成所有分辨率的图标文件到 `res/mipmap-*` 目录。

---

## 二、QQ一键登录集成

### 步骤1：下载QQ SDK

1. 访问：https://wiki.connect.qq.com/qq%e7%99%bb%e5%bd%95sdk%e4%b8%8b%e8%bd%bd
2. 下载最新的 Android SDK（通常是 `open_sdk_xxx.jar`）
3. 将jar文件放到 `adapp/app/libs/` 目录下

### 步骤2：添加依赖

在 `app/build.gradle.kts` 的 `dependencies` 块中添加：

```kotlin
// QQ登录SDK
implementation(files("libs/open_sdk_xxx.jar"))  // 替换为实际文件名
```

### 步骤3：配置AndroidManifest.xml

在 `<application>` 标签内添加：

```xml
<!-- QQ登录回调Activity -->
<activity
    android:name="com.tencent.tauth.AuthActivity"
    android:noHistory="true"
    android:launchMode="singleTask"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="tencent102124978" />  <!-- 你的QQ AppID -->
    </intent-filter>
</activity>

<activity
    android:name="com.tencent.connect.common.AssistActivity"
    android:theme="@android:style/Theme.Translucent.NoTitleBar"
    android:screenOrientation="portrait" />
```

在 `<application>` 标签前添加权限：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### 步骤4：实现LoginActivity

替换 `adapp/app/src/main/java/com/ncu/kotlincalendar/LoginActivity.kt`：

```kotlin
package com.ncu.kotlincalendar

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.api.models.QQLoginRequest
import com.ncu.kotlincalendar.utils.PreferenceManager
import com.tencent.connect.common.Constants
import com.tencent.tauth.IUiListener
import com.tencent.tauth.Tencent
import com.tencent.tauth.UiError
import kotlinx.coroutines.launch
import org.json.JSONObject

class LoginActivity : AppCompatActivity() {
    
    private lateinit var mTencent: Tencent
    private lateinit var btnQQLogin: Button
    
    companion object {
        private const val TAG = "LoginActivity"
        private const val APP_ID = "102124978"  // 你的QQ互联AppID
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        
        // 设置ActionBar
        supportActionBar?.apply {
            title = "登录"
            setDisplayHomeAsUpEnabled(true)
        }
        
        // 初始化Tencent SDK
        mTencent = Tencent.createInstance(APP_ID, applicationContext)
        
        initViews()
    }
    
    private fun initViews() {
        btnQQLogin = findViewById(R.id.btnQQLogin)
        
        btnQQLogin.setOnClickListener {
            loginWithQQ()
        }
    }
    
    /**
     * QQ登录
     */
    private fun loginWithQQ() {
        if (!mTencent.isSessionValid) {
            mTencent.login(this, "all", object : IUiListener {
                override fun onComplete(response: Any?) {
                    Log.d(TAG, "QQ登录回调: $response")
                    if (response is JSONObject) {
                        handleQQLoginSuccess(response)
                    }
                }
                
                override fun onError(error: UiError?) {
                    Log.e(TAG, "QQ登录失败: ${error?.errorMessage}")
                    Toast.makeText(this@LoginActivity, "登录失败: ${error?.errorMessage}", Toast.LENGTH_SHORT).show()
                }
                
                override fun onCancel() {
                    Log.d(TAG, "QQ登录取消")
                    Toast.makeText(this@LoginActivity, "登录已取消", Toast.LENGTH_SHORT).show()
                }
                
                override fun onWarning(p0: Int) {
                    Log.w(TAG, "QQ登录警告: $p0")
                }
            })
        }
    }
    
    /**
     * 处理QQ登录成功
     */
    private fun handleQQLoginSuccess(response: JSONObject) {
        try {
            val accessToken = response.getString(Constants.PARAM_ACCESS_TOKEN)
            val expires = response.getString(Constants.PARAM_EXPIRES_IN)
            val openid = response.getString(Constants.PARAM_OPEN_ID)
            
            Log.d(TAG, "QQ登录成功 - AccessToken: $accessToken, OpenID: $openid")
            
            // 保存QQ登录信息到Tencent对象
            mTencent.setAccessToken(accessToken, expires)
            mTencent.openId = openid
            
            // 调用后端验证并获取JWT Token
            callBackendLogin(accessToken, openid)
            
        } catch (e: Exception) {
            Log.e(TAG, "解析QQ登录响应失败", e)
            Toast.makeText(this, "登录失败: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    /**
     * 调用后端API进行登录验证
     */
    private fun callBackendLogin(accessToken: String, openid: String) {
        lifecycleScope.launch {
            try {
                val request = QQLoginRequest(accessToken, openid)
                val response = RetrofitClient.authService.qqLogin(request)
                
                if (response.isSuccessful) {
                    val authResponse = response.body()
                    if (authResponse != null) {
                        // 保存JWT Token和用户信息
                        PreferenceManager.saveTokens(
                            this@LoginActivity,
                            authResponse.access,
                            authResponse.refresh
                        )
                        PreferenceManager.saveUserInfo(
                            this@LoginActivity,
                            authResponse.user.id,
                            authResponse.user.username,
                            authResponse.user.email
                        )
                        
                        Log.d(TAG, "后端验证成功，用户: ${authResponse.user.username}")
                        Toast.makeText(this@LoginActivity, "登录成功！", Toast.LENGTH_SHORT).show()
                        
                        // 返回成功结果
                        setResult(RESULT_OK)
                        finish()
                    } else {
                        Toast.makeText(this@LoginActivity, "后端响应为空", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val errorBody = response.errorBody()?.string() ?: "未知错误"
                    Log.e(TAG, "后端验证失败: ${response.code()} - $errorBody")
                    Toast.makeText(this@LoginActivity, "后端验证失败: ${response.code()}", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Log.e(TAG, "后端登录请求失败", e)
                Toast.makeText(this@LoginActivity, "网络错误: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        Tencent.onActivityResultData(requestCode, resultCode, data, null)
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
```

### 步骤5：配置QQ互联信息

1. 访问 https://connect.qq.com/
2. 创建或管理你的应用
3. 获取 `APP ID` 和 `APP KEY`
4. 在代码中替换 `APP_ID = "102124978"` 为你的实际AppID
5. 配置回调地址为：`auth://tencent.com`（或在QQ互联后台配置的地址）

### 步骤6：后端API

后端已经实现了QQ登录接口：

- **URL**: `POST /api/auth/qq/login/`
- **请求体**:
  ```json
  {
    "access_token": "QQ返回的access_token",
    "openid": "QQ返回的openid"
  }
  ```
- **响应**:
  ```json
  {
    "access": "JWT access token",
    "refresh": "JWT refresh token",
    "user": {
      "id": 1,
      "username": "用户名",
      "email": "email@example.com"
    }
  }
  ```

### 测试流程

1. 构建并安装应用到测试设备
2. 点击"云端模式"按钮
3. 点击"去登录"
4. 点击"QQ登录"按钮
5. 完成QQ授权
6. 验证登录成功并自动切换到云端模式

---

## 注意事项

1. **QQ SDK版本**: 建议使用最新的3.5.x版本
2. **混淆配置**: 如果启用了ProGuard，需要添加QQ SDK的混淆规则
3. **签名问题**: QQ登录需要配置应用签名，确保测试和发布签名都在QQ互联后台配置
4. **网络权限**: 确保AndroidManifest.xml中已添加INTERNET权限
5. **测试环境**: 建议先在测试环境验证，再切换到生产环境

---

## 常见问题

### Q: 提示"应用签名不匹配"
A: 需要在QQ互联后台配置应用的签名SHA1值

### Q: 回调失败
A: 检查AndroidManifest.xml中的scheme配置是否正确（tencent + AppID）

### Q: 后端验证失败
A: 检查后端API是否正常运行，以及网络连接是否正常

---

**完成以上步骤后，Android端就可以使用QQ一键登录了！** 🎉

