/**
 * 数据导入导出页面
 */
import React, { useState } from 'react';
import {
  Card,
  Upload,
  Button,
  message,
  Progress,
  Alert,
  Divider,
  Space,
  DatePicker,
  Select,
  Descriptions,
} from 'antd';
import {
  UploadOutlined,
  DownloadOutlined,
  InboxOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import dayjs from 'dayjs';
import type { Dayjs } from 'dayjs';
import { orderAPI } from '../services/api';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Dragger } = Upload;

const ImportExport: React.FC = () => {
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [shopFilter, setShopFilter] = useState<string | undefined>();

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: (file) => {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        file.type === 'application/vnd.ms-excel';
      if (!isExcel) {
        message.error('只能上传 Excel 文件!');
        return false;
      }
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB!');
        return false;
      }
      return true;
    },
    customRequest: async ({ file, onSuccess, onError, onProgress }) => {
      setImporting(true);
      setImportResult(null);

      try {
        // 模拟进度
        onProgress?.({ percent: 30 });

        const result = await orderAPI.importExcel(file as File);

        onProgress?.({ percent: 100 });
        onSuccess?.(result);

        setImportResult(result);
        message.success('导入成功!');
      } catch (error: any) {
        onError?.(error);
        message.error('导入失败: ' + (error.response?.data?.detail || error.message));
      } finally {
        setImporting(false);
      }
    },
  };

  const handleExport = () => {
    const filters = {
      start_date: dateRange?.[0]?.format('YYYY-MM-DD'),
      end_date: dateRange?.[1]?.format('YYYY-MM-DD'),
      shop_name: shopFilter,
    };

    const url = orderAPI.exportExcel(filters);
    window.open(url, '_blank');
    message.success('正在下载...');
  };

  return (
    <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
      {/* 导入区域 */}
      <Card title="数据导入" extra={<UploadOutlined />} style={{ marginBottom: 24 }}>
        <Alert
          message="导入说明"
          description={
            <ul>
              <li>支持 .xlsx 和 .xls 格式的 Excel 文件</li>
              <li>文件大小不超过 10MB</li>
              <li>Excel 应包含以下列: 订单编号、产品名称、采购金额、订单日期、支付状态等</li>
              <li>重复的订单号将被更新，新订单将被添加</li>
            </ul>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Dragger {...uploadProps} disabled={importing}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单个 Excel 文件上传，请确保文件格式正确
          </p>
        </Dragger>

        {importing && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={100} status="active" />
            <p style={{ textAlign: 'center', marginTop: 8 }}>正在导入数据...</p>
          </div>
        )}

        {importResult && (
          <Alert
            message="导入完成"
            description={
              <Descriptions column={2} size="small">
                <Descriptions.Item label="成功导入">
                  {importResult.imported_count} 条
                </Descriptions.Item>
                <Descriptions.Item label="失败">
                  {importResult.error_count} 条
                </Descriptions.Item>
                <Descriptions.Item label="采购总额">
                  ¥{importResult.total_amount?.toFixed(2)}
                </Descriptions.Item>
                <Descriptions.Item label="产品种类">
                  {importResult.total_products} 种
                </Descriptions.Item>
              </Descriptions>
            }
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            style={{ marginTop: 16 }}
          />
        )}
      </Card>

      <Divider />

      {/* 导出区域 */}
      <Card title="数据导出" extra={<DownloadOutlined />}>
        <Alert
          message="导出说明"
          description={
            <ul>
              <li>可以选择日期范围和店铺进行筛选导出</li>
              <li>导出格式为 Excel (.xlsx)</li>
              <li>包含订单数据和汇总统计</li>
            </ul>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <h4>筛选条件（可选）:</h4>
            <Space wrap>
              <RangePicker
                value={dateRange}
                onChange={(dates) => setDateRange(dates)}
                format="YYYY-MM-DD"
                placeholder={['开始日期', '结束日期']}
              />
              <Select
                style={{ width: 200 }}
                placeholder="选择店铺"
                allowClear
                value={shopFilter}
                onChange={setShopFilter}
              >
                <Option value="CAISHENDAO">CAISHENDAO</Option>
                <Option value="Kitchen maestro">Kitchen maestro</Option>
              </Select>
            </Space>
          </div>

          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExport}
            size="large"
          >
            导出 Excel 数据
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default ImportExport;
