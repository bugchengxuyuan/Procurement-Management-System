"""
分析Excel文件，查看哪些数据会被过滤
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.excel_handler import parse_excel_orders


def analyze_excel_file(excel_path: str):
    """分析Excel文件"""
    print("=" * 80)
    print("Excel文件数据分析")
    print("=" * 80)

    # 读取Excel文件
    with open(excel_path, "rb") as f:
        file_content = f.read()

    # 手动读取Excel看看原始数据
    xl = pd.ExcelFile(excel_path)
    sheet_name = xl.sheet_names[0]
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)

    print(f"\n📄 工作表名称: {sheet_name}")
    print(f"📊 总行数: {len(df)} 行")
    print(f"📊 总列数: {len(df.columns)} 列")

    # 检测数据格式
    first_row = df.iloc[0].astype(str).tolist()
    print(f"\n第一行数据: {first_row[:7]}")

    if "日期" in first_row and "产品名称" in first_row:
        print("✅ 检测到新格式（表头在第一行）")
        df_data = df.iloc[1:, :7].copy()
        df_data.columns = ["日期", "初始状态", "订单编号", "产品名称", "采购金额", "时间", "先采后付"]
    else:
        print("✅ 检测到旧格式（数据从第7行开始）")
        df_data = df.iloc[7:, 10:17].copy()
        df_data.columns = ["日期", "初始状态", "订单编号", "产品名称", "采购金额", "时间", "先采后付"]

    print(f"📊 数据行数（去除表头）: {len(df_data)} 行")

    # 使用解析函数
    orders, errors = parse_excel_orders(file_content)

    print("\n" + "=" * 80)
    print("解析结果统计")
    print("=" * 80)
    print(f"✅ 成功解析: {len(orders)} 条")
    print(f"❌ 解析失败: {len(errors)} 条")

    if errors:
        print("\n⚠️  失败原因详情:")
        print("-" * 80)
        error_types = {}
        for error in errors:
            error_msg = error['error']
            error_types[error_msg] = error_types.get(error_msg, 0) + 1

        for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"  • {error_type}: {count} 条")

        print("\n具体失败记录（前10条）:")
        print("-" * 80)
        for i, error in enumerate(errors[:10], 1):
            row_idx = error['row']
            error_msg = error['error']
            # 显示该行的关键数据
            if row_idx in df_data.index:
                row_data = df_data.loc[row_idx]
                print(f"{i}. 行 {row_idx}: {error_msg}")
                print(f"   产品名称: {row_data['产品名称']}")
                print(f"   采购金额: {row_data['采购金额']}")
                print(f"   订单日期: {row_data['日期']}")
                print(f"   订单编号: {row_data['订单编号']}")
                print()

    # 检查数据完整性
    print("\n" + "=" * 80)
    print("数据完整性分析")
    print("=" * 80)

    missing_product = df_data['产品名称'].isna().sum()
    missing_amount = df_data['采购金额'].isna().sum()
    missing_date = df_data['日期'].isna().sum()
    missing_order_no = df_data['订单编号'].isna().sum()

    print(f"产品名称缺失: {missing_product} 条")
    print(f"采购金额缺失: {missing_amount} 条")
    print(f"订单日期缺失: {missing_date} 条")
    print(f"订单编号缺失: {missing_order_no} 条（这个可以自动生成，不影响导入）")

    # 检查订单号重复
    print("\n" + "=" * 80)
    print("订单号重复检查")
    print("=" * 80)

    order_nos = []
    for order in orders:
        order_nos.append(order['order_no'])

    duplicates = pd.Series(order_nos).value_counts()
    duplicates = duplicates[duplicates > 1]

    if len(duplicates) > 0:
        print(f"⚠️  发现 {len(duplicates)} 个重复的订单号")
        print(f"⚠️  重复数据总计: {duplicates.sum() - len(duplicates)} 条")
        print("\n重复订单号详情（前10个）:")
        for order_no, count in list(duplicates.items())[:10]:
            print(f"  • {order_no}: 出现 {count} 次")
    else:
        print("✅ 没有重复的订单号")

    # 总结
    print("\n" + "=" * 80)
    print("数据流向总结")
    print("=" * 80)
    print(f"1. Excel总行数: {len(df)}")
    print(f"2. 去除表头后: {len(df_data)}")
    print(f"3. 解析成功: {len(orders)}")
    print(f"4. 解析失败: {len(errors)}")
    if len(duplicates) > 0:
        print(f"5. 可能被跳过的重复数据: {duplicates.sum() - len(duplicates)}")
        print(f"6. 最终能成功导入的估计: {len(orders) - (duplicates.sum() - len(duplicates))}")
    else:
        print(f"5. 最终能成功导入: {len(orders)}")
    print("=" * 80)


if __name__ == "__main__":
    excel_file = "../采购表-2（最新版.xlsx"
    if not os.path.exists(excel_file):
        print(f"错误: 找不到文件 {excel_file}")
        sys.exit(1)

    analyze_excel_file(excel_file)
