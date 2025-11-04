import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Input,
  DatePicker,
  Select,
  Modal,
  Form,
  InputNumber,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Upload,
  Tag,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  UploadOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import {
  getOrders,
  createOrder,
  updateOrder,
  deleteOrder,
  Order,
  OrderListParams,
} from '@/services/order';
import { importExcel, exportExcel, downloadExcelFile } from '@/services/import-export';

const { RangePicker } = DatePicker;

const OrderList: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [filters, setFilters] = useState<OrderListParams>({});
  const [modalVisible, setModalVisible] = useState(false);
  const [editingOrder, setEditingOrder] = useState<Order | null>(null);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadOrders();
  }, [currentPage, pageSize, filters]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const params: OrderListParams = {
        page: currentPage,
        size: pageSize,
        ...filters,
      };
      const data = await getOrders(params);
      setOrders(data.items);
      setTotal(data.total);
    } catch (error) {
      message.error('加载订单失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (values: any) => {
    const newFilters: OrderListParams = {
      search: values.search,
      product_name: values.product_name,
      spec: values.spec,
      supplier: values.supplier,
      payment_status: values.payment_status,
    };

    if (values.dateRange && values.dateRange.length === 2) {
      newFilters.start_date = values.dateRange[0].format('YYYY-MM-DD');
      newFilters.end_date = values.dateRange[1].format('YYYY-MM-DD');
    }

    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handleReset = () => {
    setFilters({});
    setCurrentPage(1);
    form.resetFields();
  };

  const handleCreate = () => {
    setEditingOrder(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Order) => {
    setEditingOrder(record);
    form.setFieldsValue({
      ...record,
      order_date: dayjs(record.order_date),
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteOrder(id);
      message.success('删除成功');
      loadOrders();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      const data = {
        ...values,
        order_date: values.order_date.format('YYYY-MM-DD'),
      };

      if (editingOrder) {
        await updateOrder(editingOrder.id, data);
        message.success('更新成功');
      } else {
        await createOrder(data);
        message.success('创建成功');
      }

      setModalVisible(false);
      loadOrders();
    } catch (error: any) {
      if (error.response) {
        message.error(error.response.data.detail || '操作失败');
      }
    }
  };

  const handleImport = async (file: File) => {
    try {
      setUploading(true);
      const result = await importExcel(file);
      message.success(
        `导入完成！成功: ${result.success_count}条, 失败: ${result.error_count}条`
      );
      if (result.error_count > 0) {
        Modal.info({
          title: '导入错误详情',
          width: 800,
          content: (
            <div style={{ maxHeight: 400, overflow: 'auto' }}>
              {result.errors.map((err, idx) => (
                <div key={idx}>
                  行{err.row || '?'}: {err.error}
                </div>
              ))}
            </div>
          ),
        });
      }
      setImportModalVisible(false);
      loadOrders();
    } catch (error) {
      message.error('导入失败');
    } finally {
      setUploading(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await exportExcel(filters);
      downloadExcelFile(blob, `orders_export_${dayjs().format('YYYYMMDD')}.xlsx`);
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const getPaymentStatusTag = (status?: string) => {
    if (!status) return '-';

    const statusConfig: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
      '即时付款': { color: 'blue', icon: <DollarOutlined />, text: '即时付款' },
      '账期未到': { color: 'orange', icon: <ClockCircleOutlined />, text: '账期未到' },
      '账期已结': { color: 'green', icon: <CheckCircleOutlined />, text: '账期已结' },
    };

    const config = statusConfig[status];
    if (!config) return status;

    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
  };

  const columns: ColumnsType<Order> = [
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
      title: '规格',
      dataIndex: 'spec',
      key: 'spec',
      width: 120,
      render: (spec: string | null) => spec || '-',
    },
    {
      title: '采购金额',
      dataIndex: 'purchase_amount',
      key: 'purchase_amount',
      width: 120,
      render: (amount: number) => `¥${amount.toFixed(2)}`,
    },
    {
      title: '供应商',
      dataIndex: 'supplier',
      key: 'supplier',
      width: 200,
      render: (supplier: string | null) => supplier || '-',
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
      render: (status: string) => getPaymentStatusTag(status),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_: any, record: Order) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确定删除此订单?"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>订单管理</h2>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Form form={form} onFinish={handleSearch} layout="vertical">
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="search" label="快速搜索">
                <Input placeholder="订单号/产品名/供应商" prefix={<SearchOutlined />} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="product_name" label="产品名称">
                <Input placeholder="请输入产品名称" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="spec" label="规格">
                <Input placeholder="请输入规格" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="supplier" label="供应商">
                <Input placeholder="请输入供应商" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="payment_status" label="付款状态">
                <Select placeholder="请选择" allowClear>
                  <Select.Option value="即时付款">即时付款</Select.Option>
                  <Select.Option value="账期未到">账期未到</Select.Option>
                  <Select.Option value="账期已结">账期已结</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={16}>
              <Form.Item name="dateRange" label="日期范围">
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row>
            <Col span={24}>
              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                    查询
                  </Button>
                  <Button onClick={handleReset} icon={<ReloadOutlined />}>
                    重置
                  </Button>
                </Space>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {/* 操作按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新建订单
          </Button>
          <Button icon={<UploadOutlined />} onClick={() => setImportModalVisible(true)}>
            导入Excel
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出Excel
          </Button>
        </Space>
      </div>

      {/* 订单列表 */}
      <Table
        columns={columns}
        dataSource={orders}
        rowKey="id"
        loading={loading}
        pagination={{
          current: currentPage,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setCurrentPage(page);
            setPageSize(pageSize);
          },
        }}
        scroll={{ x: 1500 }}
      />

      {/* 新建/编辑订单Modal */}
      <Modal
        title={editingOrder ? '编辑订单' : '新建订单'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="order_no"
            label="订单编号"
            rules={[
              { required: true, message: '请输入订单编号' },
              { len: 19, message: '订单编号必须是19位数字' },
            ]}
          >
            <Input placeholder="请输入19位订单编号" disabled={!!editingOrder} />
          </Form.Item>
          <Form.Item
            name="product_name"
            label="产品名称"
            rules={[{ required: true, message: '请输入产品名称' }]}
          >
            <Input placeholder="请输入产品名称" />
          </Form.Item>
          <Form.Item
            name="spec"
            label="规格"
          >
            <Input placeholder="请输入规格（可选）" />
          </Form.Item>
          <Form.Item
            name="purchase_amount"
            label="采购金额"
            rules={[{ required: true, message: '请输入采购金额' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="请输入采购金额"
              precision={2}
              min={0}
              prefix="¥"
            />
          </Form.Item>
          <Form.Item
            name="supplier"
            label="供应商"
          >
            <Input placeholder="请输入供应商（可选）" />
          </Form.Item>
          <Form.Item
            name="order_date"
            label="订单日期"
            rules={[{ required: true, message: '请选择订单日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="payment_status"
            label="付款状态"
            rules={[{ required: true, message: '请选择付款状态' }]}
          >
            <Select placeholder="请选择">
              <Select.Option value="即时付款">即时付款</Select.Option>
              <Select.Option value="账期未到">账期未到</Select.Option>
              <Select.Option value="账期已结">账期已结</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="receive_date"
            label="确认收货日期"
          >
            <DatePicker style={{ width: '100%' }} placeholder="仅账期订单需要填写" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 导入Excel Modal */}
      <Modal
        title="导入Excel"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={null}
      >
        <Upload
          beforeUpload={(file) => {
            handleImport(file);
            return false;
          }}
          accept=".xlsx,.xls"
          showUploadList={false}
        >
          <Button icon={<UploadOutlined />} loading={uploading} block>
            {uploading ? '导入中...' : '选择Excel文件'}
          </Button>
        </Upload>
        <div style={{ marginTop: 16, color: '#999' }}>
          <p>支持格式: .xlsx, .xls</p>
          <p>最大文件: 10MB</p>
        </div>
      </Modal>
    </div>
  );
};

export default OrderList;
