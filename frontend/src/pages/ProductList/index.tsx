import React, { useEffect, useState } from 'react';
import {
  Table,
  Input,
  Card,
  Progress,
  Statistic,
  Row,
  Col,
  Modal,
  Tabs,
} from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { Line } from '@ant-design/charts';
import dayjs from 'dayjs';
import { getProducts, getProduct, Product, ProductDetailResponse } from '@/services/product';

const ProductList: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [searchText, setSearchText] = useState('');
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [productDetail, setProductDetail] = useState<ProductDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const params = {
        sort_by: 'total_purchase_amount',
        sort_order: 'desc',
        search: searchText,
      };
      const data = await getProducts(params);
      setProducts(data.items);
      setTotalAmount(data.total_amount);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadProducts();
  };

  const handleViewDetail = async (productId: number) => {
    try {
      setDetailLoading(true);
      setDetailModalVisible(true);
      const data = await getProduct(productId);
      setProductDetail(data);
    } catch (error) {
      console.error('Failed to load product detail:', error);
    } finally {
      setDetailLoading(false);
    }
  };

  const columns: ColumnsType<Product> = [
    {
      title: '排名',
      key: 'rank',
      width: 80,
      render: (_: any, __: any, index: number) => index + 1,
    },
    {
      title: '产品名称',
      dataIndex: 'product_name',
      key: 'product_name',
      width: 200,
    },
    {
      title: '累计采购金额',
      dataIndex: 'total_purchase_amount',
      key: 'total_purchase_amount',
      width: 200,
      render: (amount: number, record: Product) => (
        <div>
          <div style={{ marginBottom: 4 }}>¥{amount.toFixed(2)}</div>
          <Progress
            percent={record.percentage || 0}
            size="small"
            format={(percent) => `${percent?.toFixed(1)}%`}
          />
        </div>
      ),
    },
    {
      title: '订单数量',
      dataIndex: 'total_order_count',
      key: 'total_order_count',
      width: 100,
      render: (count: number) => `${count}单`,
    },
    {
      title: '平均单价',
      dataIndex: 'avg_unit_price',
      key: 'avg_unit_price',
      width: 120,
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '最近采购',
      dataIndex: 'last_purchase_date',
      key: 'last_purchase_date',
      width: 120,
      render: (date: string | null) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: Product) => (
        <a onClick={() => handleViewDetail(record.id)}>查看详情</a>
      ),
    },
  ];

  // 月度趋势图配置
  const trendConfig = productDetail ? {
    data: productDetail.monthly_trend.map(item => ({
      month: item.month,
      value: item.amount,
      category: '采购金额',
    })),
    xField: 'month',
    yField: 'value',
    seriesField: 'category',
    smooth: true,
    label: {
      style: {
        fill: '#aaa',
      },
    },
    yAxis: {
      label: {
        formatter: (v: string) => `¥${(parseFloat(v) / 1000).toFixed(1)}k`,
      },
    },
    point: {
      size: 5,
      shape: 'diamond',
    },
  } : null;

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>产品管理</h2>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="产品总数"
              value={products.length}
              suffix="种"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="累计采购金额"
              value={totalAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="平均产品采购额"
              value={products.length > 0 ? totalAmount / products.length : 0}
              precision={2}
              prefix="¥"
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索 */}
      <Card style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索产品名称"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onPressEnter={handleSearch}
          style={{ width: 300 }}
          allowClear
        />
      </Card>

      {/* 产品列表 */}
      <Table
        columns={columns}
        dataSource={products}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showTotal: (total) => `共 ${total} 种产品`,
        }}
      />

      {/* 产品详情Modal */}
      <Modal
        title="产品详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={900}
        loading={detailLoading}
      >
        {productDetail && (
          <Tabs
            items={[
              {
                key: 'info',
                label: '基本信息',
                children: (
                  <Row gutter={16}>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="累计采购额"
                          value={productDetail.product.total_purchase_amount}
                          precision={2}
                          prefix="¥"
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="订单数量"
                          value={productDetail.product.total_order_count}
                          suffix="单"
                        />
                      </Card>
                    </Col>
                    <Col span={8}>
                      <Card>
                        <Statistic
                          title="平均单价"
                          value={productDetail.product.avg_unit_price}
                          precision={2}
                          prefix="¥"
                        />
                      </Card>
                    </Col>
                  </Row>
                ),
              },
              {
                key: 'trend',
                label: '采购趋势',
                children: trendConfig && (
                  <div>
                    <h4>最近6个月采购趋势</h4>
                    <Line {...trendConfig} height={300} />
                  </div>
                ),
              },
              {
                key: 'orders',
                label: '订单历史',
                children: (
                  <Table
                    dataSource={productDetail.recent_orders}
                    columns={[
                      {
                        title: '订单日期',
                        dataIndex: 'order_date',
                        key: 'order_date',
                        render: (date: string) => dayjs(date).format('YYYY-MM-DD'),
                      },
                      {
                        title: '订单编号',
                        dataIndex: 'order_no',
                        key: 'order_no',
                      },
                      {
                        title: '采购金额',
                        dataIndex: 'purchase_amount',
                        key: 'purchase_amount',
                        render: (amount: number) => `¥${amount.toFixed(2)}`,
                      },
                      {
                        title: '订单状态',
                        dataIndex: 'order_status',
                        key: 'order_status',
                      },
                    ]}
                    rowKey="id"
                    pagination={false}
                    size="small"
                  />
                ),
              },
            ]}
          />
        )}
      </Modal>
    </div>
  );
};

export default ProductList;
