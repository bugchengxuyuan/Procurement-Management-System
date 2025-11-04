import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Tag,
  Statistic,
  Row,
  Col,
  Switch,
  Button,
  message,
  Modal,
  Alert,
  Space,
} from 'antd';
import {
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import {
  getPaymentDueGroups,
  getPaymentDueGroupDetail,
  markPaymentDueGroupAsPaid,
  PaymentDueGroup,
  PaymentDueOrderDetail,
} from '@/services/payment-due';

const PaymentDue: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [groups, setGroups] = useState<PaymentDueGroup[]>([]);
  const [includePaid, setIncludePaid] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<PaymentDueGroup | null>(null);
  const [orderDetails, setOrderDetails] = useState<PaymentDueOrderDetail[]>([]);
  const [detailTotal, setDetailTotal] = useState(0);

  useEffect(() => {
    loadGroups();
  }, [includePaid]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const data = await getPaymentDueGroups(includePaid);
      setGroups(data);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (group: PaymentDueGroup) => {
    setSelectedGroup(group);
    setDetailModalVisible(true);
    try {
      setDetailLoading(true);
      const data = await getPaymentDueGroupDetail(group.due_date, 1, 100);
      setOrderDetails(data.items);
      setDetailTotal(data.total);
    } catch (error) {
      message.error('加载订单详情失败');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleMarkGroupAsPaid = async (group: PaymentDueGroup) => {
    if (group.unpaid_count === 0) {
      message.info('该账期没有未付款订单');
      return;
    }

    Modal.confirm({
      title: '确认付款',
      content: `确定将 ${dayjs(group.due_date).format('YYYY年MM月DD日')} 到期的 ${group.unpaid_count} 单订单（总额 ¥${group.unpaid_amount.toFixed(2)}）标记为已付款吗？`,
      onOk: async () => {
        try {
          const result = await markPaymentDueGroupAsPaid(group.due_date);
          message.success(`成功标记 ${result.updated_count} 单订单为已付款`);
          loadGroups();
          if (detailModalVisible && selectedGroup?.due_date === group.due_date) {
            handleViewDetail(group);
          }
        } catch (error) {
          message.error('操作失败');
        }
      },
    });
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

  const groupColumns: ColumnsType<PaymentDueGroup> = [
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '还款日期',
      dataIndex: 'due_date',
      key: 'due_date',
      width: 130,
      render: (date: string) => (
        <span style={{ fontWeight: 'bold' }}>
          {dayjs(date).format('YYYY年MM月DD日')}
        </span>
      ),
    },
    {
      title: '剩余天数',
      dataIndex: 'days_remaining',
      key: 'days_remaining',
      width: 120,
      render: (days: number, record: PaymentDueGroup) => (
        <span style={{ color: days < 0 ? '#ff4d4f' : days <= 7 ? '#faad14' : '#52c41a' }}>
          {record.status_text}
        </span>
      ),
    },
    {
      title: '确认收货时段',
      key: 'receive_period',
      width: 200,
      render: (_: any, record: PaymentDueGroup) => {
        if (!record.receive_month_start || !record.receive_month_end) return '-';
        const start = dayjs(record.receive_month_start).format('YYYY-MM-DD');
        const end = dayjs(record.receive_month_end).format('YYYY-MM-DD');
        return (
          <div>
            <div>{start} 至 {end}</div>
            {record.is_incomplete && (
              <Tag color="blue" icon={<InfoCircleOutlined />} style={{ marginTop: 4 }}>
                账单未完整
              </Tag>
            )}
          </div>
        );
      },
    },
    {
      title: '订单数量',
      key: 'order_count',
      width: 140,
      render: (_: any, record: PaymentDueGroup) => (
        <div>
          <div>总计: {record.total_count}单</div>
          <div style={{ fontSize: 12, color: '#999' }}>
            未付: {record.unpaid_count} / 已付: {record.paid_count}
          </div>
        </div>
      ),
    },
    {
      title: '金额统计',
      key: 'amount',
      width: 160,
      render: (_: any, record: PaymentDueGroup) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>
            总额: ¥{record.total_amount.toFixed(2)}
          </div>
          <div style={{ fontSize: 12, color: '#fa8c16' }}>
            未付: ¥{record.unpaid_amount.toFixed(2)}
          </div>
          <div style={{ fontSize: 12, color: '#52c41a' }}>
            已付: ¥{record.paid_amount.toFixed(2)}
          </div>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right',
      render: (_: any, record: PaymentDueGroup) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            查看详情 ({record.total_count})
          </Button>
          <Button
            type="link"
            size="small"
            disabled={record.unpaid_count === 0}
            onClick={() => handleMarkGroupAsPaid(record)}
          >
            标记付款
          </Button>
        </Space>
      ),
    },
  ];

  const detailColumns: ColumnsType<PaymentDueOrderDetail> = [
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
      title: '规格',
      dataIndex: 'spec',
      key: 'spec',
      width: 120,
      render: (spec: string | null) => spec || '-',
    },
    {
      title: '供应商',
      dataIndex: 'supplier',
      key: 'supplier',
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
      title: '确认收货日期',
      dataIndex: 'receive_date',
      key: 'receive_date',
      width: 130,
      render: (date: string | null) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '付款状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      width: 120,
      render: (status?: string) => {
        if (!status) return '-';
        if (status === '账期已结') {
          return <Tag color="green" icon={<CheckCircleOutlined />}>账期已结</Tag>;
        }
        if (status === '账期未到') {
          return <Tag color="orange" icon={<ClockCircleOutlined />}>账期未到</Tag>;
        }
        return status;
      },
    },
  ];

  // 统计数据
  const overdueGroups = groups.filter(g => g.status === 'overdue');
  const warningGroups = groups.filter(g => g.status === 'warning');
  const normalGroups = groups.filter(g => g.status === 'normal');

  const totalUnpaidAmount = groups.reduce((sum, g) => sum + g.unpaid_amount, 0);
  const totalUnpaidCount = groups.reduce((sum, g) => sum + g.unpaid_count, 0);
  const overdueAmount = overdueGroups.reduce((sum, g) => sum + g.unpaid_amount, 0);
  const warningAmount = warningGroups.reduce((sum, g) => sum + g.unpaid_amount, 0);

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>先采后付账期管理</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="待付款订单"
              value={totalUnpaidCount}
              suffix="单"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待付款金额"
              value={totalUnpaidAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已逾期账期"
              value={overdueGroups.length}
              suffix="期"
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
              value={warningGroups.length}
              suffix="期"
              valueStyle={{ color: '#faad14' }}
              prefix={<WarningOutlined />}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              金额: ¥{warningAmount.toFixed(2)}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 账期分组列表 */}
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>按还款日分组</h3>
          <Space>
            <span>显示已付款账期:</span>
            <Switch checked={includePaid} onChange={setIncludePaid} />
          </Space>
        </div>

        {normalGroups.some(g => g.is_incomplete) && (
          <Alert
            message="账单提示"
            description="当月确认收货的订单账单可能不完整，因为月份尚未结束，后续可能会有更多订单加入。"
            type="info"
            icon={<InfoCircleOutlined />}
            showIcon
            closable
            style={{ marginBottom: 16 }}
          />
        )}

        <Table
          columns={groupColumns}
          dataSource={groups}
          rowKey="due_date"
          loading={loading}
          pagination={{
            pageSize: 20,
            showTotal: (total) => `共 ${total} 个账期`,
          }}
          scroll={{ x: 1400 }}
          rowClassName={(record) => {
            if (record.status === 'overdue') return 'overdue-row';
            if (record.status === 'warning') return 'warning-row';
            return '';
          }}
        />
      </Card>

      {/* 订单详情Modal */}
      <Modal
        title={
          selectedGroup ? (
            <div>
              <div>{dayjs(selectedGroup.due_date).format('YYYY年MM月DD日')} 还款账期详情</div>
              <div style={{ fontSize: 14, fontWeight: 'normal', color: '#999', marginTop: 4 }}>
                共 {selectedGroup.total_count} 单订单，总额 ¥{selectedGroup.total_amount.toFixed(2)}
              </div>
            </div>
          ) : '订单详情'
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={1200}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          selectedGroup && selectedGroup.unpaid_count > 0 && (
            <Button
              key="markPaid"
              type="primary"
              onClick={() => {
                if (selectedGroup) {
                  handleMarkGroupAsPaid(selectedGroup);
                }
              }}
            >
              批量标记付款 ({selectedGroup.unpaid_count}单)
            </Button>
          ),
        ]}
      >
        {selectedGroup && selectedGroup.is_incomplete && (
          <Alert
            message="此账单尚未完整"
            description={`确认收货时段: ${dayjs(selectedGroup.receive_month_start).format('YYYY-MM-DD')} 至 ${dayjs(selectedGroup.receive_month_end).format('YYYY-MM-DD')}，本月尚未结束，后续可能有更多订单加入。`}
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        <Table
          columns={detailColumns}
          dataSource={orderDetails}
          rowKey="id"
          loading={detailLoading}
          pagination={{
            pageSize: 20,
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 1000 }}
        />
      </Modal>

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
