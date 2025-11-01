/**
 * 数据总览页面
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, Row, Col, Statistic, Progress, Table, Spin, DatePicker, Space, Button, Alert } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { Dayjs } from 'dayjs'
import { statisticsApi } from '@/services/statistics'
import type { DashboardStats } from '@/types'

const { RangePicker } = DatePicker

export default function Dashboard() {
  const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null)

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard', dateRange?.[0]?.format('YYYY-MM-DD'), dateRange?.[1]?.format('YYYY-MM-DD')],
    queryFn: () => statisticsApi.getDashboard(
      dateRange?.[0]?.format('YYYY-MM-DD'),
      dateRange?.[1]?.format('YYYY-MM-DD')
    ),
  })

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '100px' }}><Spin size="large" /></div>
  }

  if (!stats) return null

  const handleDateChange = (dates: any) => {
    setDateRange(dates)
  }

  const handleReset = () => {
    setDateRange(null)
  }

  // 月度趋势图表配置
  const trendChartOption = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: stats.monthly_trend.map((item) => item.month).reverse(),
    },
    yAxis: {
      type: 'value',
      name: '金额(¥)',
    },
    series: [
      {
        name: '采购金额',
        type: 'bar',
        data: stats.monthly_trend.map((item) => item.amount).reverse(),
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
  }

  // TOP产品表格列
  const columns = [
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
    },
    {
      title: '采购金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '订单数',
      dataIndex: 'order_count',
      key: 'order_count',
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (val: number) => (
        <Progress percent={val} size="small" />
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      {/* 时间筛选器 */}
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <span>月度趋势时间范围：</span>
            <RangePicker
              value={dateRange}
              onChange={handleDateChange}
              format="YYYY-MM-DD"
              placeholder={['开始日期', '结束日期']}
            />
            {dateRange && (
              <Button onClick={handleReset}>重置</Button>
            )}
          </Space>
          <Alert
            message="说明：采购总额、订单总数、产品总数等始终显示所有数据。时间筛选仅影响月度采购趋势图表。"
            type="info"
            showIcon
            style={{ marginTop: 8 }}
          />
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        {/* 统计卡片 */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="采购总额"
              value={stats.total_amount}
              precision={2}
              prefix="¥"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="订单总数"
              value={stats.total_orders}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="产品总数"
              value={stats.total_products}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="本月采购额"
              value={stats.this_month_amount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: stats.this_month_growth >= 0 ? '#3f8600' : '#cf1322' }}
              suffix={
                stats.this_month_growth >= 0 ? (
                  <span>
                    <ArrowUpOutlined /> {Math.abs(stats.this_month_growth)}%
                  </span>
                ) : (
                  <span>
                    <ArrowDownOutlined /> {Math.abs(stats.this_month_growth)}%
                  </span>
                )
              }
            />
          </Card>
        </Col>

        {/* 支付方式分布 */}
        <Col xs={24} lg={12}>
          <Card title="支付方式分布" style={{ height: '100%' }}>
            {Object.entries(stats.payment_distribution).map(([method, data]) => (
              <div key={method} style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span>{method}</span>
                  <span>
                    {data.count}笔 / ¥{data.amount.toFixed(2)}
                  </span>
                </div>
                <Progress
                  percent={
                    (data.amount / stats.total_amount) * 100
                  }
                  showInfo={false}
                  strokeColor={method === '先采后付' ? '#faad14' : '#52c41a'}
                />
              </div>
            ))}
          </Card>
        </Col>

        {/* TOP5产品 */}
        <Col xs={24} lg={12}>
          <Card title="TOP 5 产品" style={{ height: '100%' }}>
            <Table
              dataSource={stats.top_products}
              columns={columns}
              pagination={false}
              rowKey="product_name"
              size="small"
            />
          </Card>
        </Col>

        {/* 月度趋势 */}
        <Col xs={24}>
          <Card title="月度采购趋势">
            <ReactECharts option={trendChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
