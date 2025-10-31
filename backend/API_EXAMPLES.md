# API使用示例

本文档提供了采购管理系统API的实际使用示例。

## 前提条件

确保后端服务已启动：
```bash
cd backend
python main.py
```

服务地址: `http://localhost:8000`

---

## 1. 订单管理

### 1.1 创建订单

```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_no": "9999999999999999999",
    "product_name": "测试产品",
    "purchase_amount": 1000.00,
    "order_date": "2025-10-31",
    "order_status": "已付款",
    "payment_method": "已付款"
  }'
```

### 1.2 获取订单列表（分页）

```bash
# 基本查询
curl "http://localhost:8000/api/orders?page=1&size=10"

# 按产品名称筛选
curl "http://localhost:8000/api/orders?product_name=高铸胶"

# 按日期范围筛选
curl "http://localhost:8000/api/orders?start_date=2025-01-01&end_date=2025-10-31"

# 按状态筛选
curl "http://localhost:8000/api/orders?order_status=先采后付"

# 搜索订单号或产品名
curl "http://localhost:8000/api/orders?search=管道疏通剂"

# 组合查询
curl "http://localhost:8000/api/orders?page=1&size=20&order_status=已付款&start_date=2025-10-01&sort_by=purchase_amount&sort_order=desc"
```

### 1.3 获取订单详情

```bash
curl "http://localhost:8000/api/orders/1"
```

### 1.4 更新订单

```bash
curl -X PUT "http://localhost:8000/api/orders/1" \
  -H "Content-Type: application/json" \
  -d '{
    "purchase_amount": 1200.00,
    "order_status": "已付款"
  }'
```

### 1.5 删除订单

```bash
curl -X DELETE "http://localhost:8000/api/orders/1"
```

---

## 2. 产品管理

### 2.1 获取产品列表

```bash
# 按采购金额排序（默认）
curl "http://localhost:8000/api/products"

# 按订单数量排序
curl "http://localhost:8000/api/products?sort_by=total_order_count&sort_order=desc"

# 搜索产品
curl "http://localhost:8000/api/products?search=胶"
```

### 2.2 获取产品详情

```bash
# 按ID查询
curl "http://localhost:8000/api/products/97"

# 按名称查询
curl "http://localhost:8000/api/products/name/高铸胶"
```

---

## 3. 统计分析

### 3.1 Dashboard统计

```bash
curl "http://localhost:8000/api/statistics/dashboard"
```

**返回数据包含**:
- 总采购金额
- 总订单数
- 总产品数
- 本月采购金额
- 本月环比增长率
- 支付方式分布
- 月度采购趋势（最近6个月）
- TOP 5产品

### 3.2 月度趋势

```bash
# 最近6个月
curl "http://localhost:8000/api/statistics/monthly-trend?months=6"

# 最近12个月
curl "http://localhost:8000/api/statistics/monthly-trend?months=12"
```

### 3.3 先采后付到期订单

```bash
# 7天内到期的订单
curl "http://localhost:8000/api/statistics/payment-due?days_threshold=7"

# 30天内到期的订单
curl "http://localhost:8000/api/statistics/payment-due?days_threshold=30"
```

**状态说明**:
- `overdue`: 已逾期
- `warning`: 在阈值天数内即将到期
- `normal`: 正常

### 3.4 日期范围统计

```bash
# 查询指定日期范围的统计数据
curl "http://localhost:8000/api/statistics/date-range?start_date=2025-01-01&end_date=2025-10-31"
```

---

## 4. 数据导入导出

### 4.1 Excel导入

```bash
# 导入Excel文件
curl -X POST "http://localhost:8000/api/import/excel" \
  -F "file=@采购表-2（最新版.xlsx"
```

**返回数据**:
```json
{
    "total_rows": 863,
    "success_count": 792,
    "error_count": 71,
    "errors": [
        {"row": 73, "error": "采购金额缺失"},
        {"order_no": "123456", "error": "订单编号已存在"}
    ]
}
```

### 4.2 Excel导出

