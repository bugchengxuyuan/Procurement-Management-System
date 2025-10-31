/**
 * API服务
 */
import axios from 'axios';
import type { PurchaseOrder, OrderListResponse, Statistics, ProductStats, OrderFilters } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const orderAPI = {
  /**
   * 获取订单列表
   */
  getOrders: (page: number = 1, pageSize: number = 50, filters?: OrderFilters): Promise<OrderListResponse> => {
    return api.get('/orders/', {
      params: {
        page,
        page_size: pageSize,
        ...filters,
      },
    });
  },

  /**
   * 获取订单详情
   */
  getOrder: (id: number): Promise<PurchaseOrder> => {
    return api.get(`/orders/${id}`);
  },

  /**
   * 创建订单
   */
  createOrder: (order: Partial<PurchaseOrder>): Promise<PurchaseOrder> => {
    return api.post('/orders/', order);
  },

  /**
   * 更新订单
   */
  updateOrder: (id: number, order: Partial<PurchaseOrder>): Promise<PurchaseOrder> => {
    return api.put(`/orders/${id}`, order);
  },

  /**
   * 删除订单
   */
  deleteOrder: (id: number): Promise<void> => {
    return api.delete(`/orders/${id}`);
  },

  /**
   * 获取统计数据
   */
  getStatistics: (filters?: OrderFilters): Promise<Statistics> => {
    return api.get('/orders/statistics/summary', { params: filters });
  },

  /**
   * 获取产品统计
   */
  getProductStatistics: (filters?: OrderFilters, limit: number = 50): Promise<ProductStats[]> => {
    return api.get('/orders/statistics/products', {
      params: { ...filters, limit },
    });
  },

  /**
   * 获取待支付订单
   */
  getPendingOrders: (): Promise<PurchaseOrder[]> => {
    return api.get('/orders/payment/pending');
  },

  /**
   * 导入Excel
   */
  importExcel: (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/import-export/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * 导出Excel
   */
  exportExcel: (filters?: OrderFilters): string => {
    const params = new URLSearchParams();
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.shop_name) params.append('shop_name', filters.shop_name);

    return `/api/import-export/export?${params.toString()}`;
  },
};

export default api;
