/**
 * 产品列表页面
 */
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, Table, Input, Modal, Tabs, Descriptions, Progress } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { productApi } from '@/services/product'
import type { Product } from '@/types'

export default function ProductList() {
  const [search, setSearch] = useState('')
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // 获取产品列表
  const { data, isLoading } = useQuery({
    queryKey: ['products', search],
    queryFn: () => productApi.getProducts({ search, page_size: 1000 }),
  })

  // 获取产品订单
  const { data: orders } = useQuery({
    queryKey: ['product-orders', selectedProduct?.product_name],
    queryFn: () => productApi.getProductOrders(selectedProduct!.product_name),
    enabled: !!selectedProduct,
  })

  // 获取产品趋势
  const { data: trend } = useQuery({
    queryKey: ['product-trend', selectedProduct?.product_name],
    queryFn: () => productApi.getProductTrend(selectedProduct!.product_name),
    enabled: !!selectedProduct,
  })

  const handleViewDetail = (record: Product) => {
    setSelectedProduct(record)
    setIsModalOpen(true)
  }

  const columns = [
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
    },
    {
      title: '采购总额',
      dataIndex: 'total_purchase_amount',
      key: 'total_purchase_amount',
      render: (val: number) => `¥${val.toFixed(2)}`,
      sorter: (a: Product, b: Product) => a.total_purchase_amount - b.total_purchase_amount,
    },
    {
      title: '订单数量',
      dataIndex: 'total_order_count',
      key: 'total_order_count',
      sorter: (a: Product, b: Product) => a.total_order_count - b.total_order_count,
    },
    {
      title: '平均单价',
      dataIndex: 'avg_unit_price',
      key: 'avg_unit_price',
      render: (val: number) => `¥${val.toFixed(2)}`,
    },
    {
      title: '最后采购日期',
      dataIndex: 'last_purchase_date',
      key: 'last_purchase_date',
    },
    {
      title: '占比',
      key: 'percentage',
      render: (_: any, record: Product) => {
        const total = data?.items.reduce((sum, item) => sum + item.total_purchase_amount, 0) || 0
        const percentage = total > 0 ? (record.total_purchase_amount / total) * 100 : 0
        return <Progress percent={Number(percentage.toFixed(2))} size="small" />
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Product) => (
        <a onClick={() => handleViewDetail(record)}>查看详情</a>
      ),
    },
  ]

  // 趋势图表配置
  const trendChartOption = trend
    ? {
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: trend.map((item) => item.month).reverse(),
        },
        yAxis: [
          {
            type: 'value',
            name: '金额(¥)',
          },
          {
            type: 'value',
            name: '订单数',
          },
        ],
        series: [
          {
            name: '采购金额',
            type: 'line',
            data: trend.map((item) => item.amount).reverse(),
            itemStyle: { color: '#1890ff' },
          },
          {
            name: '订单数',
            type: 'bar',
            yAxisIndex: 1,
            data: trend.map((item) => item.count).reverse(),
            itemStyle: { color: '#52c41a' },
          },
        ],
      }
    : {}

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Input
          placeholder="搜索产品名称"
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 300, marginBottom: 16 }}
        />

        <Table
          dataSource={data?.items || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            showTotal: (total) => `共 ${total} 个产品`,
            pageSize: 20,
          }}
        />
      </Card>

      {/* 产品详情弹窗 */}
      <Modal
        title="产品详情"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={900}
      >
        {selectedProduct && (
          <Tabs
            items={[
              {
                key: 'info',
                label: '基本信息',
                children: (
                  <Descriptions column={2} bordered>
                    <Descriptions.Item label="产品名称">{selectedProduct.product_name}</Descriptions.Item>
                    <Descriptions.Item label="采购总额">
                      ¥{selectedProduct.total_purchase_amount.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="订单数量">{selectedProduct.total_order_count}</Descriptions.Item>
                    <Descriptions.Item label="平均单价">
                      ¥{selectedProduct.avg_unit_price.toFixed(2)}
                    </Descriptions.Item>
                    <Descriptions.Item label="最后采购日期">
                      {selectedProduct.last_purchase_date || '-'}
                    </Descriptions.Item>
                  </Descriptions>
                ),
              },
              {
                key: 'trend',
                label: '采购趋势',
                children: (
                  <ReactECharts option={trendChartOption} style={{ height: 300 }} />
                ),
              },
              {
                key: 'orders',
                label: `订单历史 (${orders?.length || 0})`,
                children: (
                  <Table
                    dataSource={orders || []}
                    columns={[
                      { title: '订单编号', dataIndex: 'order_no', key: 'order_no' },
                      { title: '采购金额', dataIndex: 'purchase_amount', key: 'purchase_amount', render: (val: number) => `¥${val.toFixed(2)}` },
                      { title: '订单日期', dataIndex: 'order_date', key: 'order_date' },
                      { title: '支付方式', dataIndex: 'payment_method', key: 'payment_method' },
                    ]}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                  />
                ),
              },
            ]}
          />
        )}
      </Modal>
    </div>
  )
}
