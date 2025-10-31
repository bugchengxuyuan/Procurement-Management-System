/**
 * 产品分析页面
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, DatePicker, Select, Space, Spin, message, Row, Col, Statistic } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import { orderAPI } from '../services/api';
import type { ProductStats } from '../types';

const { RangePicker } = DatePicker;
const { Option } = Select;

const ProductAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [productStats, setProductStats] = useState<ProductStats[]>([]);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [shopFilter, setShopFilter] = useState<string | undefined>();
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    loadData();
  }, [dateRange, shopFilter, limit]);

  const loadData = async () => {
    setLoading(true);
    try {
      const filters = {
        start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
        end_date: dateRange?.[1]?.format('YYYY-MM-DD'),
        shop_name: shopFilter,
      };

      const data = await orderAPI.getProductStatistics(filters, limit);
      setProductStats(data);
    } catch (error) {
      message.error('加载数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns: ColumnsType<ProductStats> = [
    {
      title: '排名',
      key: 'rank',
      width: 80,
      render: (_, __, index) => index + 1,
      fixed: 'left',
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 250,
      fixed: 'left',
    },
    {
      title: '采购总额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 150,
      render: (value: number) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.total_amount - b.total_amount,
    },
    {
      title: '订单数量',
      dataIndex: 'order_count',
      key: 'order_count',
      width: 120,
      sorter: (a, b) => a.order_count - b.order_count,
    },
    {
      title: '平均金额',
      dataIndex: 'avg_amount',
      key: 'avg_amount',
      width: 150,
      render: (value: number) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.avg_amount - b.avg_amount,
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      width: 120,
      render: (value: number) => `${value.toFixed(2)}%`,
      sorter: (a, b) => a.percentage - b.percentage,
    },
  ];

  // 计算总计
  const totalAmount = productStats.reduce((sum, item) => sum + item.total_amount, 0);
  const totalOrders = productStats.reduce((sum, item) => sum + item.order_count, 0);

  return (
    <div style={{ padding: '24px' }}>
      <Spin spinning={loading}>
        {/* 筛选器 */}
        <Card style={{ marginBottom: 24 }}>
          <Space wrap>
            <RangePicker
              value={dateRange}
              onChange={(dates) => setDateRange(dates)}
              format="YYYY-MM-DD"
              placeholder={['开始日期', '结束日期']}
            />
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
            <Select
              style={{ width: 150 }}
              value={limit}
              onChange={setLimit}
            >
              <Option value={20}>TOP 20</Option>
              <Option value={50}>TOP 50</Option>
              <Option value={100}>TOP 100</Option>
              <Option value={200}>TOP 200</Option>
            </Select>
          </Space>
        </Card>

        {/* 统计卡片 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="产品总数"
                value={productStats.length}
                suffix="种"
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="采购总额"
                value={totalAmount}
                precision={2}
                prefix="¥"
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="订单总数"
                value={totalOrders}
                suffix="单"
              />
            </Card>
          </Col>
        </Row>

        {/* 图表 */}
        <Card title="产品采购金额排行" style={{ marginBottom: 24 }}>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={productStats.slice(0, 15)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="product_name" angle={-45} textAnchor="end" height={120} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_amount" fill="#8884d8" name="采购金额" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* 详细列表 */}
        <Card title="产品详细统计">
          <Table
            columns={columns}
            dataSource={productStats}
            rowKey="product_name"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 个产品`,
            }}
            scroll={{ x: 1000 }}
          />
        </Card>
      </Spin>
    </div>
  );
};

export default ProductAnalysis;
