/**
 * 账期跟踪页面
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, Table, Tag, Radio, Row, Col, Statistic } from 'antd'
import { WarningOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { statisticsApi } from '@/services/statistics'
import type { PaymentDue } from '@/types'

export default function PaymentDuePage() {
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // 获取账期数据
  const { data, isLoading } = useQuery<PaymentDue[]>({
    queryKey: ['payment-due'],
    queryFn: statisticsApi.getPaymentDue,
  })

  // 过滤数据
  const filteredData = data?.filter((item) => {
    if (statusFilter === 'all') return true
    return item.status === statusFilter
  })

  // 统计数据
  const stats = {
    total: data?.length || 0,
    overdue: data?.filter((item) => item.status === 'overdue').length || 0,
    warning: data?.filter((item) => item.status === 'warning').length || 0,
    normal: data?.filter((item) => item.status === 'normal').length || 0,
  }

  const columns = [
    {
      title: '订单编号',
      dataIndex: 'order_no',
      key: 'order_no',
      width: 200,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
    },
    {
      title: '采购金额',
      dataIndex: 'purchase_amount',
      key: 'purchase_amount',
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
    },
    {
      title: '到期日期',
      dataIndex: 'due_date',
      key: 'due_date',
    },
    {
      title: '剩余天数',
      dataIndex: 'days_remaining',
      key: 'days_remaining',
      render: (days: number) => {
        if (days < 0) return <span style={{ color: '#cf1322' }}>{days}天（已逾期）</span>
        if (days <= 5) return <span style={{ color: '#faad14' }}>{days}天</span>
        return <span>{days}天</span>
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const config = {
          overdue: { color: 'error', text: '已逾期', icon: <WarningOutlined /> },
          warning: { color: 'warning', text: '即将到期', icon: <ClockCircleOutlined /> },
          normal: { color: 'success', text: '正常', icon: <CheckCircleOutlined /> },
        }
        const cfg = config[status as keyof typeof config]
        return (
          <Tag color={cfg.color} icon={cfg.icon}>
            {cfg.text}
          </Tag>
        )
      },
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总计"
              value={stats.total}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已逾期"
              value={stats.overdue}
              valueStyle={{ color: '#cf1322' }}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="即将到期"
              value={stats.warning}
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="正常"
              value={stats.normal}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 表格 */}
      <Card>
        <Radio.Group
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ marginBottom: 16 }}
        >
          <Radio.Button value="all">全部</Radio.Button>
          <Radio.Button value="overdue">已逾期</Radio.Button>
          <Radio.Button value="warning">即将到期</Radio.Button>
          <Radio.Button value="normal">正常</Radio.Button>
        </Radio.Group>

        <Table
          dataSource={filteredData || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          rowClassName={(record) => {
            if (record.status === 'overdue') return 'row-overdue'
            if (record.status === 'warning') return 'row-warning'
            return ''
          }}
          pagination={{
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      <style>{`
        .row-overdue {
          background-color: #fff1f0;
        }
        .row-warning {
          background-color: #fffbe6;
        }
      `}</style>
    </div>
  )
}
