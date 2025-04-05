<template>
    <div v-if="visible" class="upload-modal-overlay" @click.self="closeModal">
        <div class="upload-modal">
            <div class="modal-header">
                <h3>上传文件</h3>
            </div>

            <div class="modal-body">
                <!-- 使用 vue-simple-uploader -->
                <uploader :options="uploadOptions" :file-status-text="statusText" class="uploader-instance"
                    @file-added="handleFileAdded" @file-success="handleFileSuccess" @file-error="handleFileError"
                    @complete="handleUploadComplete" ref="uploaderRef">
                    <!-- 拖拽上传区域 -->
                    <uploader-drop class="upload-drop-area">
                        <p>拖拽文件到此处上传</p>
                        <uploader-btn class="upload-btn" :directory="false">
                            选择文件
                        </uploader-btn>
                    </uploader-drop>

                    <!-- 上传队列列表 -->
                    <uploader-list class="file-upload-list"></uploader-list>
                </uploader>
            </div>

            <div class="modal-footer">
                <button class="cancel-btn" @click="closeModal">取消</button>
                <button class="pause-btn" @click="togglePause" v-if="uploadStarted">
                    {{ isPaused ? '继续上传' : '暂停上传' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useFilesStore } from '../stores/files'
import SparkMD5 from 'spark-md5'
import axios from 'axios';

export default {
    props: {
        visible: {
            type: Boolean,
            default: false
        },
        currentPath: {
            type: String,
            default: '/'
        },
        currentParentId: {
            type: String,
            default: null
        },
    },

    setup(props, { emit }) {
        const filesStore = useFilesStore()
        const uploaderRef = ref(null)
        const uploadStarted = ref(false)
        const isPaused = ref(false)

        // 上传配置（根据你的后端调整）
        const uploadOptions = ref({
            target: 'http://localhost:8000/files/upload/chunk',
            testChunks: true,
            chunkSize: 2 * 1024 * 1024,
            simultaneousUploads: 3,
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
            },
            query: (file) => ({
                identifier: file.uniqueIdentifier,
                filename: file.name,
                parent_id: props.currentParentId,
                space_type: filesStore.currentSpace
            }),
            checkChunkUploadedByResponse: (chunk, message) => {
                const data = JSON.parse(message);
                if (data.skipUpload) {
                    return true;
                }
                return (data.uploaded || []).indexOf(chunk.offset + 1) >= 0;
            }
        });
        

        const handleUploadComplete = async () => {
            const uploader = uploaderRef.value?.uploader;
            if (!uploader) return;

            const successFiles = uploader.fileList.filter(f => f.isComplete());

            for (const file of successFiles) {
                try {
                    // 创建 FormData 对象
                    const formData = new FormData();
                    formData.append('identifier', file.uniqueIdentifier);
                    formData.append('filename', file.name);
                    formData.append('space_type', filesStore.currentSpace);
                    formData.append('parent_id', props.currentParentId);

                    const res = await axios.post('http://localhost:8000/files/upload/merge', formData, {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`,
                            'Content-Type': 'multipart/form-data'  // 明确指定内容类型
                        }
                    });

                    if (res.data) {
                        filesStore.loadFiles(filesStore.currentParentId);
                    }
                } catch (error) {
                    console.error('合并文件失败:', error);
                    if (error.response) {
                        console.error('错误详情:', error.response.data);
                    }
                }
            }
        };

        // 上传状态文本
        const statusText = {
            success: '上传成功',
            error: '上传失败',
            uploading: '上传中',
            paused: '已暂停',
            waiting: '等待中'
        }

        // 文件添加时的校验
        const handleFileAdded = async (file) => {
            uploadStarted.value = true;

            return new Promise((resolve) => {
                const spark = new SparkMD5.ArrayBuffer();
                const reader = new FileReader();

                reader.onload = (e) => {
                    spark.append(e.target.result);
                    file.uniqueIdentifier = spark.end();
                    resolve(true);
                };

                reader.onerror = () => {
                    console.error('文件读取失败');
                    resolve(false);
                };

                reader.readAsArrayBuffer(file.file);
            });
        };

        // 单个文件上传成功
        const handleFileSuccess = (rootFile, file, message) => {
            console.log(`${file.name} 上传成功`, message)
        }

        // 上传出错
        const handleFileError = (rootFile, file, message) => {
            console.error(`${file.name} 上传失败`, message)
        }

        // 暂停/继续上传
        const togglePause = () => {
            if (!uploaderRef.value) return

            const uploader = uploaderRef.value.uploader
            if (isPaused.value) {
                uploader.upload()
            } else {
                uploader.pause()
            }
            isPaused.value = !isPaused.value
        }

        // 关闭模态框
        const closeModal = () => {
            if (uploaderRef.value) {
                uploaderRef.value.uploader.cancel() // 取消所有上传
            }
            emit('close')
        }

        return {
            uploaderRef,
            uploadOptions,
            statusText,
            uploadStarted,
            isPaused,
            handleFileAdded,
            handleFileSuccess,
            handleFileError,
            handleUploadComplete,
            togglePause,
            closeModal
        }
    }
}
</script>

<style scoped>
.upload-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.upload-modal {
    background: white;
    border-radius: 8px;
    width: 600px;
    max-width: 90vw;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.modal-header {
    padding: 16px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-body {
    padding: 16px;
    flex: 1;
    overflow-y: auto;
}

.modal-footer {
    padding: 12px 16px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}

.close-btn {
    font-size: 24px;
    background: none;
    border: none;
    cursor: pointer;
    color: #999;
}

.uploader-instance {
    width: 100%;
    height: 100%;
}

.upload-drop-area {
    border: 2px dashed #ddd;
    border-radius: 8px;
    padding: 40px;
    text-align: center;
    margin-bottom: 16px;
    transition: all 0.3s;
}

.upload-drop-area:hover {
    border-color: #1890ff;
    background-color: #f0f9ff;
}

.upload-btn {
    display: inline-block;
    padding: 8px 16px;
    background: #1890ff;
    color: white;
    border-radius: 4px;
    margin-top: 16px;
    cursor: pointer;
}

.file-upload-list {
    max-height: 300px;
    overflow-y: auto;
    margin-top: 16px;
}

.cancel-btn,
.pause-btn {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.cancel-btn {
    background: #f5f5f5;
    color: black;
    border: 1px solid #d9d9d9;
}

.cancel-btn:hover {
    background: #ffffff;
}

.pause-btn {
    background: #faad14;
    color: white;
    border: 1px solid #faad14;
}

.pause-btn:hover {
    background: #ffb92d;
}
</style>