```bash
# 导出所有订单
curl "http://localhost:8000/api/export/excel" -o orders_export.xlsx

# 导出筛选后的订单
curl "http://localhost:8000/api/export/excel?product_name=高铸胶&start_date=2025-01-01" -o orders_filtered.xlsx

# 导出先采后付订单
curl "http://localhost:8000/api/export/excel?payment_method=先采后付" -o orders_credit.xlsx
```

---

## 5. Python示例

### 5.1 使用requests库

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. 创建订单
def create_order():
    url = f"{BASE_URL}/api/orders"
    data = {
        "order_no": "8888888888888888888",
        "product_name": "测试产品Python",
        "purchase_amount": 2000.00,
        "order_date": "2025-10-31",
        "order_status": "已付款",
        "payment_method": "已付款"
    }
    response = requests.post(url, json=data)
    print("创建订单:", response.json())

# 2. 获取订单列表
def get_orders():
    url = f"{BASE_URL}/api/orders"
    params = {
        "page": 1,
        "size": 10,
        "product_name": "高铸胶"
    }
    response = requests.get(url, params=params)
    print("订单列表:", response.json())

# 3. 获取Dashboard统计
def get_dashboard():
    url = f"{BASE_URL}/api/statistics/dashboard"
    response = requests.get(url)
    data = response.json()

    print(f"总采购金额: ¥{data['total_amount']:.2f}")
    print(f"总订单数: {data['total_orders']}")
    print(f"总产品数: {data['total_products']}")
    print(f"本月采购: ¥{data['this_month_amount']:.2f}")
    print(f"环比增长: {data['this_month_growth']:.2f}%")

    print("\nTOP 5产品:")
    for product in data['top_products']:
        print(f"  {product['product_name']}: ¥{product['total_amount']:.2f} ({product['percentage']}%)")

# 4. 导出Excel
def export_excel():
    url = f"{BASE_URL}/api/export/excel"
    params = {
        "start_date": "2025-01-01",
        "end_date": "2025-10-31"
    }
    response = requests.get(url, params=params)

    with open("orders_export.xlsx", "wb") as f:
        f.write(response.content)
    print("导出成功: orders_export.xlsx")

# 执行示例
if __name__ == "__main__":
    create_order()
    get_orders()
    get_dashboard()
    export_excel()
```

### 5.2 使用httpx库（支持异步）

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def async_example():
    async with httpx.AsyncClient() as client:
        # 并发请求多个API
        tasks = [
            client.get(f"{BASE_URL}/api/orders?page=1&size=10"),
            client.get(f"{BASE_URL}/api/products"),
            client.get(f"{BASE_URL}/api/statistics/dashboard"),
        ]

        responses = await asyncio.gather(*tasks)

        print("订单列表:", responses[0].json()['total'])
        print("产品列表:", responses[1].json()['total'])
        print("Dashboard:", responses[2].json()['total_amount'])

# 运行异步示例
asyncio.run(async_example())
```

---

## 6. JavaScript示例

### 6.1 使用Fetch API

```javascript
const BASE_URL = 'http://localhost:8000';

// 1. 创建订单
async function createOrder() {
    const response = await fetch(`${BASE_URL}/api/orders`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            order_no: '7777777777777777777',
            product_name: '测试产品JS',
            purchase_amount: 1500.00,
            order_date: '2025-10-31',
            order_status: '已付款',
            payment_method: '已付款'
        })
    });

    const data = await response.json();
    console.log('创建订单:', data);
}

// 2. 获取订单列表
async function getOrders() {
    const params = new URLSearchParams({
        page: 1,
        size: 10,
        product_name: '高铸胶'
    });

    const response = await fetch(`${BASE_URL}/api/orders?${params}`);
    const data = await response.json();
    console.log('订单列表:', data);
}

// 3. 获取Dashboard统计
async function getDashboard() {
    const response = await fetch(`${BASE_URL}/api/statistics/dashboard`);
    const data = await response.json();

    console.log(`总采购金额: ¥${data.total_amount.toFixed(2)}`);
    console.log(`总订单数: ${data.total_orders}`);
    console.log(`本月采购: ¥${data.this_month_amount.toFixed(2)}`);

    console.log('TOP 5产品:');
    data.top_products.forEach(product => {
        console.log(`  ${product.product_name}: ¥${product.total_amount.toFixed(2)} (${product.percentage}%)`);
    });
}

// 执行示例
createOrder();
getOrders();
getDashboard();
```

