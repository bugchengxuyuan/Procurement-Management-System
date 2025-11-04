import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  DatePicker,
  Input,
  Select,
  Space,
  Spin,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  ShoppingOutlined,
  DollarOutlined,
  AppstoreOutlined,
  CalendarOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import {
  getSupplierStats,
  getSupplierOrders,
  SupplierStats,
  SupplierProduct,
} from '@/services/supplier';
import { Order } from '@/services/order';
import { exportExcel, downloadExcelFile } from '@/services/import-export';
import dayjs from 'dayjs';
import ReactECharts from 'echarts-for-react';

const { RangePicker } = DatePicker;

const SupplierDetail: React.FC = () => {
  const navigate = useNavigate();
  const { supplierName } = useParams<{ supplierName: string }>();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<SupplierStats | null>(null);

  // 订单列表相关
  const [orders, setOrders] = useState<Order[]>([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [ordersTotal, setOrdersTotal] = useState(0);
  const [ordersPage, setOrdersPage] = useState(1);
  const [ordersPageSize, setOrdersPageSize] = useState(10);
  const [orderFilters, setOrderFilters] = useState<{
    product_name?: string;
    spec?: string;
    start_date?: string;
    end_date?: string;
  }>({});

  useEffect(() => {
    if (supplierName) {
      loadSupplierStats();
      loadSupplierOrders();
    }
  }, [supplierName]);

  useEffect(() => {
    if (supplierName) {
      loadSupplierOrders();
    }
  }, [ordersPage, ordersPageSize, orderFilters]);

  const loadSupplierStats = async () => {
    if (!supplierName) return;
    try {
      setLoading(true);
      const data = await getSupplierStats(decodeURIComponent(supplierName));
      setStats(data);
    } catch (error) {
      console.error('加载供应商统计失败:', error);
      message.error('加载供应商统计失败');
    } finally {
      setLoading(false);
    }
  };

  const loadSupplierOrders = async () => {
    if (!supplierName) return;
    try {
      setOrdersLoading(true);
      const data = await getSupplierOrders(decodeURIComponent(supplierName), {
        page: ordersPage,
        page_size: ordersPageSize,
        ...orderFilters,
      });
      setOrders(data.items);
      setOrdersTotal(data.total);
    } catch (error) {
      console.error('加载订单列表失败:', error);
    } finally {
      setOrdersLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/suppliers');
  };

  const handleExportOrders = async () => {
    try {
      const blob = await exportExcel({
        supplier: decodeURIComponent(supplierName || ''),
        ...orderFilters,
      });
      downloadExcelFile(
        blob,
        `${decodeURIComponent(supplierName || 'supplier')}_orders_${dayjs().format('YYYYMMDD')}.xlsx`
      );
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };

  const handleFilterChange = (key: string, value: any) => {
    setOrderFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
    setOrdersPage(1);
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      setOrderFilters((prev) => ({
        ...prev,
        start_date: dates[0].format('YYYY-MM-DD'),
        end_date: dates[1].format('YYYY-MM-DD'),
      }));
    } else {
      setOrderFilters((prev) => {
        const { start_date, end_date, ...rest } = prev;
        return rest;
      });
    }
    setOrdersPage(1);
  };

  // 月度趋势图配置
  const getTrendChartOption = () => {
    if (!stats || !stats.monthly_trend || stats.monthly_trend.length === 0) {
      return {};
    }

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
      },
      legend: {
        data: ['采购金额', '订单数量'],
      },
      xAxis: {
        type: 'category',
        data: stats.monthly_trend.map((item) => item.month),
      },
      yAxis: [
        {
          type: 'value',
          name: '采购金额(元)',
          position: 'left',
        },
        {
          type: 'value',
          name: '订单数量',
          position: 'right',
        },
      ],
      series: [
        {
          name: '采购金额',
          type: 'line',
          smooth: true,
          data: stats.monthly_trend.map((item) => item.amount),
          itemStyle: { color: '#1890ff' },
        },
        {
          name: '订单数量',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          data: stats.monthly_trend.map((item) => item.count),
          itemStyle: { color: '#52c41a' },
        },
      ],
    };
  };

  // 产品列表列定义
  const productColumns: ColumnsType<SupplierProduct> = [
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 200,
    },
    {
      title: '规格',
      dataIndex: 'spec',
      key: 'spec',
      width: 150,
      render: (spec) => spec || '-',
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
      render: (amount) => `¥${amount.toFixed(2)}`,
    },
    {
      title: '平均单价',
      dataIndex: 'avg_amount',
      key: 'avg_amount',
      width: 150,
      align: 'right',
      render: (amount) => `¥${amount.toFixed(2)}`,
    },
  ];

  // 订单列表列定义
  const orderColumns: ColumnsType<Order> = [
    {
      title: '订单日期',
      dataIndex: 'order_date',
      key: 'order_date',
      width: 120,
      render: (date) => dayjs(date).format('YYYY-MM-DD'),
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
      render: (spec) => spec || '-',
    },
    {
      title: '采购金额',
      dataIndex: 'purchase_amount',
      key: 'purchase_amount',
      width: 120,
      align: 'right',
      render: (amount) => `¥${amount.toFixed(2)}`,
    },
    {
      title: '订单状态',
      dataIndex: 'order_status',
      key: 'order_status',
      width: 100,
    },
  ];

  if (loading || !stats) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      {/* 返回按钮和标题 */}
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={handleBack}>
          返回列表
        </Button>
        <h2 style={{ margin: 0 }}>{stats.supplier_name}</h2>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="订单总数"
              value={stats.order_count}
              prefix={<ShoppingOutlined />}
              suffix="单"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="采购总额"
              value={stats.total_amount}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="产品种类"
              value={stats.product_count}
              prefix={<AppstoreOutlined />}
              suffix="种"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最近采购"
              value={dayjs(stats.last_order_date).format('YYYY-MM-DD')}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 月度趋势图 */}
      {stats.monthly_trend && stats.monthly_trend.length > 0 && (
        <Card title="📈 采购趋势" style={{ marginBottom: 24 }}>
          <ReactECharts option={getTrendChartOption()} style={{ height: 300 }} />
        </Card>
      )}

      {/* 产品列表 */}
      <Card title="📦 产品列表" style={{ marginBottom: 24 }}>
        <Table
          columns={productColumns}
          dataSource={stats.products}
          rowKey={(record) => `${record.product_name}-${record.spec}`}
          pagination={false}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* 订单历史 */}
      <Card title="📋 采购订单历史">
        {/* 筛选 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input
            placeholder="产品名称"
            allowClear
            style={{ width: 200 }}
            onChange={(e) => handleFilterChange('product_name', e.target.value)}
          />
          <Input
            placeholder="规格"
            allowClear
            style={{ width: 150 }}
            onChange={(e) => handleFilterChange('spec', e.target.value)}
          />
          <RangePicker onChange={handleDateRangeChange} />
          <Button icon={<DownloadOutlined />} onClick={handleExportOrders}>
            导出订单
          </Button>
        </Space>

        {/* 订单表格 */}
        <Table
          columns={orderColumns}
          dataSource={orders}
          rowKey="id"
          loading={ordersLoading}
          pagination={{
            current: ordersPage,
            pageSize: ordersPageSize,
            total: ordersTotal,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条订单`,
            onChange: (page, pageSize) => {
              setOrdersPage(page);
              setOrdersPageSize(pageSize);
            },
          }}
          scroll={{ x: 1000 }}
        />
      </Card>
    </div>
  );
};

export default SupplierDetail;
