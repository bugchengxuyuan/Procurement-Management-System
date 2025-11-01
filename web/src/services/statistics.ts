/**
 * 统计API服务
 */
import api from './api'
import type { DashboardStats, PaymentDue } from '@/types'

export const statisticsApi = {
  // 获取仪表盘统计数据
  getDashboard: (startDate?: string, endDate?: string) => {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return api.get<any, DashboardStats>('/statistics/dashboard', { params })
  },

  // 获取账期跟踪列表
  getPaymentDue: () => {
    return api.get<any, PaymentDue[]>('/statistics/payment-due')
  },
}
