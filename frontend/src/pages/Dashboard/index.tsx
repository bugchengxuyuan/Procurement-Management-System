import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Progress, Spin } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { Column } from '@ant-design/charts';
import { getDashboardStats, DashboardStats } from '@/services/statistics';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 月度趋势配置
  const monthlyConfig = {
    data: stats.monthly_trend.map(item => ({
      month: item.month,
      value: item.amount,
      type: '采购金额',
    })),
    xField: 'month',
    yField: 'value',
    seriesField: 'type',
    label: {
      position: 'top' as const,
      style: {
        fill: '#000000',
        opacity: 0.6,
      },
      formatter: (datum: any) => `¥${(datum.value / 1000).toFixed(1)}k`,
    },
    xAxis: {
      label: {
        autoHide: false,
        autoRotate: false,
      },
    },
    yAxis: {
      label: {
        formatter: (v: string) => `¥${(parseFloat(v) / 1000).toFixed(0)}k`,
      },
    },
  };

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>数据概览</h2>

      {/* 核心指标卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="采购总额"
              value={stats.total_amount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="订单总数"
              value={stats.total_orders}
              suffix="单"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="产品种类"
              value={stats.total_products}
              suffix="种"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本月采购"
              value={stats.this_month_amount}
              precision={2}
              prefix="¥"
              suffix={
                stats.this_month_growth >= 0 ? (
                  <span style={{ fontSize: 14 }}>
                    <ArrowUpOutlined /> {stats.this_month_growth.toFixed(2)}%
                  </span>
                ) : (
                  <span style={{ fontSize: 14 }}>
                    <ArrowDownOutlined /> {Math.abs(stats.this_month_growth).toFixed(2)}%
                  </span>
                )
              }
              valueStyle={{ color: stats.this_month_growth >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* 支付方式分布 */}
        <Col span={12}>
          <Card title="支付方式分布" style={{ height: 400 }}>
            {Object.entries(stats.payment_distribution).map(([name, data]) => {
              const percentage = (data.amount / stats.total_amount) * 100;
              return (
                <div key={name} style={{ marginBottom: 20 }}>
                  <div style={{ marginBottom: 8 }}>
                    <span style={{ fontWeight: 'bold' }}>{name}</span>
                    <span style={{ float: 'right' }}>
                      {data.count}单 | ¥{data.amount.toFixed(2)}
                    </span>
                  </div>
                  <Progress
                    percent={percentage}
                    format={(percent) => `${percent?.toFixed(1)}%`}
                    strokeColor={name === '已付款' ? '#52c41a' : '#1890ff'}
                  />
                </div>
              );
            })}
          </Card>
        </Col>

        {/* TOP 5 产品 */}
        <Col span={12}>
          <Card title="TOP 5 产品" style={{ height: 400 }}>
            <Table
              dataSource={stats.top_products}
              columns={[
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
                  title: '采购金额',
                  dataIndex: 'total_amount',
                  key: 'total_amount',
                  render: (value: number) => `¥${value.toFixed(2)}`,
                },
                {
                  title: '占比',
                  dataIndex: 'percentage',
                  key: 'percentage',
                  render: (value: number) => (
                    <Progress
                      percent={value}
                      size="small"
                      format={(percent) => `${percent?.toFixed(1)}%`}
                    />
                  ),
                },
              ]}
              pagination={false}
              size="small"
              rowKey="product_name"
            />
          </Card>
        </Col>
      </Row>

      {/* 月度采购趋势 */}
      <Card title="月度采购趋势（最近6个月）" style={{ marginBottom: 24 }}>
        <Column {...monthlyConfig} height={300} />
      </Card>
    </div>
  );
};

export default Dashboard;
