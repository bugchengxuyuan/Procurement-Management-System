"""
数据导入导出API
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
import os
from datetime import datetime
from typing import Optional

from ..database import get_db
from ..models import PurchaseOrder
from ..models.schemas import ImportResponse

router = APIRouter(prefix="/api/import-export", tags=["import-export"])


@router.post("/import", response_model=ImportResponse, summary="导入Excel数据")
async def import_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    从Excel文件导入订单数据

    支持的格式：
    - .xlsx
    - .xls
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")

    try:
        # 读取上传的文件
        contents = await file.read()

        # 读取Excel
        excel_data = pd.ExcelFile(io.BytesIO(contents))

        imported_count = 0
        error_count = 0

        # 处理每个sheet
        for sheet_name in excel_data.sheet_names:
            try:
                df = pd.read_excel(io.BytesIO(contents), sheet_name=sheet_name, skiprows=6)

                # 确定列名（CAISHENDAO和Kitchen maestro可能不同）
                if '先采后付' in df.columns:
                    payment_col = '先采后付'
                elif '采购方式' in df.columns:
                    payment_col = '采购方式'
                else:
                    continue

                order_columns = ['日期', '初始状态', '订单编号', '产品名称', '采购金额', '时间', payment_col]

                # 检查必需的列是否存在
                if not all(col in df.columns for col in order_columns):
                    continue

                orders_df = df[order_columns].copy()
                orders_df = orders_df.dropna(subset=['订单编号', '产品名称'])
                orders_df = orders_df[orders_df['订单编号'].astype(str).str.len() > 10]

                # 清理采购金额
                orders_df['采购金额'] = pd.to_numeric(orders_df['采购金额'], errors='coerce')
                orders_df = orders_df.dropna(subset=['采购金额'])

                # 导入数据
                for idx, row in orders_df.iterrows():
                    try:
                        # 检查订单是否已存在
                        order_no = str(row['订单编号'])
                        existing = db.query(PurchaseOrder).filter(PurchaseOrder.order_no == order_no).first()

                        if existing:
                            # 更新现有订单
                            existing.product_name = str(row['产品名称'])
                            existing.purchase_amount = float(row['采购金额'])
                            existing.order_date = pd.to_datetime(row['日期']) if pd.notna(row['日期']) else None
                            existing.order_time = pd.to_datetime(row['时间']) if pd.notna(row['时间']) else None
                            existing.initial_status = str(row['初始状态']) if pd.notna(row['初始状态']) else None
                            existing.payment_status = str(row[payment_col]) if pd.notna(row[payment_col]) else None
                            existing.shop_name = sheet_name
                        else:
                            # 创建新订单
                            order = PurchaseOrder(
                                order_no=order_no,
                                product_name=str(row['产品名称']),
                                purchase_amount=float(row['采购金额']),
                                order_date=pd.to_datetime(row['日期']) if pd.notna(row['日期']) else None,
                                order_time=pd.to_datetime(row['时间']) if pd.notna(row['时间']) else None,
                                initial_status=str(row['初始状态']) if pd.notna(row['初始状态']) else None,
                                payment_status=str(row[payment_col]) if pd.notna(row[payment_col]) else None,
                                shop_name=sheet_name
                            )
                            db.add(order)

                        imported_count += 1

                        if imported_count % 100 == 0:
                            db.commit()

                    except Exception as e:
                        error_count += 1
                        print(f"导入第{idx}行失败: {e}")
                        continue

            except Exception as e:
                print(f"处理sheet {sheet_name} 失败: {e}")
                continue

        # 提交剩余数据
        db.commit()

        # 统计信息
        total_amount = db.query(func.sum(PurchaseOrder.purchase_amount)).scalar() or 0
        total_products = db.query(PurchaseOrder.product_name).distinct().count()

        return {
            "success": True,
            "message": f"成功导入 {imported_count} 条订单",
            "imported_count": imported_count,
            "error_count": error_count,
            "total_amount": float(total_amount),
            "total_products": total_products
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/export", summary="导出Excel数据")
def export_excel(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    shop_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    导出订单数据为Excel文件

    支持筛选条件：
    - start_date: 开始日期
    - end_date: 结束日期
    - shop_name: 店铺名称
    """
    try:
        # 查询数据
        query = db.query(PurchaseOrder)

        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)
        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)
        if shop_name:
            query = query.filter(PurchaseOrder.shop_name == shop_name)

        orders = query.order_by(PurchaseOrder.order_date.desc()).all()

        # 转换为DataFrame
        data = []
        for order in orders:
            data.append({
                '订单编号': order.order_no,
                '产品名称': order.product_name,
                '采购金额': order.purchase_amount,
                '订单日期': order.order_date.strftime('%Y-%m-%d') if order.order_date else '',
                '订单时间': order.order_time.strftime('%Y-%m-%d %H:%M:%S') if order.order_time else '',
                '初始状态': order.initial_status or '',
                '支付状态': order.payment_status or '',
                '店铺名称': order.shop_name
            })

        df = pd.DataFrame(data)

        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='订单数据')

            # 获取工作簿和工作表
            workbook = writer.book
            worksheet = writer.sheets['订单数据']

            # 设置列宽
            worksheet.set_column('A:A', 25)  # 订单编号
            worksheet.set_column('B:B', 30)  # 产品名称
            worksheet.set_column('C:C', 12)  # 采购金额
            worksheet.set_column('D:E', 20)  # 日期时间
            worksheet.set_column('F:H', 15)  # 状态和店铺

            # 添加汇总信息
            summary_sheet = workbook.add_worksheet('汇总统计')
            bold = workbook.add_format({'bold': True})

            summary_sheet.write('A1', '汇总统计', bold)
            summary_sheet.write('A3', '订单总数:')
            summary_sheet.write('B3', len(orders))
            summary_sheet.write('A4', '采购总额:')
            summary_sheet.write('B4', sum(order.purchase_amount for order in orders))
            summary_sheet.write('A5', '产品种类:')
            summary_sheet.write('B5', len(set(order.product_name for order in orders)))

        output.seek(0)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"采购数据导出_{timestamp}.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
