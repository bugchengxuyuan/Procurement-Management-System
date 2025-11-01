/**
 * 数据类型定义
 */

export interface Order {
  id: number
  order_no: string
  product_name: string
  purchase_amount: number
  order_date: string
  order_status: string
  payment_method: string
  record_time: string
  created_at: string
  updated_at: string
}

export interface OrderCreate {
  order_no: string
  product_name: string
  purchase_amount: number
  order_date: string
  order_status: string
  payment_method: string
  record_time: string
}

export interface OrderUpdate {
  product_name?: string
  purchase_amount?: number
  order_date?: string
  order_status?: string
  payment_method?: string
  record_time?: string
}

export interface Product {
  id: number
  product_name: string
  total_purchase_amount: number
  total_order_count: number
  avg_unit_price: number
  last_purchase_date: string | null
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  total_amount: number
  total_orders: number
  total_products: number
  this_month_amount: number
  this_month_growth: number
  payment_distribution: {
    [key: string]: {
      count: number
      amount: number
    }
  }
  monthly_trend: Array<{
    month: string
    amount: number
    count: number
  }>
  top_products: Array<{
    product_name: string
    total_amount: number
    order_count: number
    percentage: number
  }>
  date_range: {
    start_date: string | null
    end_date: string | null
  }
}

export interface PaymentDue {
  id: number
  order_no: string
  product_name: string
  purchase_amount: number
  order_date: string
  due_date: string
  days_remaining: number
  status: 'overdue' | 'warning' | 'normal'
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  size: number
  items: T[]
}
