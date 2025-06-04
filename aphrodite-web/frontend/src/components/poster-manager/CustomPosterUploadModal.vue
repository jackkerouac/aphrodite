<template>
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-2xl">
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">Upload Custom Poster</h3>
        <button class="btn btn-sm btn-circle btn-ghost" @click="$emit('close')">✕</button>
      </div>

      <!-- Upload Form -->
      <div class="space-y-6">
        <!-- File Upload Area -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-medium">Select Poster Image</span>
          </label>
          
          <!-- File Drop Zone -->
          <div 
            class="border-2 border-dashed border-base-300 rounded-lg p-8 text-center transition-colors cursor-pointer"
            :class="{
              'border-primary bg-primary/10': isDragOver,
              'border-error bg-error/10': uploadError
            }"
            @drop="handleDrop"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @click="triggerFileInput"
          >
            <input 
              ref="fileInput"
              type="file"
              class="hidden"
              accept=".jpg,.jpeg,.png,.webp,.gif"
              @change="handleFileSelect"
            />
            
            <div v-if="!selectedFile" class="space-y-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-base-content/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <div class="text-base-content/70">
                <p class="font-medium">Drop your poster here or click to browse</p>
                <p class="text-sm">Supports JPG, PNG, WebP, GIF files</p>
              </div>
            </div>
            
            <div v-else class="space-y-3">
              <!-- File Preview -->
              <div class="flex items-center justify-center space-x-3">
                <img 
                  v-if="previewUrl" 
                  :src="previewUrl" 
                  alt="Preview" 
                  class="h-20 w-20 object-cover rounded"
                />
                <div class="text-left">
                  <p class="font-medium">{{ selectedFile.name }}</p>
                  <p class="text-sm text-base-content/70">{{ formatFileSize(selectedFile.size) }}</p>
                  <p class="text-sm text-base-content/70">{{ imageDimensions }}</p>
                </div>
              </div>
              
              <button 
                type="button" 
                class="btn btn-sm btn-outline"
                @click.stop="clearFile"
              >
                Choose Different File
              </button>
            </div>
          </div>
          
          <label v-if="uploadError" class="label">
            <span class="label-text-alt text-error">{{ uploadError }}</span>
          </label>
        </div>

        <!-- Badge Application Option -->
        <div class="form-control">
          <label class="label cursor-pointer">
            <span class="label-text">
              <span class="font-medium">Apply Badges</span>
              <span class="text-sm text-base-content/70 block">Add audio, resolution, and review badges to the poster</span>
            </span>
            <input 
              v-model="applyBadges" 
              type="checkbox" 
              class="toggle toggle-primary" 
            />
          </label>
        </div>

        <!-- Info Alert -->
        <div class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm">
            <p>The uploaded image will be resized to 1000px width and saved as the new poster for this item.</p>
            <p class="mt-1">The original poster will be replaced in both Aphrodite and Jellyfin.</p>
          </div>
        </div>
      </div>

      <!-- Modal Actions -->
      <div class="modal-action">
        <button 
          class="btn btn-ghost" 
          @click="$emit('close')"
          :disabled="isUploading"
        >
          Cancel
        </button>
        <button 
          class="btn btn-primary" 
          @click="uploadPoster"
          :disabled="!selectedFile || isUploading"
        >
          <span v-if="isUploading" class="loading loading-spinner loading-sm"></span>
          {{ isUploading ? 'Uploading...' : 'Upload Poster' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onUnmounted } from 'vue'

export default {
  name: 'CustomPosterUploadModal',
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'upload-started'],
  setup(props, { emit }) {
    const fileInput = ref(null)
    const selectedFile = ref(null)
    const previewUrl = ref(null)
    const applyBadges = ref(true)
    const isUploading = ref(false)
    const uploadError = ref(null)
    const isDragOver = ref(false)
    const imageDimensions = ref('')

    // File handling methods
    const triggerFileInput = () => {
      if (!isUploading.value) {
        fileInput.value.click()
      }
    }

    const validateFile = (file) => {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
      const maxSize = 50 * 1024 * 1024 // 50MB
      
      if (!allowedTypes.includes(file.type)) {
        return 'Invalid file type. Please upload a JPG, PNG, WebP, or GIF image.'
      }
      
      if (file.size > maxSize) {
        return 'File too large. Maximum size is 50MB.'
      }
      
      return null
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        processFile(file)
      }
    }

    const processFile = (file) => {
      uploadError.value = validateFile(file)
      if (uploadError.value) {
        return
      }
      
      selectedFile.value = file
      
      // Create preview URL
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
      }
      previewUrl.value = URL.createObjectURL(file)
      
      // Get image dimensions
      const img = new Image()
      img.onload = () => {
        imageDimensions.value = `${img.width} × ${img.height}px`
      }
      img.src = previewUrl.value
    }

    const clearFile = () => {
      selectedFile.value = null
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
        previewUrl.value = null
      }
      imageDimensions.value = ''
      uploadError.value = null
      fileInput.value.value = ''
    }

    // Drag and drop handlers
    const handleDragOver = (event) => {
      event.preventDefault()
      isDragOver.value = true
    }

    const handleDragLeave = (event) => {
      event.preventDefault()
      isDragOver.value = false
    }

    const handleDrop = (event) => {
      event.preventDefault()
      isDragOver.value = false
      
      const files = event.dataTransfer.files
      if (files.length > 0) {
        processFile(files[0])
      }
    }

    // Upload method
    const uploadPoster = async () => {
      if (!selectedFile.value || isUploading.value) {
        return
      }
      
      isUploading.value = true
      uploadError.value = null
      
      try {
        const formData = new FormData()
        formData.append('poster', selectedFile.value)
        formData.append('apply_badges', applyBadges.value.toString())
        
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/upload-custom`, {
          method: 'POST',
          body: formData
        })
        
        const data = await response.json()
        
        if (data.success) {
          // Emit success event with job details
          emit('upload-started', {
            jobId: data.jobId,
            message: data.message,
            applyBadges: applyBadges.value
          })
        } else {
          uploadError.value = data.message || 'Upload failed'
          isUploading.value = false
        }
      } catch (error) {
        console.error('Upload error:', error)
        uploadError.value = 'Network error occurred during upload'
        isUploading.value = false
      }
    }

    // Utility methods
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    // Cleanup on unmount
    onUnmounted(() => {
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
      }
    })

    return {
      fileInput,
      selectedFile,
      previewUrl,
      applyBadges,
      isUploading,
      uploadError,
      isDragOver,
      imageDimensions,
      triggerFileInput,
      handleFileSelect,
      clearFile,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      uploadPoster,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.border-dashed {
  border-style: dashed;
}
</style>
