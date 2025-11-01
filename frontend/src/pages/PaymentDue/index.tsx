import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Tag,
  Statistic,
  Row,
  Col,
  Tabs,
  Button,
  message,
} from 'antd';
import {
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { getPaymentDueOrders, PaymentDueOrder } from '@/services/statistics';
import { updateOrder } from '@/services/order';

const PaymentDue: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<PaymentDueOrder[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<PaymentDueOrder[]>([]);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    loadOrders();
  }, []);

  useEffect(() => {
    filterOrders();
  }, [activeTab, orders]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const data = await getPaymentDueOrders(7);
      setOrders(data);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const filterOrders = () => {
    let filtered = orders;
    if (activeTab !== 'all') {
      filtered = orders.filter(order => order.status === activeTab);
    }
    setFilteredOrders(filtered);
  };

  const handleMarkAsPaid = async (orderId: number) => {
    try {
      await updateOrder(orderId, {
        order_status: '已付款',
        payment_method: '已付款',
      });
      message.success('已标记为付款');
      loadOrders();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'overdue':
        return <Tag color="red" icon={<ExclamationCircleOutlined />}>已逾期</Tag>;
      case 'warning':
        return <Tag color="orange" icon={<WarningOutlined />}>即将到期</Tag>;
      case 'normal':
        return <Tag color="green" icon={<ClockCircleOutlined />}>正常</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  const getDaysRemainingText = (days: number) => {
    if (days < 0) {
      return `逾期${Math.abs(days)}天`;
    } else if (days === 0) {
      return '今天到期';
    } else {
      return `剩余${days}天`;
    }
  };

  const columns: ColumnsType<PaymentDueOrder> = [
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '订单编号',
      dataIndex: 'order_no',
      key: 'order_no',
      width: 180,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 150,
    },
    {
      title: '采购金额',
      dataIndex: 'purchase_amount',
      key: 'purchase_amount',
      width: 120,
      render: (amount: number) => `¥${amount.toFixed(2)}`,
    },
    {
      title: '到期日期',
      dataIndex: 'due_date',
      key: 'due_date',
      width: 120,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '剩余天数',
      dataIndex: 'days_remaining',
      key: 'days_remaining',
      width: 120,
      render: (days: number) => (
        <span style={{ color: days < 0 ? '#ff4d4f' : days <= 7 ? '#faad14' : '#52c41a' }}>
          {getDaysRemainingText(days)}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_: any, record: PaymentDueOrder) => (
        <Button
          type="link"
          size="small"
          onClick={() => handleMarkAsPaid(record.order_id)}
        >
          标记付款
        </Button>
      ),
    },
  ];

  // 统计数据
  const overdueOrders = orders.filter(o => o.status === 'overdue');
  const warningOrders = orders.filter(o => o.status === 'warning');
  const normalOrders = orders.filter(o => o.status === 'normal');

  const overdueAmount = overdueOrders.reduce((sum, o) => sum + o.purchase_amount, 0);
  const warningAmount = warningOrders.reduce((sum, o) => sum + o.purchase_amount, 0);
  const totalAmount = orders.reduce((sum, o) => sum + o.purchase_amount, 0);

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>先采后付订单管理</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="待付款订单"
              value={orders.length}
              suffix="单"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待付款金额"
              value={totalAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已逾期订单"
              value={overdueOrders.length}
              suffix="单"
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<ExclamationCircleOutlined />}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              金额: ¥{overdueAmount.toFixed(2)}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="7天内到期"
              value={warningOrders.length}
              suffix="单"
              valueStyle={{ color: '#faad14' }}
              prefix={<WarningOutlined />}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              金额: ¥{warningAmount.toFixed(2)}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 订单列表 */}
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'all',
              label: `全部 (${orders.length})`,
            },
            {
              key: 'overdue',
              label: `已逾期 (${overdueOrders.length})`,
            },
            {
              key: 'warning',
              label: `即将到期 (${warningOrders.length})`,
            },
            {
              key: 'normal',
              label: `正常 (${normalOrders.length})`,
            },
          ]}
        />
        <Table
          columns={columns}
          dataSource={filteredOrders}
          rowKey="order_id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 1200 }}
          rowClassName={(record) => {
            if (record.status === 'overdue') return 'overdue-row';
            if (record.status === 'warning') return 'warning-row';
            return '';
          }}
        />
      </Card>

      <style>{`
        .overdue-row {
          background-color: #fff1f0;
        }
        .warning-row {
          background-color: #fffbe6;
        }
      `}</style>
    </div>
  );
};

export default PaymentDue;
