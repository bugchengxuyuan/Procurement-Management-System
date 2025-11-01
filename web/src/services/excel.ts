/**
 * Excel导入导出API服务
 */
import api from './api'

export const excelApi = {
  // 导入Excel
  importOrders: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<any, { success_count: number; error_count: number; errors: any[] }>(
      '/excel/import',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
  },

  // 导出Excel
  exportOrders: async () => {
    const response = await api.get('/excel/export', {
      responseType: 'blob',
    })

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response as any]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `orders_${Date.now()}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },
}
