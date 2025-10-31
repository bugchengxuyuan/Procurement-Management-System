/**
 * 主应用组件
 */
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Layout, Menu, Typography } from 'antd';
import {
  DashboardOutlined,
  ShoppingCartOutlined,
  BarChartOutlined,
  ImportOutlined,
  CreditCardOutlined,
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import OrderList from './pages/OrderList';
import ProductAnalysis from './pages/ProductAnalysis';
import ImportExport from './pages/ImportExport';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">数据概览</Link>,
    },
    {
      key: '/orders',
      icon: <ShoppingCartOutlined />,
      label: <Link to="/orders">订单管理</Link>,
    },
    {
      key: '/products',
      icon: <BarChartOutlined />,
      label: <Link to="/products">产品分析</Link>,
    },
    {
      key: '/import-export',
      icon: <ImportOutlined />,
      label: <Link to="/import-export">数据导入导出</Link>,
    },
  ];

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
          <div
            style={{
              height: 64,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: collapsed ? 16 : 20,
              fontWeight: 'bold',
            }}
          >
            {collapsed ? '采购' : '采购管理系统'}
          </div>
          <Menu theme="dark" mode="inline" items={menuItems} defaultSelectedKeys={['/']} />
        </Sider>

        <Layout>
          <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 1px 4px rgba(0,0,0,.08)' }}>
            <Title level={3} style={{ margin: '14px 0' }}>
              采购管理系统
            </Title>
          </Header>

          <Content style={{ margin: '0', background: '#f0f2f5' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/orders" element={<OrderList />} />
              <Route path="/products" element={<ProductAnalysis />} />
              <Route path="/import-export" element={<ImportExport />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;
