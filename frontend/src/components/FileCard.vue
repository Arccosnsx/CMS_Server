<template>
  <div 
    class="file-card" 
    @click="handleClick"
    @contextmenu.prevent="showContextMenu"
  >
    <div class="file-icon">
      <span v-if="item.is_folder" class="folder-icon">📁</span>
      <span v-else class="file-icon">📄</span>
    </div>
    <div class="file-name">{{ item.name }}</div>
    <div class="file-meta">
      <span v-if="!item.is_folder">{{ formatSize(item.size) }}</span>
      <span>{{ formatDate(item.updated_at) }}</span>
    </div>

    <!-- 右键菜单 -->
    <div 
      v-if="showMenu" 
      class="context-menu" 
      :style="{ top: menuPosition.y + 'px', left: menuPosition.x + 'px' }"
      @click.stop
    >
      <div class="menu-item" @click="handleMenuAction('download')">下载</div>
      <div class="menu-item" @click="handleMenuAction('rename')">重命名</div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showMenu: false,
      menuPosition: { x: 0, y: 0 }
    }
  },
  methods: {
    handleClick() {
      this.$emit('click', this.item)
    },
    formatSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    showContextMenu(event) {
      this.menuPosition = {
        x: event.clientX,
        y: event.clientY
      }
      this.showMenu = true
      // 点击其他地方关闭菜单
      const closeMenu = () => {
        this.showMenu = false
        document.removeEventListener('click', closeMenu)
      }
      document.addEventListener('click', closeMenu)
    },
    handleMenuAction(action) {
      this.$emit('menu-action', { action, file: this.item })
      this.showMenu = false
    }
  }
}
</script>

<style scoped>
/* 原有样式保持不变 */
.file-card {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative; /* 新增，为菜单定位做准备 */
}

.file-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.file-icon {
  font-size: 40px;
  margin-bottom: 10px;
  text-align: center;
}

.folder-icon {
  color: #1890ff;
}

.file-name {
  font-weight: 500;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

/* 新增右键菜单样式 */
.context-menu {
  position: absolute; /* 改为相对于卡片定位 */
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 900;
  min-width: 120px;
  max-width: 200px;
  padding: 4px 0;
  transform: translate(0, 0); /* 确保精确定位 */
}


.menu-item {
  padding: 8px 12px;
  cursor: pointer;
}

.menu-item:hover {
  background-color: #f0f0f0;
}
</style>