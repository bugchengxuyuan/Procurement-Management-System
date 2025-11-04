/**
 * Supplier API Service
 */
import api from './api';

export interface SupplierListItem {
  supplier_name: string;
  order_count: number;
  total_amount: number;
  product_count: number;
  last_order_date: string;
  first_order_date: string;
}

export interface SupplierListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: 'total_amount' | 'order_count' | 'last_order_date';
  sort_order?: 'desc' | 'asc';
}

export interface SupplierListResponse {
  total: number;
  page: number;
  size: number;
  items: SupplierListItem[];
}

export interface MonthlyTrend {
  month: string;
  amount: number;
  count: number;
}

export interface SupplierProduct {
  product_name: string;
  spec: string | null;
  order_count: number;
  total_amount: number;
  avg_amount: number;
}

export interface SupplierStats {
  supplier_name: string;
  order_count: number;
  total_amount: number;
  product_count: number;
  last_order_date: string;
  first_order_date: string;
  monthly_trend: MonthlyTrend[];
  products: SupplierProduct[];
}

export interface SupplierOrdersParams {
  page?: number;
  page_size?: number;
  product_name?: string;
  spec?: string;
  start_date?: string;
  end_date?: string;
}

// Get supplier list
export const getSupplierList = (params: SupplierListParams): Promise<SupplierListResponse> => {
  return api.get('/suppliers/list', { params });
};

// Get supplier stats
export const getSupplierStats = (supplierName: string): Promise<SupplierStats> => {
  return api.get(`/suppliers/${encodeURIComponent(supplierName)}/stats`);
};

// Get supplier orders
export const getSupplierOrders = (
  supplierName: string,
  params: SupplierOrdersParams
): Promise<{ total: number; page: number; size: number; items: any[] }> => {
  return api.get(`/suppliers/${encodeURIComponent(supplierName)}/orders`, { params });
};
