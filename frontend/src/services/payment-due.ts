/**
 * Payment Due Service - 先采后付账期管理
 */
import api from './api';

export interface PaymentDueGroup {
  due_date: string;
  days_remaining: number;
  status: 'overdue' | 'warning' | 'normal';
  status_text: string;
  total_count: number;
  total_amount: number;
  unpaid_count: number;
  unpaid_amount: number;
  paid_count: number;
  paid_amount: number;
  receive_month_start: string | null;
  receive_month_end: string | null;
  is_current_month: boolean;
  is_incomplete: boolean;
  order_ids: number[];
}

export interface PaymentDueOrderDetail {
  id: number;
  order_no: string;
  product_name: string;
  supplier: string;
  purchase_amount: number;
  order_date: string;
  receive_date?: string | null;
  payment_status?: string;
  spec?: string | null;
}

export interface PaymentDueGroupDetailResponse {
  total: number;
  page: number;
  page_size: number;
  items: PaymentDueOrderDetail[];
  due_date: string;
}

export interface MarkAsPaidResponse {
  due_date: string;
  updated_count: number;
  updated_amount: number;
}

/**
 * 获取按还款日分组的统计
 */
export const getPaymentDueGroups = (includePaid: boolean = false): Promise<PaymentDueGroup[]> => {
  return api.get('/payment-due/groups', {
    params: { include_paid: includePaid }
  });
};

/**
 * 获取指定还款日的订单详情
 */
export const getPaymentDueGroupDetail = (
  dueDate: string,
  page: number = 1,
  pageSize: number = 50
): Promise<PaymentDueGroupDetailResponse> => {
  return api.get(`/payment-due/groups/${dueDate}`, {
    params: { page, page_size: pageSize }
  });
};

/**
 * 将指定还款日的所有未付款订单标记为已付款
 */
export const markPaymentDueGroupAsPaid = (dueDate: string): Promise<MarkAsPaidResponse> => {
  return api.post(`/payment-due/groups/${dueDate}/mark-paid`);
};
