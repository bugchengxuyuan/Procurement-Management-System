/**
 * Import/Export API Service
 */
import axios from 'axios';

export interface ImportResult {
  total_rows: number;
  success_count: number;
  error_count: number;
  errors: Array<{
    row?: number;
    order_no?: string;
    error: string;
  }>;
}

// Import Excel file
export const importExcel = (file: File): Promise<ImportResult> => {
  const formData = new FormData();
  formData.append('file', file);

  return axios.post('/api/import/excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(res => res.data);
};

// Export Excel file
export const exportExcel = (params?: {
  product_name?: string;
  order_status?: string;
  payment_method?: string;
  start_date?: string;
  end_date?: string;
}): Promise<Blob> => {
  return axios.get('/api/export/excel', {
    params,
    responseType: 'blob',
  }).then(res => res.data);
};

// Download exported file
export const downloadExcelFile = (blob: Blob, filename: string = 'orders_export.xlsx') => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
