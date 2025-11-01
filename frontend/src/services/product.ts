/**
 * Product API Service
 */
import api from './api';

export interface Product {
  id: number;
  product_name: string;
  total_purchase_amount: number;
  total_order_count: number;
  avg_unit_price: number;
  last_purchase_date: string | null;
  created_at: string;
  updated_at: string;
  percentage?: number;
}

export interface ProductListResponse {
  total: number;
  total_amount: number;
  items: Product[];
}

export interface ProductDetailResponse {
  product: Product;
  recent_orders: any[];
  monthly_trend: {
    month: string;
    amount: number;
    count: number;
  }[];
}

// Get product list
export const getProducts = (params?: {
  sort_by?: string;
  sort_order?: string;
  search?: string;
}): Promise<ProductListResponse> => {
  return api.get('/products', { params });
};

// Get product by ID
export const getProduct = (id: number): Promise<ProductDetailResponse> => {
  return api.get(`/products/${id}`);
};

// Get product by name
export const getProductByName = (name: string): Promise<Product> => {
  return api.get(`/products/name/${encodeURIComponent(name)}`);
};
