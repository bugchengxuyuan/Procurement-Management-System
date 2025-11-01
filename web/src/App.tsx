/**
 * 主应用
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { queryClient } from '@/utils/queryClient'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import OrderList from '@/pages/OrderList'
import ProductList from '@/pages/ProductList'
import PaymentDue from '@/pages/PaymentDue'

export default function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="orders" element={<OrderList />} />
              <Route path="products" element={<ProductList />} />
              <Route path="payment-due" element={<PaymentDue />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ConfigProvider>
  )
}
