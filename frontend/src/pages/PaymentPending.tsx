/**
 * 先采后付订单管理页面
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  message,
  Tag,
  Statistic,
  Row,
  Col,
  Collapse,
  Modal,
  Select,
  Spin,
} from 'antd';
import {
  CreditCardOutlined,
  DollarOutlined,
  ShoppingCartOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import { orderAPI } from '../services/api';
import type { PurchaseOrder } from '../types';

const { Panel } = Collapse;
const { Option } = Select;

interface OrderGroup {
  order_no: string;
  shop_name: string;
  order_date?: string;
  payment_status?: string;
  products: PurchaseOrder[];
  total_amount: number;
  product_count: number;
}

const PaymentPending: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [groupedOrders, setGroupedOrders] = useState<OrderGroup[]>([]);
  const [selectedOrders, setSelectedOrders] = useState<string[]>([]);
  const [markPaymentModalVisible, setMarkPaymentModalVisible] = useState(false);
  const [currentOrderNo, setCurrentOrderNo] = useState<string | null>(null);

  useEffect(() => {
    loadPendingOrders();
  }, []);

  useEffect(() => {
    // 按订单号分组
    const grouped = groupOrdersByOrderNo(orders);
    setGroupedOrders(grouped);
  }, [orders]);

  const loadPendingOrders = async () => {
    setLoading(true);
    try {
      const data = await orderAPI.getPendingOrders();
      setOrders(data);
      message.success(`加载成功，共 ${data.length} 条待支付订单`);
    } catch (error) {
      message.error('加载待支付订单失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const groupOrdersByOrderNo = (orders: PurchaseOrder[]): OrderGroup[] => {
    const grouped = new Map<string, OrderGroup>();

    orders.forEach((order) => {
      const key = order.order_no;
      if (!grouped.has(key)) {
        grouped.set(key, {
          order_no: order.order_no,
          shop_name: order.shop_name,
          order_date: order.order_date,
          payment_status: order.payment_status,
          products: [],
          total_amount: 0,
          product_count: 0,
        });
      }

      const group = grouped.get(key)!;
      group.products.push(order);
      group.total_amount += order.purchase_amount;
      group.product_count += 1;
    });

    return Array.from(grouped.values()).sort((a, b) => {
      // 按日期降序排序
      if (a.order_date && b.order_date) {
        return new Date(b.order_date).getTime() - new Date(a.order_date).getTime();
      }
      return 0;
    });
  };

  const handleMarkAsPaid = (orderNo: string) => {
    setCurrentOrderNo(orderNo);
    setMarkPaymentModalVisible(true);
  };

  const confirmMarkAsPaid = async () => {
    if (!currentOrderNo) return;

    try {
      const group = groupedOrders.find((g) => g.order_no === currentOrderNo);
      if (!group) return;

      // 更新该订单下的所有产品的支付状态
      await Promise.all(
        group.products.map((product) =>
          orderAPI.updateOrder(product.id, { payment_status: '已付款' })
        )
      );

      message.success('订单已标记为已付款');
      setMarkPaymentModalVisible(false);
      setCurrentOrderNo(null);
      loadPendingOrders();
    } catch (error) {
      message.error('更新支付状态失败');
      console.error(error);
    }
  };

  const productColumns: ColumnsType<PurchaseOrder> = [
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 300,
    },
    {
      title: '采购金额',
      dataIndex: 'purchase_amount',
      key: 'purchase_amount',
      width: 120,
      render: (value: number) => (
        <span style={{ fontWeight: 'bold', color: '#ff4d4f' }}>¥{value.toFixed(2)}</span>
      ),
    },
    {
      title: '初始状态',
      dataIndex: 'initial_status',
      key: 'initial_status',
      width: 100,
      render: (status: string) => status || '-',
    },
  ];

  const getTotalStats = () => {
    const totalAmount = groupedOrders.reduce((sum, group) => sum + group.total_amount, 0);
    const totalOrders = groupedOrders.length;
    const totalProducts = orders.length;

    return { totalAmount, totalOrders, totalProducts };
  };

  const { totalAmount, totalOrders, totalProducts } = getTotalStats();

  return (
    <div style={{ padding: '24px' }}>
      <Spin spinning={loading}>
        {/* 统计卡片 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="待支付总额"
                value={totalAmount}
                precision={2}
                prefix={<DollarOutlined />}
                suffix="元"
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="待支付订单数"
                value={totalOrders}
                prefix={<ShoppingCartOutlined />}
                suffix="单"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="待支付产品数"
                value={totalProducts}
                prefix={<CreditCardOutlined />}
                suffix="件"
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
        </Row>

        {/* 订单列表 */}
        <Card
          title={
            <Space>
              <CreditCardOutlined />
              <span>先采后付订单列表</span>
            </Space>
          }
          extra={
            <Button icon={<ReloadOutlined />} onClick={loadPendingOrders}>
              刷新
            </Button>
          }
        >
          {groupedOrders.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
              <CheckCircleOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <div>暂无待支付订单</div>
            </div>
          ) : (
            <Collapse accordion>
              {groupedOrders.map((group, index) => (
                <Panel
                  header={
                    <Row align="middle" style={{ width: '100%' }}>
                      <Col span={6}>
                        <strong>订单号：</strong>
                        {group.order_no}
                      </Col>
                      <Col span={4}>
                        <strong>店铺：</strong>
                        {group.shop_name}
                      </Col>
                      <Col span={4}>
                        <strong>日期：</strong>
                        {group.order_date ? dayjs(group.order_date).format('YYYY-MM-DD') : '-'}
                      </Col>
                      <Col span={3}>
                        <Tag color="orange">{group.payment_status}</Tag>
                      </Col>
                      <Col span={3}>
                        <strong>产品数：</strong>
                        {group.product_count}
                      </Col>
                      <Col span={4} style={{ textAlign: 'right' }}>
                        <span style={{ fontSize: 16, fontWeight: 'bold', color: '#ff4d4f' }}>
                          ¥{group.total_amount.toFixed(2)}
                        </span>
                      </Col>
                    </Row>
                  }
                  key={group.order_no}
                  extra={
                    <Button
                      type="primary"
                      size="small"
                      icon={<CheckCircleOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMarkAsPaid(group.order_no);
                      }}
                    >
                      标记已付款
                    </Button>
                  }
                >
                  <Table
                    columns={productColumns}
                    dataSource={group.products}
                    rowKey="id"
                    pagination={false}
                    size="small"
                    summary={() => (
                      <Table.Summary fixed>
                        <Table.Summary.Row>
                          <Table.Summary.Cell index={0}>
                            <strong>订单合计</strong>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={1}>
                            <strong style={{ color: '#ff4d4f', fontSize: 16 }}>
                              ¥{group.total_amount.toFixed(2)}
                            </strong>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={2}></Table.Summary.Cell>
                        </Table.Summary.Row>
                      </Table.Summary>
                    )}
                  />
                </Panel>
              ))}
            </Collapse>
          )}
        </Card>

        {/* 标记付款确认对话框 */}
        <Modal
          title="确认标记为已付款"
          open={markPaymentModalVisible}
          onOk={confirmMarkAsPaid}
          onCancel={() => {
            setMarkPaymentModalVisible(false);
            setCurrentOrderNo(null);
          }}
          okText="确认"
          cancelText="取消"
        >
          <p>确定要将订单 {currentOrderNo} 标记为已付款吗？</p>
          <p style={{ color: '#999', fontSize: 12 }}>
            此操作将更新该订单下所有产品的支付状态。
          </p>
        </Modal>
      </Spin>
    </div>
  );
};

export default PaymentPending;
