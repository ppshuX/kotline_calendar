// ====================================
// 🔐 认证 Token 调试脚本
// ====================================
// 
// 使用方法：
// 1. 打开 Ralendar 网站
// 2. 按 F12 打开开发者工具
// 3. 切换到 Console（控制台）标签
// 4. 复制下面的代码，粘贴到控制台并按回车
//
// ====================================

console.clear();
console.log('====================================');
console.log('🔐 认证 Token 诊断');
console.log('====================================\n');

// 1. 检查 LocalStorage 中的 Token
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

console.log('===== 1. Token 存储状态 =====\n');

if (accessToken) {
    console.log('✅ Access Token 存在');
    console.log('   长度:', accessToken.length + ' 字符');
    console.log('   前20字符:', accessToken.substring(0, 20) + '...');
    
    // 解析 JWT Token
    try {
        const parts = accessToken.split('.');
        if (parts.length === 3) {
            const payload = JSON.parse(atob(parts[1]));
            console.log('\n📋 Token 信息:');
            console.log('   用户 ID:', payload.user_id);
            console.log('   签发时间:', new Date(payload.iat * 1000).toLocaleString());
            console.log('   过期时间:', new Date(payload.exp * 1000).toLocaleString());
            
            const now = Date.now() / 1000;
            const remaining = payload.exp - now;
            if (remaining > 0) {
                console.log(`   ✅ Token 有效，剩余 ${Math.floor(remaining / 60)} 分钟`);
            } else {
                console.log(`   ❌ Token 已过期 ${Math.floor(-remaining / 60)} 分钟`);
            }
        }
    } catch (e) {
        console.error('   ⚠️ Token 格式无效:', e.message);
    }
} else {
    console.log('❌ Access Token 不存在！');
}

console.log('');

if (refreshToken) {
    console.log('✅ Refresh Token 存在');
    console.log('   长度:', refreshToken.length + ' 字符');
} else {
    console.log('❌ Refresh Token 不存在！');
}

console.log('\n===== 2. 测试 API 请求 =====\n');

// 2. 测试 API 请求
fetch('https://app7626.acapp.acwing.com.cn/api/events/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
})
.then(response => {
    console.log('API 响应状态:', response.status, response.statusText);
    
    if (response.status === 200) {
        console.log('✅ Token 有效，API 请求成功');
        return response.json();
    } else if (response.status === 401) {
        console.log('❌ Token 无效或已过期（401 Unauthorized）');
        console.log('\n💡 建议操作：');
        console.log('   1. 重新登录');
        console.log('   2. 或执行: localStorage.clear(); location.reload();');
    } else {
        console.log('⚠️ 其他错误:', response.status);
    }
    return response.text();
})
.then(data => {
    if (typeof data === 'string') {
        try {
            const json = JSON.parse(data);
            console.log('\n📦 响应数据:', json);
        } catch (e) {
            console.log('\n📦 响应文本:', data);
        }
    } else {
        console.log('\n📦 响应数据:', data);
    }
})
.catch(error => {
    console.error('❌ 请求失败:', error.message);
});

console.log('\n===== 3. 当前用户信息 =====\n');

// 3. 检查用户信息
fetch('https://app7626.acapp.acwing.com.cn/api/auth/me/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(user => {
    console.log('✅ 当前登录用户:');
    console.log('   用户名:', user.username);
    console.log('   邮箱:', user.email || '(未设置)');
    console.log('   用户 ID:', user.id);
})
.catch(error => {
    console.error('❌ 获取用户信息失败:', error.message);
    console.log('\n💡 可能的原因：');
    console.log('   - Token 已过期');
    console.log('   - 用户未登录');
    console.log('   - 网络连接问题');
});

console.log('\n====================================');
console.log('💡 快速修复命令：');
console.log('====================================');
console.log('// 清除所有 Token 并刷新页面');
console.log('localStorage.clear(); location.reload();');
console.log('\n// 查看所有 LocalStorage 内容');
console.log('console.table(Object.entries(localStorage));');
console.log('====================================');

