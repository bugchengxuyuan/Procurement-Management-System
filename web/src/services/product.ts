/**
 * 产品API服务
 */
import api from './api'
import type { Product, Order, PaginatedResponse } from '@/types'

export interface ProductListParams {
  page?: number
  page_size?: number
  search?: string
}

export const productApi = {
  // 获取产品列表
  getProducts: (params: ProductListParams = {}) => {
    return api.get<any, PaginatedResponse<Product>>('/products', { params })
  },

  // 获取产品详情
  getProduct: (id: number) => {
    return api.get<any, Product>(`/products/${id}`)
  },

  // 获取产品的所有订单
  getProductOrders: (productName: string) => {
    return api.get<any, Order[]>(`/products/name/${encodeURIComponent(productName)}/orders`)
  },

  // 获取产品月度趋势
  getProductTrend: (productName: string) => {
    return api.get<any, Array<{ month: string; amount: number; count: number }>>(
      `/products/name/${encodeURIComponent(productName)}/trend`
    )
  },
}
