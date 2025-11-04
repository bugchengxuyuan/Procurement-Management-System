"""
先采后付按还款日分组统计服务
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from collections import defaultdict

from ..models import PurchaseOrder
from ..core.config import settings


def get_payment_due_groups(session: Session, include_paid: bool = False) -> List[Dict[str, Any]]:
    """获取先采后付订单按还款日分组统计

    Args:
        session: 数据库会话
        include_paid: 是否包含已付款订单

    Returns:
        按还款日分组的订单统计列表

    业务逻辑：
    1. 按确认收货月份分组（10月确认→11月8日还款，11月确认→12月8日还款）
    2. 动态实时计算，不依赖静态账单文件
    3. 支持过滤已付款/未付款订单
    """

    # 查询先采后付订单（新状态系统：账期未到 + 账期已结）
    if include_paid:
        # 包含已付款：查询"账期未到"和"账期已结"
        try:
            query = select(PurchaseOrder).where(
                PurchaseOrder.payment_status.in_(["账期未到", "账期已结"])
            )
        except Exception:
            # 向后兼容：如果新状态不存在，使用旧查询
            query = select(PurchaseOrder).where(
                PurchaseOrder.payment_method == "先采后付"
            )
    else:
        # 只查询未付款：只查询"账期未到"
        try:
            query = select(PurchaseOrder).where(
                PurchaseOrder.payment_status == "账期未到"
            )
        except Exception:
            # 向后兼容
            query = select(PurchaseOrder).where(
                PurchaseOrder.payment_method == "先采后付",
                PurchaseOrder.payment_status == "unpaid"
            )

    orders = session.exec(query).all()

    # 按还款日分组
    payment_groups = defaultdict(list)

    for order in orders:
        # 1688规则：只有确认收货的订单才进入账期
        # 必须有 receive_date，不能用 order_date 代替
        try:
            if not hasattr(order, 'receive_date') or not order.receive_date:
                # 跳过没有确认收货时间的订单
                continue

            base_date = order.receive_date
        except AttributeError:
            # 如果字段不存在，跳过
            continue

        # 计算还款日（次月8号）
        next_month = base_date + relativedelta(months=1)
        due_date = date(next_month.year, next_month.month, settings.PAYMENT_DUE_DAY)

        payment_groups[due_date].append(order)

    # 构建结果
    today = date.today()
    result = []

    for due_date in sorted(payment_groups.keys()):
        orders_in_group = payment_groups[due_date]

        # 统计金额
        total_amount = sum(float(o.purchase_amount) for o in orders_in_group)

        # 统计付款状态（新状态系统）
        unpaid_orders = []  # 账期未到
        paid_orders = []    # 账期已结

        for order in orders_in_group:
            payment_status = getattr(order, 'payment_status', None)
            # 新状态系统
            if payment_status == '账期已结':
                paid_orders.append(order)
            elif payment_status == '账期未到':
                unpaid_orders.append(order)
            # 向后兼容旧状态
            elif payment_status == 'paid':
                paid_orders.append(order)
            else:
                unpaid_orders.append(order)

        unpaid_amount = sum(float(o.purchase_amount) for o in unpaid_orders)
        paid_amount = sum(float(o.purchase_amount) for o in paid_orders)

        # 计算剩余天数和状态
        days_remaining = (due_date - today).days

        if days_remaining < 0:
            status = "overdue"
            status_text = f"已逾期 {abs(days_remaining)} 天"
        elif days_remaining <= settings.WARNING_DAYS:
            status = "warning"
            status_text = f"即将到期（{days_remaining}天后）"
        else:
            status = "normal"
            status_text = f"{days_remaining}天后"

        # 确定确认收货月份范围
        receive_dates = []
        for order in orders_in_group:
            try:
                if hasattr(order, 'receive_date') and order.receive_date:
                    receive_dates.append(order.receive_date)
                else:
                    receive_dates.append(order.order_date)
            except AttributeError:
                receive_dates.append(order.order_date)

        receive_month_start = min(receive_dates) if receive_dates else None
        receive_month_end = max(receive_dates) if receive_dates else None

        # 判断账单完整性
        # 关键业务规则：只有当前月份确认收货的订单账单可能不完整
        # 例如：今天11月4日
        #   - 11月8日账单（10月确认收货）：10月已结束 → 完整 ✅
        #   - 12月8日账单（11月确认收货）：11月进行中 → 不完整 ⚠️
        is_current_month = False
        is_incomplete = False

        if receive_month_start:
            # 获取确认收货月份（以最早确认收货日期为准）
            receive_month = receive_month_start.replace(day=1)  # 确认收货月份的第一天
            current_month = today.replace(day=1)                # 当前月份的第一天

            # 检查是否是当月确认收货
            if receive_month == current_month:
                is_current_month = True
                # 当月账单：如果月份还没结束，账单肯定不完整
                # 保守估计：28号之前都可能有新订单加入
                if today.day < 28:
                    is_incomplete = True
            else:
                # 过去月份的账单：都是完整的（月份已结束）
                is_current_month = False
                is_incomplete = False

        result.append({
            "due_date": due_date,
            "days_remaining": days_remaining,
            "status": status,
            "status_text": status_text,
            "total_count": len(orders_in_group),
            "total_amount": total_amount,
            "unpaid_count": len(unpaid_orders),
            "unpaid_amount": unpaid_amount,
            "paid_count": len(paid_orders),
            "paid_amount": paid_amount,
            "receive_month_start": receive_month_start,
            "receive_month_end": receive_month_end,
            "is_current_month": is_current_month,
            "is_incomplete": is_incomplete,
            "order_ids": [o.id for o in orders_in_group],
        })

    return result


def get_payment_due_group_detail(
    session: Session,
    due_date: date,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """获取指定还款日的订单详情

    Args:
        session: 数据库会话
        due_date: 还款日期
        page: 页码
        page_size: 每页数量

    Returns:
        订单详情列表和分页信息
    """

    # 查询先采后付订单（新状态系统：账期未到 + 账期已结）
    try:
        query = select(PurchaseOrder).where(
            PurchaseOrder.payment_status.in_(["账期未到", "账期已结"])
        )
    except Exception:
        # 向后兼容
        query = select(PurchaseOrder).where(
            PurchaseOrder.payment_method == "先采后付"
        )

    orders = session.exec(query).all()

    # 筛选属于指定还款日的订单
    matching_orders = []

    for order in orders:
        # 1688规则：只有确认收货的订单才进入账期
        try:
            if not hasattr(order, 'receive_date') or not order.receive_date:
                # 跳过没有确认收货时间的订单
                continue

            base_date = order.receive_date
        except AttributeError:
            # 如果字段不存在，跳过
            continue

        # 计算还款日
        next_month = base_date + relativedelta(months=1)
        order_due_date = date(next_month.year, next_month.month, settings.PAYMENT_DUE_DAY)

        if order_due_date == due_date:
            matching_orders.append(order)

    # 排序：未付款优先，然后按日期倒序
    matching_orders.sort(
        key=lambda o: (
            getattr(o, 'payment_status', 'unpaid') == 'paid',  # 未付款在前
            -(getattr(o, 'receive_date', o.order_date) or o.order_date).toordinal()  # 日期倒序
        )
    )

    # 分页
    total = len(matching_orders)
    start = (page - 1) * page_size
    end = start + page_size
    page_orders = matching_orders[start:end]

    # 构建结果
    items = []
    for order in page_orders:
        item = {
            "id": order.id,
            "order_no": order.order_no,
            "product_name": order.product_name,
            "supplier": order.supplier,
            "purchase_amount": float(order.purchase_amount),
            "order_date": order.order_date,
        }

        # 添加可选字段
        if hasattr(order, 'receive_date'):
            item["receive_date"] = order.receive_date
        if hasattr(order, 'payment_status'):
            item["payment_status"] = order.payment_status
        if hasattr(order, 'spec'):
            item["spec"] = order.spec

        items.append(item)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
        "due_date": due_date,
    }


def mark_payment_due_group_as_paid(
    session: Session,
    due_date: date
) -> Dict[str, Any]:
    """将指定还款日的所有未付款订单标记为已付款（账期已结）

    Args:
        session: 数据库会话
        due_date: 还款日期

    Returns:
        更新结果统计
    """

    # 查询"账期未到"的订单（新状态系统）
    try:
        query = select(PurchaseOrder).where(
            PurchaseOrder.payment_status == "账期未到"
        )
    except Exception:
        # 向后兼容
        query = select(PurchaseOrder).where(
            PurchaseOrder.payment_method == "先采后付",
            PurchaseOrder.payment_status == "unpaid"
        )

    orders = session.exec(query).all()

    # 筛选属于指定还款日的订单
    updated_count = 0
    updated_amount = 0.0

    for order in orders:
        # 1688规则：只有确认收货的订单才进入账期
        try:
            if not hasattr(order, 'receive_date') or not order.receive_date:
                # 跳过没有确认收货时间的订单
                continue

            base_date = order.receive_date
        except AttributeError:
            # 如果字段不存在，跳过
            continue

        # 计算还款日
        next_month = base_date + relativedelta(months=1)
        order_due_date = date(next_month.year, next_month.month, settings.PAYMENT_DUE_DAY)

        if order_due_date == due_date:
            # 标记为"账期已结"（新状态系统）
            if hasattr(order, 'payment_status'):
                order.payment_status = '账期已结'
                updated_count += 1
                updated_amount += float(order.purchase_amount)

    session.commit()

    return {
        "due_date": due_date,
        "updated_count": updated_count,
        "updated_amount": updated_amount,
    }
