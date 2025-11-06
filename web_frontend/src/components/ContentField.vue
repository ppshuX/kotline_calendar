<template>
  <div class="content-field">
    <div class="container-fluid">
      <div class="main-card card shadow-lg border-0">
        <div class="card-body p-4">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.content-field {
  padding: 16px;
  min-height: calc(100vh - 60px);
}

.main-card {
  border-radius: 16px;
  background: white;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.main-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .content-field {
    padding: 10px;
  }
}
</style>

