<template>
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">上传文件</h3>
                    <button @click="$emit('close')" class="text-gray-400 hover:text-gray-500">
                        <span class="sr-only">关闭</span>
                        <XIcon class="h-6 w-6" />
                    </button>
                </div>

                <div class="mt-2">
                    <input type="file" ref="fileInput" @change="handleFileChange" />
                </div>

                <div class="mt-5 flex justify-end space-x-3">
                    <button type="button" @click="$emit('close')"
                        class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                        取消
                    </button>
                    <button type="button" @click="handleUpload"
                        class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                        :disabled="!selectedFile">
                        上传
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { XIcon } from '@heroicons/vue/outline'

const emit = defineEmits(['close', 'upload'])
const fileInput = ref(null)
const selectedFile = ref(null)

const handleFileChange = (e) => {
    selectedFile.value = e.target.files[0]
}

const handleUpload = () => {
    if (selectedFile.value) {
        emit('upload', selectedFile.value)
        emit('close')
    }
}
</script>