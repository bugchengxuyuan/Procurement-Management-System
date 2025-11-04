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
  paid_date?: string | null;
  bill_import_time?: string | null;
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

/**
 * 1688账单导入结果
 */
export interface BillImportResult {
  success_count: number;
  failed_count: number;
  not_found_count: number;
  already_paid_count: number;
  success_orders: string[];
  not_found_orders: string[];
  already_paid_orders: string[];
  errors: Array<{ order_no: string; error: string }>;
  paid_date: string;
  import_time: string;
  total_amount: number;
}

/**
 * 导入1688账单Excel并批量更新订单状态
 */
export const importPaymentBill = async (
  file: File,
  paidDate: string
): Promise<BillImportResult> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('paid_date', paidDate);

  return api.post('/payment-due/import-bill', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
