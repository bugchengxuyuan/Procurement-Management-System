import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Input,
  Select,
  Row,
  Col,
  Statistic,
  Space,
  Button,
} from 'antd';
import {
  SearchOutlined,
  ShopOutlined,
  ShoppingOutlined,
  AppstoreOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import {
  getSupplierList,
  SupplierListItem,
  SupplierListParams,
} from '@/services/supplier';
import dayjs from 'dayjs';

const SupplierList: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [suppliers, setSuppliers] = useState<SupplierListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'total_amount' | 'order_count' | 'last_order_date'>('total_amount');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  // 统计数据
  const [totalSuppliers, setTotalSuppliers] = useState(0);
  const [totalOrders, setTotalOrders] = useState(0);
  const [totalAmount, setTotalAmount] = useState(0);
  const [totalProducts, setTotalProducts] = useState(0);

  useEffect(() => {
    loadSuppliers();
  }, [currentPage, pageSize, search, sortBy, sortOrder]);

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const params: SupplierListParams = {
        page: currentPage,
        page_size: pageSize,
        search: search || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      const data = await getSupplierList(params);
      setSuppliers(data.items);
      setTotal(data.total);

      // 计算统计数据
      setTotalSuppliers(data.total);
      const orders = data.items.reduce((sum, item) => sum + item.order_count, 0);
      const amount = data.items.reduce((sum, item) => sum + item.total_amount, 0);
      const products = data.items.reduce((sum, item) => sum + item.product_count, 0);
      setTotalOrders(orders);
      setTotalAmount(amount);
      setTotalProducts(products);
    } catch (error) {
      console.error('加载供应商列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearch(value);
    setCurrentPage(1);
  };

  const handleSortChange = (value: string) => {
    const [field, order] = value.split('-');
    setSortBy(field as any);
    setSortOrder(order as any);
    setCurrentPage(1);
  };

  const handleViewDetail = (supplierName: string) => {
    navigate(`/suppliers/${encodeURIComponent(supplierName)}`);
  };

  const columns: ColumnsType<SupplierListItem> = [
    {
      title: '序号',
      key: 'index',
      width: 60,
      render: (_: any, __: any, index: number) => (currentPage - 1) * pageSize + index + 1,
    },
    {
      title: '供应商名称',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      width: 300,
      ellipsis: true,
    },
    {
      title: '订单数',
      dataIndex: 'order_count',
      key: 'order_count',
      width: 100,
      align: 'right',
    },
    {
      title: '采购总额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 150,
      align: 'right',
      render: (amount: number) => `¥${amount.toFixed(2)}`,
    },
    {
      title: '产品种类',
      dataIndex: 'product_count',
      key: 'product_count',
      width: 100,
      align: 'right',
      render: (count: number) => `${count}种`,
    },
    {
      title: '最近采购',
      dataIndex: 'last_order_date',
      key: 'last_order_date',
      width: 120,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_: any, record: SupplierListItem) => (
        <Button type="link" size="small" onClick={() => handleViewDetail(record.supplier_name)}>
          查看详情
        </Button>
      ),
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>供应商管理</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="供应商总数"
              value={totalSuppliers}
              prefix={<ShopOutlined />}
              suffix="个"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="订单总数"
              value={totalOrders}
              prefix={<ShoppingOutlined />}
              suffix="单"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="产品种类"
              value={totalProducts}
              prefix={<AppstoreOutlined />}
              suffix="种"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="采购总额"
              value={totalAmount}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="middle">
          <Input.Search
            placeholder="搜索供应商名称"
            allowClear
            style={{ width: 300 }}
            onSearch={handleSearch}
            prefix={<SearchOutlined />}
          />
          <Select
            style={{ width: 200 }}
            value={`${sortBy}-${sortOrder}`}
            onChange={handleSortChange}
            options={[
              { label: '采购金额 ↓', value: 'total_amount-desc' },
              { label: '采购金额 ↑', value: 'total_amount-asc' },
              { label: '订单数量 ↓', value: 'order_count-desc' },
              { label: '订单数量 ↑', value: 'order_count-asc' },
              { label: '最近采购 ↓', value: 'last_order_date-desc' },
              { label: '最近采购 ↑', value: 'last_order_date-asc' },
            ]}
          />
        </Space>
      </Card>

      {/* 供应商列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={suppliers}
          rowKey="supplier_name"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个供应商`,
            onChange: (page, pageSize) => {
              setCurrentPage(page);
              setPageSize(pageSize);
            },
          }}
          scroll={{ x: 1000 }}
        />
      </Card>
    </div>
  );
};

export default SupplierList;
