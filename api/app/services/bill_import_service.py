"""
1688账单导入服务
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional, BinaryIO
from sqlmodel import Session, select
import pandas as pd
from io import BytesIO

from ..models import PurchaseOrder


class BillImportResult:
    """账单导入结果"""
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.not_found_count = 0
        self.already_paid_count = 0

        self.success_orders: List[str] = []
        self.not_found_orders: List[str] = []
        self.already_paid_orders: List[str] = []
        self.errors: List[Dict[str, str]] = []

        self.paid_date: Optional[date] = None
        self.import_time: datetime = datetime.now()
        self.total_amount = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "not_found_count": self.not_found_count,
            "already_paid_count": self.already_paid_count,
            "success_orders": self.success_orders,
            "not_found_orders": self.not_found_orders,
            "already_paid_orders": self.already_paid_orders,
            "errors": self.errors,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
            "import_time": self.import_time.isoformat(),
            "total_amount": round(self.total_amount, 2),
        }


class BillImportService:
    """先采后付账单导入服务"""

    @staticmethod
    def parse_excel(file_content: bytes) -> List[str]:
        """
        解析1688账单Excel文件

        Args:
            file_content: Excel文件内容

        Returns:
            订单号列表

        Raises:
            ValueError: 如果Excel格式不正确
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(BytesIO(file_content))

            # 尝试多种可能的列名
            order_no_columns = ['订单编号', '订单号', 'order_no', 'order_number', '交易编号']

            order_no_column = None
            for col_name in order_no_columns:
                if col_name in df.columns:
                    order_no_column = col_name
                    break

            if not order_no_column:
                raise ValueError(
                    f"Excel文件缺少订单编号列。"
                    f"请确保文件包含以下任一列名: {', '.join(order_no_columns)}"
                )

            # 提取订单号并去重
            order_nos = df[order_no_column].astype(str).str.strip().tolist()

            # 过滤空值
            order_nos = [no for no in order_nos if no and no != 'nan']

            if not order_nos:
                raise ValueError("Excel文件中没有找到有效的订单编号")

            return order_nos

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Excel文件解析失败: {str(e)}")

    @staticmethod
    def import_payment_bill(
        session: Session,
        file_content: bytes,
        paid_date: date
    ) -> BillImportResult:
        """
        导入1688账单并批量更新订单状态

        Args:
            session: 数据库会话
            file_content: Excel文件内容
            paid_date: 实际付款日期

        Returns:
            导入结果统计

        业务流程：
        1. 解析Excel文件，提取订单号列表
        2. 在数据库中查找匹配的订单
        3. 验证订单当前状态（必须是"账期未到"）
        4. 批量更新为"账期已结"
        5. 记录付款日期和导入时间
        6. 返回导入结果统计
        """
        result = BillImportResult()
        result.paid_date = paid_date

        try:
            # 1. 解析Excel文件
            order_nos = BillImportService.parse_excel(file_content)

            print(f"📄 从Excel中解析到 {len(order_nos)} 个订单号")

            # 2. 查找所有先采后付订单（只查询"账期未到"和"账期已结"）
            statement = select(PurchaseOrder).where(
                PurchaseOrder.order_no.in_(order_nos)
            )
            found_orders = session.exec(statement).all()

            # 创建订单号到订单对象的映射
            order_map = {o.order_no: o for o in found_orders}

            print(f"🔍 在数据库中找到 {len(found_orders)} 个订单")

            # 3. 逐个处理订单
            for order_no in order_nos:
                order = order_map.get(order_no)

                # 订单不存在
                if not order:
                    result.not_found_count += 1
                    result.not_found_orders.append(order_no)
                    continue

                # 检查当前付款状态
                payment_status = getattr(order, 'payment_status', None)

                # 已经付款的订单
                if payment_status == '账期已结':
                    result.already_paid_count += 1
                    result.already_paid_orders.append(order_no)
                    continue

                # 不是先采后付订单
                if payment_status not in ['账期未到', None]:
                    # 可能是"即时付款"订单
                    if payment_status == '即时付款':
                        result.already_paid_count += 1
                        result.already_paid_orders.append(order_no)
                        result.errors.append({
                            "order_no": order_no,
                            "error": "此订单为即时付款订单，不需要账期结算"
                        })
                        continue

                # 必须是"账期未到"才能导入
                if payment_status != '账期未到':
                    # 向后兼容：检查旧字段
                    if hasattr(order, 'payment_method') and order.payment_method != '先采后付':
                        result.errors.append({
                            "order_no": order_no,
                            "error": f"订单状态不正确：{payment_status}，应为'账期未到'"
                        })
                        result.failed_count += 1
                        continue

                # 4. 更新订单状态
                try:
                    order.payment_status = '账期已结'
                    order.paid_date = paid_date
                    order.bill_import_time = result.import_time
                    order.updated_at = result.import_time

                    result.success_count += 1
                    result.success_orders.append(order_no)
                    result.total_amount += float(order.purchase_amount)

                except Exception as e:
                    result.failed_count += 1
                    result.errors.append({
                        "order_no": order_no,
                        "error": f"更新失败: {str(e)}"
                    })

            # 5. 提交更改
            session.commit()

            print(f"✅ 成功更新 {result.success_count} 个订单")
            print(f"❌ 失败: {result.failed_count} 个")
            print(f"⚠️  未找到: {result.not_found_count} 个")
            print(f"ℹ️  已付款: {result.already_paid_count} 个")

            return result

        except Exception as e:
            session.rollback()
            raise Exception(f"账单导入失败: {str(e)}")

    @staticmethod
    def validate_bill_orders(
        session: Session,
        order_nos: List[str]
    ) -> Dict[str, Any]:
        """
        验证账单中的订单

        Args:
            session: 数据库会话
            order_nos: 订单号列表

        Returns:
            验证结果统计
        """
        # 查找订单
        statement = select(PurchaseOrder).where(
            PurchaseOrder.order_no.in_(order_nos)
        )
        found_orders = session.exec(statement).all()

        # 统计
        found_nos = {o.order_no for o in found_orders}
        not_found_nos = [no for no in order_nos if no not in found_nos]

        # 检查状态
        can_import = []
        already_paid = []
        wrong_status = []

        for order in found_orders:
            payment_status = getattr(order, 'payment_status', None)

            if payment_status == '账期未到':
                can_import.append(order.order_no)
            elif payment_status == '账期已结':
                already_paid.append(order.order_no)
            else:
                wrong_status.append(order.order_no)

        return {
            "total": len(order_nos),
            "found": len(found_nos),
            "not_found": not_found_nos,
            "can_import": can_import,
            "already_paid": already_paid,
            "wrong_status": wrong_status,
        }

    @staticmethod
    def mark_orders_as_paid(
        session: Session,
        order_nos: List[str],
        paid_date: date
    ) -> Dict[str, Any]:
        """
        批量标记订单为已付款（不需要Excel，直接标记）

        Args:
            session: 数据库会话
            order_nos: 订单号列表
            paid_date: 付款日期

        Returns:
            更新结果统计
        """
        # 查找订单
        statement = select(PurchaseOrder).where(
            PurchaseOrder.order_no.in_(order_nos),
            PurchaseOrder.payment_status == '账期未到'
        )
        orders = session.exec(statement).all()

        updated_count = 0
        total_amount = 0.0

        import_time = datetime.now()

        for order in orders:
            order.payment_status = '账期已结'
            order.paid_date = paid_date
            order.bill_import_time = import_time
            order.updated_at = import_time

            updated_count += 1
            total_amount += float(order.purchase_amount)

        session.commit()

        return {
            "updated_count": updated_count,
            "updated_amount": round(total_amount, 2),
            "paid_date": paid_date.isoformat(),
            "import_time": import_time.isoformat(),
        }