### 6.2 使用Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// 创建axios实例
const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 1. 创建订单
async function createOrder() {
    try {
        const response = await api.post('/api/orders', {
            order_no: '6666666666666666666',
            product_name: '测试产品Axios',
            purchase_amount: 1800.00,
            order_date: '2025-10-31',
            order_status: '已付款',
            payment_method: '已付款'
        });
        console.log('创建订单成功:', response.data);
    } catch (error) {
        console.error('创建订单失败:', error.response?.data || error.message);
    }
}

// 2. 获取订单列表
async function getOrders(filters = {}) {
    try {
        const response = await api.get('/api/orders', {
            params: {
                page: 1,
                size: 10,
                ...filters
            }
        });
        console.log(`共${response.data.total}条订单`);
        return response.data;
    } catch (error) {
        console.error('获取订单失败:', error.response?.data || error.message);
    }
}

// 3. 批量操作示例
async function batchOperations() {
    try {
        // 并发请求
        const [orders, products, dashboard] = await Promise.all([
            api.get('/api/orders?page=1&size=10'),
            api.get('/api/products'),
            api.get('/api/statistics/dashboard')
        ]);

        console.log('订单总数:', orders.data.total);
        console.log('产品总数:', products.data.total);
        console.log('采购总额:', dashboard.data.total_amount);
    } catch (error) {
        console.error('批量操作失败:', error.response?.data || error.message);
    }
}

// 执行示例
createOrder();
getOrders({ product_name: '高铸胶' });
batchOperations();
```

---

## 7. 错误处理

### 7.1 常见错误码

| 状态码 | 说明 | 处理方式 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应 |
| 201 | 创建成功 | 资源已创建 |
| 400 | 请求错误 | 检查请求参数 |
| 404 | 资源不存在 | 检查资源ID |
| 422 | 验证错误 | 检查数据格式 |
| 500 | 服务器错误 | 联系管理员 |

### 7.2 错误响应示例

```json
{
    "detail": "订单编号 3655240347686198464 已存在"
}
```

### 7.3 Python错误处理

```python
import requests

def create_order_with_error_handling():
    try:
        response = requests.post(
            "http://localhost:8000/api/orders",
            json={...},
            timeout=10
        )
        response.raise_for_status()  # 抛出HTTP错误
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"请求错误: {e.response.json()['detail']}")
        elif e.response.status_code == 404:
            print("资源不存在")
        else:
            print(f"HTTP错误: {e}")

    except requests.exceptions.Timeout:
        print("请求超时")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
```

---

## 8. 性能优化建议

### 8.1 分页查询

```python
# 推荐：使用分页
response = requests.get(
    "http://localhost:8000/api/orders",
    params={"page": 1, "size": 20}
)

# 不推荐：查询所有数据
response = requests.get(
    "http://localhost:8000/api/orders",
    params={"size": 10000}  # 过大的size会影响性能
)
```

### 8.2 使用筛选减少数据量

```python
# 推荐：使用筛选条件
response = requests.get(
    "http://localhost:8000/api/orders",
    params={
        "product_name": "高铸胶",
        "start_date": "2025-10-01",
        "end_date": "2025-10-31"
    }
)
```

### 8.3 并发请求

```python
import asyncio
import httpx

async def fetch_multiple_data():
    async with httpx.AsyncClient() as client:
        # 并发请求多个API
        tasks = [
            client.get("http://localhost:8000/api/orders"),
            client.get("http://localhost:8000/api/products"),
            client.get("http://localhost:8000/api/statistics/dashboard"),
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

---

## 9. 测试工具

### 9.1 使用Postman

1. 导入API collection
2. 设置环境变量: `BASE_URL=http://localhost:8000`
3. 运行测试集合

### 9.2 使用HTTPie

```bash
# 安装
pip install httpie

# 使用示例
http GET http://localhost:8000/api/orders page==1 size==10
http POST http://localhost:8000/api/orders order_no=9999999999999999999 product_name="测试产品" purchase_amount:=1000.00 order_date="2025-10-31" order_status="已付款" payment_method="已付款"
```

---

## 10. API文档

访问自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

最后更新: 2025-10-31
