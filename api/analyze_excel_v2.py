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

        # 检查规格（同一产品不同规格也算不同明细）
        if '规格' in records.columns:
            unique_specs = records['规格'].dropna().unique()
            different_specs = len(unique_specs) > 1
        else:
            different_specs = False

        # 检查金额
        unique_amounts = records['采购金额'].unique()

        # 判断类型
        if same_date and (different_products or different_specs):
            return True, 'multi_item_same_day'  # 同一天，多个产品或规格 → 真正的一单多品
        elif same_date and not different_products and not different_specs:
            return True, 'duplicate_entry'      # 同一天，同产品同规格 → 重复录入
        elif not same_date and (different_products or different_specs):
            return True, 'multi_item_diff_day'  # 不同天，多个产品或规格 → 可能是分批发货
        else:
            return True, 'data_error'           # 不同天，同产品同规格 → 数据错误

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
            # 检查是否包含规格和供应商字段（新格式v2）
            if "规格" in first_row and "供应商" in first_row:
                # 新格式v2：包含规格和供应商，9列
                self.df = df_raw.iloc[1:, :9].copy()
                self.df.columns = ["日期", "初始状态", "订单编号", "产品名称", "规格", "采购金额", "供应商", "时间", "先采后付"]
            else:
                # 新格式v1：没有规格和供应商，7列
                self.df = df_raw.iloc[1:, :7].copy()
                self.df.columns = ["日期", "初始状态", "订单编号", "产品名称", "采购金额", "时间", "先采后付"]
                # 添加空列
                self.df["规格"] = None
                self.df["供应商"] = None
        else:
            # 旧格式：数据在列10-16，从第7行开始
            self.df = df_raw.iloc[7:, 10:17].copy()
            self.df.columns = ["日期", "初始状态", "订单编号", "产品名称", "采购金额", "时间", "先采后付"]
            # 添加空列
            self.df["规格"] = None
            self.df["供应商"] = None

        # 数据类型转换
        # 清洗采购金额：去除空格、逗号等常见字符
        def clean_amount(val):
            if pd.isna(val):
                return np.nan
            val_str = str(val).strip()
            # 移除常见的非数字字符（保留小数点和负号）
            val_str = val_str.replace(',', '').replace('，', '').replace(' ', '')
            val_str = val_str.replace('¥', '').replace('￥', '').replace('元', '')
            if val_str == '' or val_str == 'nan':
                return np.nan
            try:
                return float(val_str)
            except (ValueError, AttributeError):
                return np.nan

        self.df['采购金额'] = self.df['采购金额'].apply(clean_amount)
        self.df['日期'] = pd.to_datetime(self.df['日期'], errors='coerce')

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

        # 5. 供应商分析
        self._analyze_suppliers()

        # 6. 规格分析
        self._analyze_specs()

        # 7. 导入建议
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
                        spec_info = f" [{row['规格']}]" if pd.notna(row.get('规格')) else ""
                        supplier_info = f" - {row['供应商']}" if pd.notna(row.get('供应商')) else ""
                        print(f"      - {row['产品名称']:20s}{spec_info:15s} ¥{row['采购金额']:8.2f}{supplier_info}")

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

    def _analyze_suppliers(self):
        """供应商分析"""
        print(f"\n\n【供应商统计分析】")
        print("=" * 80)

        if '供应商' not in self.df.columns or self.df['供应商'].isna().all():
            print("  没有供应商数据")
            return

        # 移除空值
        df_with_supplier = self.df[self.df['供应商'].notna()].copy()

        if len(df_with_supplier) == 0:
            print("  没有供应商数据")
            return

        unique_suppliers = df_with_supplier['供应商'].nunique()
        print(f"\n供应商总数: {unique_suppliers} 个")
        print(f"有供应商信息的订单: {len(df_with_supplier)}/{len(self.df)} 条 ({len(df_with_supplier)/len(self.df)*100:.1f}%)")

        # 按订单数统计TOP供应商
        supplier_counts = df_with_supplier['供应商'].value_counts()
        print(f"\nTOP 10 供应商（按订单数）:")
        for i, (supplier, count) in enumerate(supplier_counts.head(10).items(), 1):
            percentage = count / len(df_with_supplier) * 100
            print(f"  {i:2d}. {supplier:40s}: {count:3d} 条订单 ({percentage:5.1f}%)")

        # 按采购金额统计TOP供应商
        supplier_amounts = df_with_supplier.groupby('供应商')['采购金额'].sum().sort_values(ascending=False)
        total_amount = df_with_supplier['采购金额'].sum()
        print(f"\nTOP 10 供应商（按采购金额）:")
        for i, (supplier, amount) in enumerate(supplier_amounts.head(10).items(), 1):
            percentage = amount / total_amount * 100
            print(f"  {i:2d}. {supplier:40s}: ¥{amount:10,.2f} ({percentage:5.1f}%)")

        # 供应商提供的产品种类
        supplier_products = df_with_supplier.groupby('供应商')['产品名称'].nunique().sort_values(ascending=False)
        print(f"\nTOP 10 供应商（按产品种类）:")
        for i, (supplier, prod_count) in enumerate(supplier_products.head(10).items(), 1):
            print(f"  {i:2d}. {supplier:40s}: {prod_count:3d} 种产品")

        self.analysis_results['supplier_count'] = unique_suppliers

    def _analyze_specs(self):
        """规格分析"""
        print(f"\n\n【规格统计分析】")
        print("=" * 80)

        if '规格' not in self.df.columns or self.df['规格'].isna().all():
            print("  没有规格数据")
            return

        # 移除空值
        df_with_spec = self.df[self.df['规格'].notna()].copy()

        if len(df_with_spec) == 0:
            print("  没有规格数据")
            return

        unique_specs = df_with_spec['规格'].nunique()
        print(f"\n规格总数: {unique_specs} 种")
        print(f"有规格信息的订单: {len(df_with_spec)}/{len(self.df)} 条 ({len(df_with_spec)/len(self.df)*100:.1f}%)")

        # 按订单数统计TOP规格
        spec_counts = df_with_spec['规格'].value_counts()
        print(f"\nTOP 15 规格（按订单数）:")
        for i, (spec, count) in enumerate(spec_counts.head(15).items(), 1):
            percentage = count / len(df_with_spec) * 100
            print(f"  {i:2d}. {spec:25s}: {count:3d} 条订单 ({percentage:5.1f}%)")

        # 产品与规格的关系
        print(f"\n产品规格多样性分析:")
        product_spec_counts = df_with_spec.groupby('产品名称')['规格'].nunique().sort_values(ascending=False)
        products_with_multiple_specs = product_spec_counts[product_spec_counts > 1]

        if len(products_with_multiple_specs) > 0:
            print(f"  有多种规格的产品: {len(products_with_multiple_specs)} 个")
            print(f"\n  TOP 10 多规格产品:")
            for i, (product, spec_count) in enumerate(products_with_multiple_specs.head(10).items(), 1):
                specs = df_with_spec[df_with_spec['产品名称'] == product]['规格'].unique()
                specs_str = ', '.join([str(s) for s in specs[:5]])
                if len(specs) > 5:
                    specs_str += f" ... (共{spec_count}种)"
                print(f"    {i:2d}. {product:25s}: {spec_count} 种规格 ({specs_str})")
        else:
            print(f"  所有产品都只有一种规格")

        self.analysis_results['spec_count'] = unique_specs

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
                # DataFrame索引 = df_raw索引 = Excel行号 - 1
                # 所以 Excel行号 = DataFrame索引 + 1
                excel_row = row_idx + 1
                if row_idx in self.df.index:
                    row = self.df.loc[row_idx]
                    print(f"  Excel行{excel_row}: 订单号={row.get('订单编号', 'N/A')}, "
                          f"产品={row.get('产品名称', 'N/A')}, "
                          f"金额={row.get('采购金额', 'N/A')}")

            if len(error_list) > 5:
                print(f"  ... 还有 {len(error_list) - 5} 条")


def main():
    """主函数"""
    # 获取Excel文件路径
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        # 默认使用项目根目录下的Excel文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        excel_file = os.path.join(project_root, "采购表.xlsx")

    if not os.path.exists(excel_file):
        print(f"错误: 找不到文件 {excel_file}")
        print(f"\n使用方法:")
        print(f"  python3 analyze_excel_v2.py [Excel文件路径]")
        print(f"\n示例:")
        print(f"  python3 analyze_excel_v2.py ../采购表.xlsx")
        return

    analyzer = OrderAnalyzer(excel_file)
    analyzer.analyze_excel_file()

    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
