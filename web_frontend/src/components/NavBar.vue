<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
    <div class="container-fluid">
      <!-- Logo -->
      <a class="navbar-brand" href="/">
        <span class="brand-icon">📅</span>
        <span class="brand-text">KotlinCalendar</span>
      </a>
      
      <!-- 移动端折叠按钮 -->
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <!-- 导航菜单 -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">
              <i class="bi bi-calendar3"></i> 日历
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#" @click.prevent="$emit('subscribe')">
              <i class="bi bi-rss"></i> 订阅
            </a>
          </li>
          <li class="nav-item dropdown">
            <a 
              class="nav-link dropdown-toggle" 
              href="#" 
              id="userDropdown" 
              role="button" 
              data-bs-toggle="dropdown"
            >
              <i class="bi bi-person-circle"></i> 游客
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><a class="dropdown-item" href="#" @click.prevent="$emit('login')">
                🔑 登录
              </a></li>
              <li><a class="dropdown-item" href="#" @click.prevent="$emit('register')">
                ✍️ 注册
              </a></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item" href="#" @click.prevent="$emit('logout')">
                🚪 退出
              </a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
defineEmits(['login', 'register', 'logout', 'subscribe'])
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 12px 0;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 24px;
}

.brand-icon { font-size: 28px; }

.brand-text {
  background: linear-gradient(135deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 500;
  padding: 8px 16px !important;
  border-radius: 8px;
  transition: all 0.3s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff !important;
  transform: translateY(-2px);
}

.dropdown-menu {
  border-radius: 12px;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  padding: 8px;
}

.dropdown-item {
  border-radius: 8px;
  padding: 10px 16px;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  transform: translateX(4px);
}
</style>

