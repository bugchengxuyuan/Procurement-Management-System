/**
 * Dashboard统计页面
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, DatePicker, Select, Spin, Table, message } from 'antd';
import { ShoppingCartOutlined, ProductOutlined, DollarOutlined } from '@ant-design/icons';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import { orderAPI } from '../services/api';
import type { Statistics, ProductStats } from '../types';

const { RangePicker } = DatePicker;
const { Option } = Select;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [productStats, setProductStats] = useState<ProductStats[]>([]);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [shopFilter, setShopFilter] = useState<string | undefined>();

  useEffect(() => {
    loadData();
  }, [dateRange, shopFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const filters = {
        start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
        end_date: dateRange?.[1]?.format('YYYY-MM-DD'),
        shop_name: shopFilter,
      };

      const [stats, prodStats] = await Promise.all([
        orderAPI.getStatistics(filters),
        orderAPI.getProductStatistics(filters, 10),
      ]);

      setStatistics(stats);
      setProductStats(prodStats);
    } catch (error) {
      message.error('加载数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (dates: any) => {
    setDateRange(dates);
  };

  const productColumns = [
    {
      title: '排名',
      key: 'rank',
      width: 60,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
    },
    {
      title: '采购总额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value: number) => `¥${value.toFixed(2)}`,
      sorter: (a: ProductStats, b: ProductStats) => a.total_amount - b.total_amount,
    },
    {
      title: '订单数量',
      dataIndex: 'order_count',
      key: 'order_count',
    },
    {
      title: '平均金额',
      dataIndex: 'avg_amount',
      key: 'avg_amount',
      render: (value: number) => `¥${value.toFixed(2)}`,
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (value: number) => `${value.toFixed(2)}%`,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Spin spinning={loading}>
        {/* 筛选器 */}
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col>
              <RangePicker
                value={dateRange}
                onChange={handleDateChange}
                format="YYYY-MM-DD"
                placeholder={['开始日期', '结束日期']}
              />
            </Col>
            <Col>
              <Select
                style={{ width: 200 }}
                placeholder="选择店铺"
                allowClear
                value={shopFilter}
                onChange={setShopFilter}
              >
                <Option value="CAISHENDAO">CAISHENDAO</Option>
                <Option value="Kitchen maestro">Kitchen maestro</Option>
              </Select>
            </Col>
          </Row>
        </Card>

        {/* 统计卡片 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="采购总额"
                value={statistics?.total_amount || 0}
                precision={2}
                prefix={<DollarOutlined />}
                suffix="元"
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="订单总数"
                value={statistics?.total_orders || 0}
                prefix={<ShoppingCartOutlined />}
                suffix="单"
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="产品种类"
                value={statistics?.total_products || 0}
                prefix={<ProductOutlined />}
                suffix="种"
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 图表 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={12}>
            <Card title="店铺采购统计">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statistics?.shop_stats || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="shop_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total_amount" fill="#8884d8" name="采购金额" />
                  <Bar dataKey="order_count" fill="#82ca9d" name="订单数量" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="支付状态分布">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statistics?.payment_stats || []}
                    dataKey="order_count"
                    nameKey="payment_status"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.payment_status}: ${entry.order_count}单`}
                  >
                    {(statistics?.payment_stats || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        {/* 产品排行榜 */}
        <Card title="产品采购排行 TOP10">
          <Table
            columns={productColumns}
            dataSource={productStats}
            rowKey="product_name"
            pagination={false}
            size="small"
          />
        </Card>
      </Spin>
    </div>
  );
};

export default Dashboard;
