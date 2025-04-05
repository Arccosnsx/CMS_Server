<template>
    <div v-if="visible" class="context-menu" :style="{ top: `${position.y}px`, left: `${position.x}px` }" @click.stop
        v-click-outside="closeMenu">
        <div v-for="item in menuItems" :key="item.id" class="menu-item" @click="handleMenuItemClick(item.action)">
            <span class="menu-icon">{{ item.icon }}</span>
            <span class="menu-text">{{ item.text }}</span>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        position: {
            type: Object,
            default: () => ({ x: 0, y: 0 })
        },
        targetItem: {
            type: Object,
            default: null
        }
    },
    data() {
        return {
            menuItems: [
                { id: 'download', text: '下载', icon: '⏬', action: 'download' },
                { id: 'rename', text: '重命名', icon: '✏️', action: 'rename' },
                { id: 'move', text: '移动', icon: '↗️', action: 'move' },
                { id: 'properties', text: '属性', icon: 'ℹ️', action: 'properties' }
            ]
        }
    },
    methods: {
        closeMenu() {
            this.$emit('close')
        },
        handleMenuItemClick(action) {
            this.$emit('action', { action, item: this.targetItem })
            this.closeMenu()
        }
    },
    directives: {
        'click-outside': {
            bind(el, binding, vnode) {
                el.clickOutsideEvent = function (event) {
                    if (!(el === event.target || el.contains(event.target))) {
                        vnode.context[binding.expression](event)
                    }
                }
                document.body.addEventListener('click', el.clickOutsideEvent)
            },
            unbind(el) {
                document.body.removeEventListener('click', el.clickOutsideEvent)
            }
        }
    }
}
</script>

<style scoped>
.context-menu {
    position: fixed;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 160px;
    padding: 4px 0;
}

.menu-item {
    padding: 8px 16px;
    display: flex;
    align-items: center;
    cursor: pointer;
}

.menu-item:hover {
    background-color: #f0f0f0;
}

.menu-icon {
    margin-right: 8px;
    width: 20px;
    text-align: center;
}

.menu-text {
    flex: 1;
}
</style>