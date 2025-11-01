/**
 * 订单列表页面
 */
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Card,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Select,
  message,
  Popconfirm,
  Row,
  Col,
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { orderApi, type OrderListParams } from '@/services/order'
import type { Order, OrderCreate } from '@/types'

export default function OrderList() {
  const queryClient = useQueryClient()
  const [form] = Form.useForm()
  const [searchForm] = Form.useForm()

  const [params, setParams] = useState<OrderListParams>({ page: 1, page_size: 20 })
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingOrder, setEditingOrder] = useState<Order | null>(null)

  // 获取订单列表
  const { data, isLoading } = useQuery({
    queryKey: ['orders', params],
    queryFn: () => orderApi.getOrders(params),
  })

  // 创建/更新订单
  const mutation = useMutation({
    mutationFn: (values: any) => {
      if (editingOrder) {
        return orderApi.updateOrder(editingOrder.id, values)
      }
      return orderApi.createOrder(values as OrderCreate)
    },
    onSuccess: () => {
      message.success(editingOrder ? '更新成功' : '创建成功')
      setIsModalOpen(false)
      setEditingOrder(null)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
    onError: () => {
      message.error('操作失败')
    },
  })

  // 删除订单
  const deleteMutation = useMutation({
    mutationFn: orderApi.deleteOrder,
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
  })

  const handleAdd = () => {
    setEditingOrder(null)
    form.resetFields()
    setIsModalOpen(true)
  }

  const handleEdit = (record: Order) => {
    setEditingOrder(record)
    form.setFieldsValue({
      ...record,
      order_date: dayjs(record.order_date),
      record_time: dayjs(record.record_time),
    })
    setIsModalOpen(true)
  }

  const handleSubmit = async () => {
    const values = await form.validateFields()
    mutation.mutate({
      ...values,
      order_date: values.order_date.format('YYYY-MM-DD'),
      record_time: values.record_time.format('YYYY-MM-DD HH:mm:ss'),
    })
  }

  const handleSearch = (values: any) => {
    setParams({
      ...params,
      page: 1,
      ...values,
      start_date: values.start_date?.format('YYYY-MM-DD'),
      end_date: values.end_date?.format('YYYY-MM-DD'),
    })
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
      title: '订单状态',
      dataIndex: 'order_status',
      key: 'order_status',
    },
    {
      title: '支付方式',
      dataIndex: 'payment_method',
      key: 'payment_method',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Order) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除?"
            onConfirm={() => deleteMutation.mutate(record.id)}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 搜索表单 */}
        <Form form={searchForm} onFinish={handleSearch} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="search">
                <Input placeholder="订单编号/产品名称" prefix={<SearchOutlined />} />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="order_status">
                <Select placeholder="订单状态" allowClear>
                  <Select.Option value="已付款">已付款</Select.Option>
                  <Select.Option value="先采后付">先采后付</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="payment_method">
                <Select placeholder="支付方式" allowClear>
                  <Select.Option value="已付款">已付款</Select.Option>
                  <Select.Option value="先采后付">先采后付</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={10}>
              <Space>
                <Button type="primary" htmlType="submit">
                  搜索
                </Button>
                <Button onClick={() => { searchForm.resetFields(); setParams({ page: 1, page_size: 20 }) }}>
                  重置
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                  新增订单
                </Button>
              </Space>
            </Col>
          </Row>
        </Form>

        {/* 表格 */}
        <Table
          dataSource={data?.items || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: params.page,
            pageSize: params.page_size,
            total: data?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => setParams({ ...params, page, page_size: pageSize }),
          }}
        />
      </Card>

      {/* 新增/编辑弹窗 */}
      <Modal
        title={editingOrder ? '编辑订单' : '新增订单'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false)
          setEditingOrder(null)
          form.resetFields()
        }}
        width={600}
        confirmLoading={mutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          {!editingOrder && (
            <Form.Item
              name="order_no"
              label="订单编号"
              rules={[{ required: true, message: '请输入订单编号' }]}
            >
              <Input placeholder="订单编号" />
            </Form.Item>
          )}
          <Form.Item
            name="product_name"
            label="产品名称"
            rules={[{ required: true, message: '请输入产品名称' }]}
          >
            <Input placeholder="产品名称" />
          </Form.Item>
          <Form.Item
            name="purchase_amount"
            label="采购金额"
            rules={[{ required: true, message: '请输入采购金额' }]}
          >
            <InputNumber
              placeholder="采购金额"
              style={{ width: '100%' }}
              min={0}
              precision={2}
            />
          </Form.Item>
          <Form.Item
            name="order_date"
            label="订单日期"
            rules={[{ required: true, message: '请选择订单日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="order_status"
            label="订单状态"
            rules={[{ required: true, message: '请选择订单状态' }]}
          >
            <Select>
              <Select.Option value="已付款">已付款</Select.Option>
              <Select.Option value="先采后付">先采后付</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="payment_method"
            label="支付方式"
            rules={[{ required: true, message: '请选择支付方式' }]}
          >
            <Select>
              <Select.Option value="已付款">已付款</Select.Option>
              <Select.Option value="先采后付">先采后付</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="record_time"
            label="记录时间"
            rules={[{ required: true, message: '请选择记录时间' }]}
          >
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
