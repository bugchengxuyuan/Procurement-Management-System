/**
 * 订单API服务
 */
import api from './api'
import type { Order, OrderCreate, OrderUpdate, PaginatedResponse } from '@/types'

export interface OrderListParams {
  page?: number
  page_size?: number
  product_name?: string
  order_status?: string
  payment_method?: string
  start_date?: string
  end_date?: string
  search?: string
}

export const orderApi = {
  // 获取订单列表
  getOrders: (params: OrderListParams = {}) => {
    return api.get<any, PaginatedResponse<Order>>('/orders', { params })
  },

  // 获取订单详情
  getOrder: (id: number) => {
    return api.get<any, Order>(`/orders/${id}`)
  },

  // 创建订单
  createOrder: (data: OrderCreate) => {
    return api.post<any, Order>('/orders', data)
  },

  // 更新订单
  updateOrder: (id: number, data: OrderUpdate) => {
    return api.put<any, Order>(`/orders/${id}`, data)
  },

  // 删除订单
  deleteOrder: (id: number) => {
    return api.delete<any, { message: string }>(`/orders/${id}`)
  },
}
