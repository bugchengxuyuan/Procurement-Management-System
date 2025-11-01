import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/Layout';
import Dashboard from './pages/Dashboard';
import OrderList from './pages/OrderList';
import ProductList from './pages/ProductList';
import PaymentDue from './pages/PaymentDue';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="orders" element={<OrderList />} />
          <Route path="products" element={<ProductList />} />
          <Route path="payment-due" element={<PaymentDue />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
