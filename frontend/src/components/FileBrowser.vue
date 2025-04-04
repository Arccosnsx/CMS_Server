<template>
    <div class="file-browser">
        <div class="breadcrumb">
            <span v-for="(item, index) in currentPath" :key="index">
                {{ item.name }} /
            </span>
        </div>

        <div class="file-list">
            <div v-for="file in files" :key="file.id" class="file-item">
                <span v-if="file.is_folder">📁</span>
                <span v-else>📄</span>
                {{ file.name }}
            </div>
        </div>
    </div>
</template>

<script>
import { computed } from 'vue'
import { useFilesStore } from '../stores/files.js'

export default {
    setup() {
        const filesStore = useFilesStore()

        return {
            files: computed(() => filesStore.currentFiles),
            currentPath: computed(() => filesStore.currentPath)
        }
    }
}
</script>

<style>
.file-browser {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.breadcrumb {
    margin-bottom: 15px;
    padding-bottom: 5px;
    border-bottom: 1px solid #eee;
}

.file-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
}

.file-item {
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
    cursor: pointer;
}

.file-item:hover {
    background-color: #f5f5f5;
}
</style>