"""
Import/Export API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from io import BytesIO

from database import get_db
from utils.excel import read_excel_file, parse_order_data, export_orders_to_excel
from services.order_service import OrderService
from schemas.order import OrderCreate

router = APIRouter(prefix="/api", tags=["import_export"])


@router.post("/import/excel")
async def import_excel(
    file: UploadFile = File(..., description="Excel文件"),
    db: Session = Depends(get_db),
):
    """
    从Excel导入订单数据

    Expected Excel columns:
    - 日期
    - 订单编号
    - 产品名称
    - 采购金额
    - 初始状态
    - 先采后付
    - 时间 (optional)
    """
    try:
        # Check file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")

        # Read file content
        content = await file.read()

        # Read Excel
        df = read_excel_file(content, sheet_name="sheet")

        # Parse data
        orders, errors = parse_order_data(df)

        # Import orders
        success_count = 0
        import_errors = errors.copy()

        for order_data in orders:
            try:
                # Create OrderCreate schema
                order_create = OrderCreate(**order_data)

                # Check if order already exists
                existing_order = OrderService.get_order_by_order_no(db, order_create.order_no)

                if existing_order:
                    import_errors.append({
                        "order_no": order_create.order_no,
                        "error": "订单编号已存在",
                    })
                    continue

                # Create order
                OrderService.create_order(db, order_create)
                success_count += 1

            except Exception as e:
                import_errors.append({
                    "order_no": order_data.get("order_no", "Unknown"),
                    "error": str(e),
                })

        return {
            "total_rows": len(orders) + len(errors),
            "success_count": success_count,
            "error_count": len(import_errors),
            "errors": import_errors,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/export/excel")
def export_excel(
    product_name: Optional[str] = Query(None, description="产品名称"),
    order_status: Optional[str] = Query(None, description="订单状态"),
    payment_method: Optional[str] = Query(None, description="支付方式"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    导出订单数据到Excel
    """
    try:
        # Get orders based on filters
        result = OrderService.get_orders(
            db,
            page=1,
            size=10000,  # Export all matching records
            product_name=product_name,
            order_status=order_status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
        )

        # Convert to dict list
        orders = [order.to_dict() for order in result["items"]]

        # Export to Excel
        excel_content = export_orders_to_excel(orders)

        # Return as download
        return StreamingResponse(
            BytesIO(excel_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=orders_export.xlsx"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
