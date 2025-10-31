/**
 * 订单列表页面
 */
import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Button,
  Input,
  DatePicker,
  Select,
  Space,
  message,
  Modal,
  Form,
  InputNumber,
  Tag,
  Popconfirm,
} from 'antd';
import { PlusOutlined, SearchOutlined, ExportOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import { orderAPI } from '../services/api';
import type { PurchaseOrder, OrderFilters } from '../types';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Search } = Input;

const OrderList: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [filters, setFilters] = useState<OrderFilters>({});
  const [modalVisible, setModalVisible] = useState(false);
  const [editingOrder, setEditingOrder] = useState<PurchaseOrder | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadOrders();
  }, [page, pageSize, filters]);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const response = await orderAPI.getOrders(page, pageSize, filters);
      setOrders(response.orders);
      setTotal(response.total);
    } catch (error) {
      message.error('加载订单失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, search: value });
    setPage(1);
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates) {
      setFilters({
        ...filters,
        start_date: dates[0].format('YYYY-MM-DD'),
        end_date: dates[1].format('YYYY-MM-DD'),
      });
    } else {
      const newFilters = { ...filters };
      delete newFilters.start_date;
      delete newFilters.end_date;
      setFilters(newFilters);
    }
    setPage(1);
  };

  const handleShopChange = (value: string | undefined) => {
    if (value) {
      setFilters({ ...filters, shop_name: value });
    } else {
      const newFilters = { ...filters };
      delete newFilters.shop_name;
      setFilters(newFilters);
    }
    setPage(1);
  };

  const handleStatusChange = (value: string | undefined) => {
    if (value) {
      setFilters({ ...filters, payment_status: value });
    } else {
      const newFilters = { ...filters };
      delete newFilters.payment_status;
      setFilters(newFilters);
    }
    setPage(1);
  };

  const handleCreate = () => {
    setEditingOrder(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: PurchaseOrder) => {
    setEditingOrder(record);
    form.setFieldsValue({
      ...record,
      order_date: record.order_date ? dayjs(record.order_date) : undefined,
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await orderAPI.deleteOrder(id);
      message.success('删除成功');
      loadOrders();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const orderData = {
        ...values,
        order_date: values.order_date?.toISOString(),
      };

      if (editingOrder) {
        await orderAPI.updateOrder(editingOrder.id, orderData);
        message.success('更新成功');
      } else {
        await orderAPI.createOrder(orderData);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadOrders();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleExport = () => {
    const url = orderAPI.exportExcel(filters);
    window.open(url, '_blank');
  };

  const columns: ColumnsType<PurchaseOrder> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
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
      width: 200,
    },
    {
      title: '采购金额',
      dataIndex: 'purchase_amount',
      key: 'purchase_amount',
      width: 120,
      render: (value: number) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.purchase_amount - b.purchase_amount,
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '店铺',
      dataIndex: 'shop_name',
      key: 'shop_name',
      width: 150,
    },
    {
      title: '支付状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      width: 120,
      render: (status: string) => {
        const color = status === '已付款' ? 'green' : status === '先采后付' ? 'orange' : 'default';
        return <Tag color={color}>{status || '-'}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定删除此订单？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 筛选栏 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Search
            placeholder="搜索订单号或产品名称"
            onSearch={handleSearch}
            style={{ width: 250 }}
            allowClear
          />
          <RangePicker onChange={handleDateRangeChange} format="YYYY-MM-DD" />
          <Select
            style={{ width: 150 }}
            placeholder="选择店铺"
            allowClear
            onChange={handleShopChange}
          >
            <Option value="CAISHENDAO">CAISHENDAO</Option>
            <Option value="Kitchen maestro">Kitchen maestro</Option>
          </Select>
          <Select
            style={{ width: 150 }}
            placeholder="支付状态"
            allowClear
            onChange={handleStatusChange}
          >
            <Option value="已付款">已付款</Option>
            <Option value="先采后付">先采后付</Option>
            <Option value="先用后付">先用后付</Option>
          </Select>
          <Button icon={<PlusOutlined />} type="primary" onClick={handleCreate}>
            新建订单
          </Button>
          <Button icon={<ExportOutlined />} onClick={handleExport}>
            导出数据
          </Button>
          <Button icon={<ReloadOutlined />} onClick={loadOrders}>
            刷新
          </Button>
        </Space>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize);
            },
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 编辑/创建对话框 */}
      <Modal
        title={editingOrder ? '编辑订单' : '新建订单'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="订单编号"
            name="order_no"
            rules={[{ required: true, message: '请输入订单编号' }]}
          >
            <Input placeholder="请输入订单编号" disabled={!!editingOrder} />
          </Form.Item>
          <Form.Item
            label="产品名称"
            name="product_name"
            rules={[{ required: true, message: '请输入产品名称' }]}
          >
            <Input placeholder="请输入产品名称" />
          </Form.Item>
          <Form.Item
            label="采购金额"
            name="purchase_amount"
            rules={[{ required: true, message: '请输入采购金额' }]}
          >
            <InputNumber min={0} precision={2} style={{ width: '100%' }} placeholder="请输入采购金额" />
          </Form.Item>
          <Form.Item label="订单日期" name="order_date">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            label="店铺名称"
            name="shop_name"
            rules={[{ required: true, message: '请选择店铺' }]}
          >
            <Select placeholder="请选择店铺">
              <Option value="CAISHENDAO">CAISHENDAO</Option>
              <Option value="Kitchen maestro">Kitchen maestro</Option>
            </Select>
          </Form.Item>
          <Form.Item label="支付状态" name="payment_status">
            <Select placeholder="请选择支付状态">
              <Option value="已付款">已付款</Option>
              <Option value="先采后付">先采后付</Option>
              <Option value="先用后付">先用后付</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OrderList;
