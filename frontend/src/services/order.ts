/**
 * Order API Service
 */
import api from './api';

export interface Order {
  id: number;
  order_no: string;
  product_name: string;
  spec?: string | null;
  purchase_amount: number;
  supplier?: string | null;
  order_date: string;
  order_status: string;
  payment_method: string;
  record_time: string;
  created_at: string;
  updated_at: string;
}

export interface OrderListParams {
  page?: number;
  size?: number;
  product_name?: string;
  spec?: string;
  supplier?: string;
  order_status?: string;
  payment_method?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}

export interface OrderListResponse {
  total: number;
  page: number;
  size: number;
  items: Order[];
}

export interface OrderCreateParams {
  order_no: string;
  product_name: string;
  spec?: string;
  purchase_amount: number;
  supplier?: string;
  order_date: string;
  order_status: string;
  payment_method: string;
  record_time?: string;
}

export interface OrderUpdateParams {
  product_name?: string;
  spec?: string;
  purchase_amount?: number;
  supplier?: string;
  order_date?: string;
  order_status?: string;
  payment_method?: string;
  record_time?: string;
}

// Get order list
export const getOrders = (params: OrderListParams): Promise<OrderListResponse> => {
  return api.get('/orders', { params });
};

// Get order by ID
export const getOrder = (id: number): Promise<Order> => {
  return api.get(`/orders/${id}`);
};

// Create order
export const createOrder = (data: OrderCreateParams): Promise<Order> => {
  return api.post('/orders', data);
};

// Update order
export const updateOrder = (id: number, data: OrderUpdateParams): Promise<Order> => {
  return api.put(`/orders/${id}`, data);
};

// Delete order
export const deleteOrder = (id: number): Promise<{ message: string }> => {
  return api.delete(`/orders/${id}`);
};
