const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
const MAX_WIDTH = 1920
const QUALITY = 0.8

export function validateImage(file) {
  if (!file) {
    return { valid: false, error: '请选择图片文件' }
  }
  if (!ALLOWED_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: `不支持的文件格式「${file.name}」，仅支持 JPG、PNG、WebP 格式`
    }
  }
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    const sizeKB = Math.round(file.size / 1024)
    return {
      valid: false,
      error: `文件过大「${file.name}」(${sizeKB}KB)，单张图片最大支持 5MB`
    }
  }
  return { valid: true }
}

export function compressImage(file, options = {}) {
  const maxWidth = options.maxWidth || MAX_WIDTH
  const quality = options.quality || QUALITY

  return new Promise((resolve, reject) => {
    if (!file || !file.type.startsWith('image/')) {
      reject(new Error('无效的图片文件'))
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        let { width, height } = img

        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width)
          width = maxWidth
        }

        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height

        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)

        let mimeType = file.type
        if (file.type === 'image/jpg') mimeType = 'image/jpeg'

        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('图片压缩失败'))
              return
            }

            const compressedFile = new File([blob], file.name, {
              type: mimeType,
              lastModified: Date.now()
            })

            resolve({
              file: compressedFile,
              originalSize: file.size,
              compressedSize: blob.size,
              width,
              height
            })
          },
          mimeType,
          quality
        )
      }
      img.onerror = () => reject(new Error('图片加载失败'))
      img.src = e.target.result
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsDataURL(file)
  })
}

export async function compressImages(files, options = {}) {
  const results = []
  for (const file of files) {
    const validation = validateImage(file)
    if (!validation.valid) {
      results.push({ file, error: validation.error })
      continue
    }
    try {
      const result = await compressImage(file, options)
      results.push({ file: result.file, originalFile: file, ...result })
    } catch (e) {
      results.push({ file, error: e.message })
    }
  }
  return results
}
