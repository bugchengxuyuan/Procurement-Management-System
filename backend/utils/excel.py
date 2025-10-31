"""
Excel processing utilities
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO


def read_excel_file(file_content: bytes, sheet_name: str = "sheet") -> pd.DataFrame:
    """
    Read Excel file and return DataFrame

    Args:
        file_content: Excel file content in bytes
        sheet_name: Sheet name to read

    Returns:
        DataFrame with the Excel data
    """
    try:
        df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name)
        return df
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {str(e)}")


def parse_order_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Parse DataFrame into order data list

    Expected columns:
    - 日期 (Date)
    - 订单编号 (Order No)
    - 产品名称 (Product Name)
    - 采购金额 (Purchase Amount)
    - 初始状态 (Order Status)
    - 先采后付 (Payment Method)
    - 时间 (Record Time) - optional

    Args:
        df: DataFrame with order data

    Returns:
        List of order dictionaries
    """
    orders = []
    errors = []

    # Column mapping
    column_mapping = {
        "日期": "order_date",
        "订单编号": "order_no",
        "产品名称": "product_name",
        "采购金额": "purchase_amount",
        "初始状态": "order_status",
        "先采后付": "payment_method",
        "时间": "record_time",
    }

    for idx, row in df.iterrows():
        try:
            # Extract data
            order_data = {}

            # Required fields
            order_data["order_no"] = str(int(row.get("订单编号", ""))).strip() if pd.notna(row.get("订单编号")) else None
            order_data["product_name"] = str(row.get("产品名称", "")).strip() if pd.notna(row.get("产品名称")) else None
            order_data["purchase_amount"] = float(row.get("采购金额", 0)) if pd.notna(row.get("采购金额")) else None

            # Date fields
            order_date = row.get("日期")
            if pd.notna(order_date):
                if isinstance(order_date, str):
                    order_data["order_date"] = pd.to_datetime(order_date).date()
                else:
                    order_data["order_date"] = order_date.date() if hasattr(order_date, 'date') else order_date
            else:
                order_data["order_date"] = None

            # Status fields
            order_data["order_status"] = str(row.get("初始状态", "")).strip() if pd.notna(row.get("初始状态")) else None
            order_data["payment_method"] = str(row.get("先采后付", "")).strip() if pd.notna(row.get("先采后付")) else None

            # Record time (optional)
            record_time = row.get("时间")
            if pd.notna(record_time):
                if isinstance(record_time, str):
                    order_data["record_time"] = pd.to_datetime(record_time)
                else:
                    order_data["record_time"] = record_time
            else:
                # Use order_date as record_time if not provided
                order_data["record_time"] = datetime.combine(order_data["order_date"], datetime.min.time()) if order_data["order_date"] else datetime.now()

            # Validation
            if not order_data["order_no"]:
                errors.append({"row": idx + 2, "error": "订单编号缺失"})
                continue

            if not order_data["product_name"]:
                errors.append({"row": idx + 2, "error": "产品名称缺失"})
                continue

            if order_data["purchase_amount"] is None:
                errors.append({"row": idx + 2, "error": "采购金额缺失"})
                continue

            if not order_data["order_date"]:
                errors.append({"row": idx + 2, "error": "订单日期缺失"})
                continue

            orders.append(order_data)

        except Exception as e:
            errors.append({"row": idx + 2, "error": f"数据解析错误: {str(e)}"})

    return orders, errors


def export_orders_to_excel(orders: List[Dict[str, Any]]) -> bytes:
    """
    Export orders to Excel file

    Args:
        orders: List of order dictionaries

    Returns:
        Excel file content in bytes
    """
    # Convert to DataFrame
    df = pd.DataFrame(orders)

    # Rename columns to Chinese
    column_mapping = {
        "order_date": "日期",
        "order_no": "订单编号",
        "product_name": "产品名称",
        "purchase_amount": "采购金额",
        "order_status": "订单状态",
        "payment_method": "支付方式",
        "record_time": "记录时间",
    }

    # Select and rename columns
    df = df[[col for col in column_mapping.keys() if col in df.columns]]
    df = df.rename(columns=column_mapping)

    # Export to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='订单数据', index=False)

    output.seek(0)
    return output.getvalue()
