"""
先采后付按还款日分组API
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from datetime import date as date_type
from typing import Optional

from ..core.database import get_session
from ..services import payment_due_service
from ..services.bill_import_service import BillImportService

router = APIRouter(prefix="/payment-due", tags=["先采后付管理"])


@router.get("/groups")
def get_payment_due_groups(
    include_paid: bool = Query(False, description="是否包含已付款订单"),
    session: Session = Depends(get_session)
):
    """获取先采后付订单按还款日分组统计

    返回格式：
    [
        {
            "due_date": "2025-11-08",
            "days_remaining": 4,
            "status": "warning",  // overdue/warning/normal
            "status_text": "即将到期（4天后）",
            "total_count": 40,
            "total_amount": 26329.93,
            "unpaid_count": 30,
            "unpaid_amount": 7578.05,
            "paid_count": 10,
            "paid_amount": 18751.88,
            "receive_month_start": "2025-10-02",
            "receive_month_end": "2025-10-31",
            "is_current_month": false,
            "is_incomplete": false,
            "order_ids": [1, 2, 3, ...]
        },
        ...
    ]

    字段说明：
    - is_current_month: 是否包含当月确认收货的订单
    - is_incomplete: 账单是否可能不完整（当月未结束）
    """
    return payment_due_service.get_payment_due_groups(session, include_paid)


@router.get("/groups/{due_date}/detail")
def get_payment_due_group_detail(
    due_date: date_type,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    session: Session = Depends(get_session)
):
    """获取指定还款日的订单详情列表

    Args:
        due_date: 还款日期，格式：YYYY-MM-DD，例如 2025-11-08
        page: 页码
        page_size: 每页数量

    Returns:
        订单详情列表和分页信息
    """
    return payment_due_service.get_payment_due_group_detail(
        session, due_date, page, page_size
    )


@router.post("/groups/{due_date}/mark-paid")
def mark_payment_due_group_as_paid(
    due_date: date_type,
    session: Session = Depends(get_session)
):
    """将指定还款日的所有未付款订单标记为已付款

    Args:
        due_date: 还款日期，格式：YYYY-MM-DD，例如 2025-11-08

    Returns:
        更新结果统计
        {
            "due_date": "2025-11-08",
            "updated_count": 30,
            "updated_amount": 7578.05
        }

    使用场景：
    - 完成还款后，批量标记该还款日的所有订单为已付款
    - 避免逐个订单手动标记
    """
    return payment_due_service.mark_payment_due_group_as_paid(session, due_date)


@router.post("/import-bill")
async def import_payment_bill(
    file: UploadFile = File(..., description="1688账单Excel文件"),
    paid_date: date_type = Form(..., description="实际付款日期，格式：YYYY-MM-DD"),
    session: Session = Depends(get_session)
):
    """导入1688账单Excel并批量更新订单状态为"账期已结"

    Args:
        file: 1688账单Excel文件（必须包含"订单编号"列）
        paid_date: 实际付款日期（例如：2025-11-08）

    Returns:
        导入结果统计
        {
            "success_count": 30,         // 成功更新的订单数
            "failed_count": 0,           // 失败的订单数
            "not_found_count": 2,        // 未找到的订单数
            "already_paid_count": 5,     // 已付款的订单数
            "success_orders": ["..."],   // 成功更新的订单号列表
            "not_found_orders": ["..."], // 未找到的订单号列表
            "already_paid_orders": ["..."],  // 已付款的订单号列表
            "errors": [],                // 错误详情
            "paid_date": "2025-11-08",   // 付款日期
            "import_time": "2025-11-08T14:30:00",  // 导入时间
            "total_amount": 7578.05      // 总付款金额
        }

    业务流程：
    1. 从1688下载月度账单Excel
    2. 上传并指定实际付款日期
    3. 系统自动解析订单号
    4. 批量更新为"账期已结"
    5. 记录付款日期和导入时间

    注意事项：
    - Excel文件必须包含"订单编号"列（或"订单号"、"order_no"等）
    - 只能更新状态为"账期未到"的订单
    - 已付款订单会被跳过
    - 未找到的订单号会在结果中列出
    """
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="文件格式不正确，请上传Excel文件（.xlsx 或 .xls）"
        )

    try:
        # 读取文件内容
        file_content = await file.read()

        # 调用导入服务
        result = BillImportService.import_payment_bill(
            session=session,
            file_content=file_content,
            paid_date=paid_date
        )

        return result.to_dict()

    except ValueError as e:
        # Excel解析错误
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
