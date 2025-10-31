/**
 * 类型定义
 */

export interface PurchaseOrder {
  id: number;
  order_no: string;
  product_name: string;
  purchase_amount: number;
  order_date?: string;
  order_time?: string;
  initial_status?: string;
  payment_status?: string;
  shop_name: string;
  created_at?: string;
  updated_at?: string;
}

export interface OrderListResponse {
  total: number;
  orders: PurchaseOrder[];
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Statistics {
  total_amount: number;
  total_orders: number;
  total_products: number;
  shop_stats: {
    shop_name: string;
    total_amount: number;
    order_count: number;
  }[];
  payment_stats: {
    payment_status: string;
    total_amount: number;
    order_count: number;
  }[];
}

export interface ProductStats {
  product_name: string;
  total_amount: number;
  order_count: number;
  avg_amount: number;
  percentage: number;
}

export interface OrderFilters {
  start_date?: string;
  end_date?: string;
  shop_name?: string;
  product_name?: string;
  payment_status?: string;
  search?: string;
}
