"""
Excel导入导出API
"""
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from io import BytesIO
from ..core.database import get_session
from ..models import PurchaseOrderCreate
from ..services import order_service
from ..utils.excel_handler import parse_excel_orders, export_orders_to_excel

router = APIRouter()


@router.post("/import")
async def import_orders(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """导入Excel订单"""
    # 读取文件内容
    content = await file.read()

    # 解析订单数据
    orders, errors = parse_excel_orders(content)

    # 导入订单
    success_count = 0
    error_count = len(errors)
    import_errors = []

    for order_data in orders:
        try:
            order = PurchaseOrderCreate(**order_data)
            order_service.create_order(session, order)
            success_count += 1
        except Exception as e:
            error_count += 1
            import_errors.append({
                "order_no": order_data.get("order_no"),
                "error": str(e),
            })

    return {
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors[:10] + import_errors[:10],  # 只返回前10条错误
    }


@router.get("/export")
def export_orders(session: Session = Depends(get_session)):
    """导出订单到Excel"""
    # 获取所有订单
    result = order_service.get_orders(session, page=1, page_size=10000)
    orders = result["items"]

    # 生成Excel
    excel_content = export_orders_to_excel(orders)

    # 返回文件
    return StreamingResponse(
        BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=orders.xlsx"},
    )
