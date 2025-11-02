"""
Excel采购数据深度分析工具 v2.0
- 识别订单来源（1688、手工录入等）
- 检测一单多品情况
- 区分真实重复和数据错误
- 提供导入建议
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.excel_handler import parse_excel_orders


class OrderAnalyzer:
    """订单分析器"""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.df = None
        self.analysis_results = {}

    def classify_order_source(self, order_no):
        """分类订单来源"""
        order_no_str = str(order_no).strip()

        if order_no_str in ['#', 'nan', ''] or pd.isna(order_no):
            return 'manual_no_number'  # 手工订单-无订单号
        elif '#' in order_no_str:
            return 'manual_with_hash'  # 手工订单-带#号
        elif order_no_str.isdigit() and len(order_no_str) == 19:
            return '1688'              # 1688订单（19位纯数字）
        elif order_no_str.isdigit():
            return 'other_platform'    # 其他平台订单
        else:
            return 'unknown'           # 未知格式

    def detect_multi_item_order(self, records):
        """检测是否为一单多品"""
        if len(records) == 1:
            return False, None

        # 检查日期
        unique_dates = records['日期'].unique()
        same_date = len(unique_dates) == 1

        # 检查产品
        unique_products = records['产品名称'].unique()
        different_products = len(unique_products) > 1

        # 检查金额
        unique_amounts = records['采购金额'].unique()

        # 判断类型
        if same_date and different_products:
            return True, 'multi_item_same_day'  # 同一天，多个产品 → 真正的一单多品
        elif same_date and not different_products:
            return True, 'duplicate_entry'      # 同一天，同产品 → 重复录入
        elif not same_date and different_products:
            return True, 'multi_item_diff_day'  # 不同天，多个产品 → 可能是分批发货
        else:
            return True, 'data_error'           # 不同天，同产品 → 数据错误

    def analyze_excel_file(self):
        """完整分析Excel文件"""
        print("=" * 80)
        print("采购数据深度分析报告")
        print("=" * 80)
        print(f"\n文件: {self.excel_path}")
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 读取数据 - 使用与parse_excel_orders相同的方式
        with open(self.excel_path, "rb") as f:
            file_content = f.read()

        xl = pd.ExcelFile(BytesIO(file_content))
        sheet_names = xl.sheet_names
        sheet_name = "CAISHENDAO" if "CAISHENDAO" in sheet_names else sheet_names[0]

        df_raw = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, header=None)
        first_row = df_raw.iloc[0].astype(str).tolist()

        # 检测数据格式并提取数据（与parse_excel_orders保持一致）
        if "日期" in first_row and "产品名称" in first_row:
            # 新格式：数据在列0-6，第一行是表头
            self.df = df_raw.iloc[1:, :7].copy()
            self.df.columns = ["日期", "初始状态", "订单编号", "产品名称", "采购金额", "时间", "先采后付"]
        else:
            # 旧格式：数据在列10-16，从第7行开始
            self.df = df_raw.iloc[7:, 10:17].copy()
            self.df.columns = ["日期", "初始状态", "订单编号", "产品名称", "采购金额", "时间", "先采后付"]

        print(f"\n【基础信息】")
        print("-" * 80)
        print(f"总行数: {len(df_raw)}")
        print(f"数据行数（去除表头）: {len(self.df)}")
        print(f"总列数: {len(self.df.columns)}")
        print(f"列名: {list(self.df.columns)}")

        # 1. 订单来源分析
        self._analyze_order_source()

        # 2. 数据质量分析
        self._analyze_data_quality()

        # 3. 订单重复分析
        self._analyze_order_duplicates()

        # 4. 产品分析
        self._analyze_products()

        # 5. 导入建议
        self._generate_import_suggestions()

    def _analyze_order_source(self):
        """分析订单来源"""
        print(f"\n\n【订单来源分析】")
        print("=" * 80)

        self.df['source_type'] = self.df['订单编号'].apply(self.classify_order_source)
        source_counts = self.df['source_type'].value_counts()

        source_names = {
            '1688': '1688订单（19位纯数字）',
            'manual_no_number': '手工订单（无订单号或仅#）',
            'manual_with_hash': '手工订单（包含#）',
            'other_platform': '其他平台订单（纯数字但非19位）',
            'unknown': '未知格式'
        }

        total = len(self.df)
        for source_type, count in source_counts.items():
            name = source_names.get(source_type, source_type)
            percentage = count / total * 100
            print(f"{name:40s}: {count:4d} 条 ({percentage:5.1f}%)")

        # 显示各来源的样例
        print(f"\n订单号样例:")
        for source_type in source_counts.index[:3]:
            sample = self.df[self.df['source_type'] == source_type]['订单编号'].head(3)
            print(f"\n  {source_names.get(source_type, source_type)}:")
            for i, order_no in enumerate(sample, 1):
                print(f"    {i}. {order_no}")

        self.analysis_results['source_counts'] = source_counts.to_dict()

    def _analyze_data_quality(self):
        """数据质量分析"""
        print(f"\n\n【数据质量分析】")
        print("=" * 80)

        required_fields = ['产品名称', '采购金额', '日期']

        for field in required_fields:
            if field in self.df.columns:
                missing = self.df[field].isna().sum()
                percentage = missing / len(self.df) * 100
                status = "✓" if missing == 0 else "✗"
                print(f"{status} {field:15s}: 缺失 {missing:4d} 条 ({percentage:5.1f}%)")

        # 异常值检测
        print(f"\n异常值检测:")

        # 负数金额
        if '采购金额' in self.df.columns:
            negative = self.df[self.df['采购金额'] < 0]
            if len(negative) > 0:
                print(f"  ⚠ 发现 {len(negative)} 条负金额记录:")
                for idx, row in negative.head(3).iterrows():
                    print(f"     行{idx}: {row['产品名称']} = ¥{row['采购金额']}")

        # 空订单号
        empty_order_no = self.df['订单编号'].isna() | (self.df['订单编号'].astype(str).str.strip() == '')
        if empty_order_no.sum() > 0:
            print(f"  ⚠ 发现 {empty_order_no.sum()} 条空订单号记录")

        self.analysis_results['data_quality'] = {
            'missing_fields': {field: int(self.df[field].isna().sum()) for field in required_fields if field in self.df.columns},
            'negative_amounts': len(negative) if '采购金额' in self.df.columns else 0,
            'empty_order_no': int(empty_order_no.sum())
        }

    def _analyze_order_duplicates(self):
        """订单重复分析（核心功能）"""
        print(f"\n\n【订单重复深度分析】")
        print("=" * 80)

        # 只分析1688订单（手工订单允许重复或无订单号）
        df_1688 = self.df[self.df['source_type'] == '1688'].copy()

        if len(df_1688) == 0:
            print("  没有1688订单数据")
            return

        print(f"\n1688订单统计:")
        print(f"  总订单数: {len(df_1688)}")
        print(f"  唯一订单号: {df_1688['订单编号'].nunique()}")

        # 查找重复
        duplicates = df_1688['订单编号'].value_counts()
        duplicates = duplicates[duplicates > 1]

        if len(duplicates) == 0:
            print(f"  ✓ 没有重复订单号")
            self.analysis_results['duplicates'] = {}
            return

        print(f"  ⚠ 重复订单号: {len(duplicates)} 个")

        # 分类分析
        duplicate_analysis = {
            'multi_item_same_day': [],      # 一单多品（同一天）
            'multi_item_diff_day': [],      # 一单多品（不同天）
            'duplicate_entry': [],          # 重复录入
            'data_error': []                # 数据错误
        }

        print(f"\n重复订单详细分析:")
        print("-" * 80)

        for order_no, count in duplicates.items():
            records = df_1688[df_1688['订单编号'] == order_no]
            is_multi, dup_type = self.detect_multi_item_order(records)

            duplicate_analysis[dup_type].append({
                'order_no': order_no,
                'count': count,
                'records': records
            })

        # 输出分析结果
        type_names = {
            'multi_item_same_day': '✓ 一单多品（同一天下单多个产品）',
            'multi_item_diff_day': '⚠ 一单多品（不同天，可能是分批发货）',
            'duplicate_entry': '✗ 重复录入（需要去重）',
            'data_error': '✗ 数据错误（需要人工核对）'
        }

        for dup_type, name in type_names.items():
            items = duplicate_analysis[dup_type]
            if items:
                print(f"\n{name}: {len(items)} 个订单")

                # 显示前3个样例
                for item in items[:3]:
                    order_no = item['order_no']
                    records = item['records']
                    print(f"\n  订单号: {order_no} (共{item['count']}个明细)")

                    # 显示日期范围
                    dates = records['日期'].unique()
                    if len(dates) == 1:
                        print(f"    日期: {dates[0]}")
                    else:
                        print(f"    日期范围: {min(dates)} ~ {max(dates)}")

                    # 显示产品明细
                    print(f"    明细:")
                    for idx, row in records.iterrows():
                        print(f"      - {row['产品名称']:20s} ¥{row['采购金额']:8.2f}")

        self.analysis_results['duplicates'] = {
            k: len(v) for k, v in duplicate_analysis.items()
        }
        self.duplicate_details = duplicate_analysis

    def _analyze_products(self):
        """产品分析"""
        print(f"\n\n【产品统计分析】")
        print("=" * 80)

        unique_products = self.df['产品名称'].nunique()
        print(f"\n产品种类: {unique_products} 种")

        # TOP产品
        product_counts = self.df['产品名称'].value_counts()
        print(f"\nTOP 10 产品（按订单数）:")
        for i, (product, count) in enumerate(product_counts.head(10).items(), 1):
            print(f"  {i:2d}. {product:25s}: {count:3d} 条订单")

        self.analysis_results['product_count'] = unique_products

    def _generate_import_suggestions(self):
        """生成导入建议"""
        print(f"\n\n【导入建议】")
        print("=" * 80)

        # 使用解析器检查
        with open(self.excel_path, "rb") as f:
            file_content = f.read()

        orders, errors = parse_excel_orders(file_content)

        total_rows = len(self.df)
        valid_orders = len(orders)
        error_count = len(errors)

        # 计算可能被跳过的重复订单
        skip_count = 0
        if 'duplicates' in self.analysis_results:
            # 重复录入需要去重
            skip_count += self.analysis_results['duplicates'].get('duplicate_entry', 0)

        estimated_import = valid_orders - skip_count

        print(f"\n导入预估:")
        print(f"  Excel总行数: {total_rows}")
        print(f"  有效数据: {valid_orders} 条")
        print(f"  解析失败: {error_count} 条")
        if skip_count > 0:
            print(f"  建议去重: {skip_count} 条（重复录入）")
        print(f"  预计成功导入: {estimated_import} 条")

        print(f"\n导入策略建议:")

        # 1688订单
        if self.analysis_results.get('source_counts', {}).get('1688', 0) > 0:
            print(f"\n  1. 1688订单处理:")
            print(f"     - 一单多品（同一天）: 作为一个订单的多个明细导入 ✓")
            print(f"     - 一单多品（不同天）: 需要人工确认是否为分批发货 ⚠")
            print(f"     - 重复录入: 自动去重，只保留第一条 ✓")
            print(f"     - 数据错误: 标记为待审核，需要人工处理 ⚠")

        # 手工订单
        manual_count = (
            self.analysis_results.get('source_counts', {}).get('manual_no_number', 0) +
            self.analysis_results.get('source_counts', {}).get('manual_with_hash', 0)
        )
        if manual_count > 0:
            print(f"\n  2. 手工订单处理:")
            print(f"     - 无订单号或带#: 自动生成19位订单号 ✓")
            print(f"     - 允许重复: 每条都作为独立订单导入 ✓")

        # 数据质量问题
        if error_count > 0:
            print(f"\n  3. 数据质量问题:")
            print(f"     - 必填字段缺失: {error_count} 条")
            print(f"     - 建议: 修复Excel后重新导入 ⚠")

        print(f"\n\n建议操作流程:")
        print(f"  步骤1: 修复数据质量问题（必填字段缺失、负金额等）")
        print(f"  步骤2: 运行导入预览，查看重复订单处理结果")
        print(f"  步骤3: 人工确认'不同天一单多品'和'数据错误'的订单")
        print(f"  步骤4: 执行批量导入")

        # 生成错误报告
        if error_count > 0:
            self._generate_error_report(errors)

    def _generate_error_report(self, errors):
        """生成错误报告"""
        print(f"\n\n【错误详情报告】")
        print("=" * 80)

        # 按错误类型分组
        error_by_type = defaultdict(list)
        for error in errors:
            error_by_type[error['error']].append(error)

        for error_type, error_list in error_by_type.items():
            print(f"\n{error_type}: {len(error_list)} 条")
            for error in error_list[:5]:
                row_idx = error['row']
                if row_idx in self.df.index:
                    row = self.df.loc[row_idx]
                    print(f"  行{row_idx}: 订单号={row.get('订单编号', 'N/A')}, "
                          f"产品={row.get('产品名称', 'N/A')}, "
                          f"金额={row.get('采购金额', 'N/A')}")

            if len(error_list) > 5:
                print(f"  ... 还有 {len(error_list) - 5} 条")


def main():
    """主函数"""
    excel_file = "../采购表-2（最新版.xlsx"

    if not os.path.exists(excel_file):
        print(f"错误: 找不到文件 {excel_file}")
        return

    analyzer = OrderAnalyzer(excel_file)
    analyzer.analyze_excel_file()

    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
