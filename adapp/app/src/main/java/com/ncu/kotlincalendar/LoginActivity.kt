package com.ncu.kotlincalendar

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.ncu.kotlincalendar.api.client.RetrofitClient
import com.ncu.kotlincalendar.api.services.AuthService
import com.ncu.kotlincalendar.utils.PreferenceManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 登录页面
 * 
 * 使用Web端相同的QQ OAuth2流程，无需QQ SDK：
 * 1. 调用后端获取QQ授权URL
 * 2. 在WebView中打开授权页面
 * 3. 拦截回调URL，提取code
 * 4. 调用后端接口获取JWT token
 */
class LoginActivity : AppCompatActivity() {
    
    private lateinit var btnQQLogin: Button
    private lateinit var loginContainer: View
    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var authService: AuthService
    
    companion object {
        private const val TAG = "LoginActivity"
        private const val QQ_CALLBACK_URL = "https://app7626.acapp.acwing.com.cn/qq/callback"
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)
        
        // 设置ActionBar
        supportActionBar?.apply {
            title = "登录"
            setDisplayHomeAsUpEnabled(true)
        }
        
        authService = RetrofitClient.authService
        initViews()
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun initViews() {
        btnQQLogin = findViewById(R.id.btnQQLogin)
        loginContainer = findViewById(R.id.loginContainer)
        webView = findViewById(R.id.webView)
        progressBar = findViewById(R.id.progressBar)
        
        // 配置WebView
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            javaScriptCanOpenWindowsAutomatically = true
        }
        
        // 设置WebViewClient拦截回调URL
        webView.webViewClient = object : WebViewClient() {
            // 处理URL的逻辑（抽取为通用方法）
            private fun handleUrl(url: String?): Boolean {
                if (url == null) return false
                
                Log.d(TAG, "加载URL: $url")
                
                // 拦截QQ回调URL
                if (url.startsWith(QQ_CALLBACK_URL)) {
                    handleQQCallback(url)
                    return true // 拦截，不继续加载
                }
                
                // 处理QQ自定义协议（尝试打开QQ客户端）
                if (url.startsWith("wtloginmqq://") || url.startsWith("mqqapi://") || url.startsWith("tencent://")) {
                    try {
                        val intent = Intent(Intent.ACTION_VIEW, android.net.Uri.parse(url))
                        if (intent.resolveActivity(packageManager) != null) {
                            startActivity(intent)
                            return true // 拦截，已用Intent处理
                        } else {
                            // 如果没有安装QQ客户端，提示用户
                            Toast.makeText(this@LoginActivity, "请先安装QQ客户端", Toast.LENGTH_LONG).show()
                            return true
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "打开QQ客户端失败", e)
                        Toast.makeText(this@LoginActivity, "无法打开QQ客户端", Toast.LENGTH_SHORT).show()
                        return true
                    }
                }
                
                return false // 继续加载其他URL
            }
            
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString()
                return handleUrl(url)
            }
            
            // 兼容旧版本Android（API < 24）
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return handleUrl(url)
            }
            
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
            }
        }
        
        // 默认隐藏WebView
        webView.visibility = View.GONE
        progressBar.visibility = View.GONE
        
        btnQQLogin.setOnClickListener {
            startQQLogin()
        }
    }
    
    /**
     * 开始QQ登录流程
     */
    private fun startQQLogin() {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                progressBar.visibility = View.VISIBLE
                
                // 1. 调用后端获取QQ授权URL
                val response = withContext(Dispatchers.IO) {
                    authService.getQQLoginUrl()
                }
                
                if (response.isSuccessful && response.body() != null) {
                    val authUrl = response.body()!!.applyCodeUrl
                    Log.d(TAG, "QQ授权URL: $authUrl")
                    
                    // 2. 在WebView中打开授权页面
                    loginContainer.visibility = View.GONE
                    webView.visibility = View.VISIBLE
                    webView.loadUrl(authUrl)
                    
                } else {
                    progressBar.visibility = View.GONE
                    Toast.makeText(this@LoginActivity, "获取授权URL失败", Toast.LENGTH_SHORT).show()
                }
                
            } catch (e: Exception) {
                progressBar.visibility = View.GONE
                Log.e(TAG, "QQ登录失败", e)
                Toast.makeText(this@LoginActivity, "登录失败: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    /**
     * 处理QQ回调URL，提取code并调用后端接口
     */
    private fun handleQQCallback(url: String) {
        Log.d(TAG, "处理QQ回调: $url")
        
        try {
            // 解析URL参数
            val uri = android.net.Uri.parse(url)
            val code = uri.getQueryParameter("code")
            val state = uri.getQueryParameter("state")
            
            if (code == null) {
                Toast.makeText(this, "授权失败：缺少授权码", Toast.LENGTH_SHORT).show()
                loginContainer.visibility = View.VISIBLE
                webView.visibility = View.GONE
                return
            }
            
            // 调用后端接口获取JWT token
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    progressBar.visibility = View.VISIBLE
                    
                    val response = withContext(Dispatchers.IO) {
                        authService.qqLogin(com.ncu.kotlincalendar.api.models.QQLoginRequest(code))
                    }
                    
                    if (response.isSuccessful && response.body() != null) {
                        val loginResponse = response.body()!!
                        
                        // 保存JWT token
                        if (loginResponse.access != null) {
                            PreferenceManager.saveAccessToken(this@LoginActivity, loginResponse.access!!)
                            if (loginResponse.refresh != null) {
                                PreferenceManager.saveRefreshToken(this@LoginActivity, loginResponse.refresh!!)
                            }
                            
                            // 保存用户信息（如果有）
                            loginResponse.user?.let { user ->
                                PreferenceManager.saveUserInfo(this@LoginActivity, user.id, user.username, user.email)
                            }
                            
                            Toast.makeText(this@LoginActivity, "登录成功！", Toast.LENGTH_SHORT).show()
                            
                            // 返回设置页
                            val resultIntent = Intent()
                            resultIntent.putExtra("login_success", true)
                            setResult(RESULT_OK, resultIntent)
                            finish()
                            
                        } else {
                            Toast.makeText(this@LoginActivity, "登录失败：未获取到token", Toast.LENGTH_SHORT).show()
                            loginContainer.visibility = View.VISIBLE
                            webView.visibility = View.GONE
                        }
                        
                    } else {
                        val errorBody = response.errorBody()?.string() ?: "未知错误"
                        Log.e(TAG, "登录失败: ${response.code()}, $errorBody")
                        Toast.makeText(this@LoginActivity, "登录失败: ${response.message()}", Toast.LENGTH_SHORT).show()
                        loginContainer.visibility = View.VISIBLE
                        webView.visibility = View.GONE
                    }
                    
                    progressBar.visibility = View.GONE
                    
                } catch (e: Exception) {
                    progressBar.visibility = View.GONE
                    Log.e(TAG, "登录失败", e)
                    Toast.makeText(this@LoginActivity, "登录失败: ${e.message}", Toast.LENGTH_SHORT).show()
                    loginContainer.visibility = View.VISIBLE
                    webView.visibility = View.GONE
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "解析回调URL失败", e)
            Toast.makeText(this, "处理回调失败: ${e.message}", Toast.LENGTH_SHORT).show()
            loginContainer.visibility = View.VISIBLE
            webView.visibility = View.GONE
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    override fun onBackPressed() {
        if (webView.visibility == View.VISIBLE && webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}

