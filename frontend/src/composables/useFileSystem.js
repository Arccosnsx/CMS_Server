import { ref, computed } from 'vue'
import { useFilesStore } from '@/stores/files'

export default function useFileSystem() {
    const filesStore = useFilesStore()
    const isLoading = ref(false)

    const currentFiles = computed(() => filesStore.files)

    const uploadFile = async (file) => {
        isLoading.value = true
        try {
            await filesStore.uploadFile(file)
            await filesStore.fetchFiles()
        } finally {
            isLoading.value = false
        }
    }

    return {
        currentFiles,
        uploadFile,
        isLoading
    }
}