/**
 * Statistics API Service
 */
import api from './api';

export interface PaymentDistribution {
  count: number;
  amount: number;
}

export interface MonthlyTrend {
  month: string;
  amount: number;
  count: number;
}

export interface TopProduct {
  product_name: string;
  total_amount: number;
  order_count: number;
  percentage: number;
}

export interface DashboardStats {
  total_amount: number;
  total_orders: number;
  total_products: number;
  this_month_amount: number;
  this_month_growth: number;
  payment_distribution: Record<string, PaymentDistribution>;
  monthly_trend: MonthlyTrend[];
  top_products: TopProduct[];
}

export interface PaymentDueOrder {
  order_id: number;
  order_no: string;
  product_name: string;
  purchase_amount: number;
  order_date: string;
  due_date: string;
  days_remaining: number;
  status: 'overdue' | 'warning' | 'normal';
}

export interface DateRangeStats {
  start_date: string;
  end_date: string;
  total_amount: number;
  total_orders: number;
  avg_order_amount: number;
}

// Get dashboard statistics
export const getDashboardStats = (): Promise<DashboardStats> => {
  return api.get('/statistics/dashboard');
};

// Get monthly trend
export const getMonthlyTrend = (months: number = 6): Promise<MonthlyTrend[]> => {
  return api.get('/statistics/monthly-trend', { params: { months } });
};

// Get payment due orders
export const getPaymentDueOrders = (days_threshold: number = 7): Promise<PaymentDueOrder[]> => {
  return api.get('/statistics/payment-due', { params: { days_threshold } });
};

// Get date range statistics
export const getDateRangeStats = (start_date: string, end_date: string): Promise<DateRangeStats> => {
  return api.get('/statistics/date-range', { params: { start_date, end_date } });
};
