"""
产品名称匹配测试工具
用于测试1688订单和采购系统产品名称的匹配效果
"""
import pandas as pd
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import re


class ProductMatcher:
    """产品名称智能匹配器"""

    def __init__(self, system_products: List[str]):
        """
        初始化匹配器

        Args:
            system_products: 系统中的产品名称列表
        """
        self.system_products = system_products
        # 为每个产品提取关键词
        self.product_keywords = {}
        for product in system_products:
            keywords = self._extract_keywords(product)
            self.product_keywords[product] = keywords

    def _extract_keywords(self, product_name: str) -> List[str]:
        """提取产品名称中的关键词"""
        # 移除常见的修饰词
        noise_words = ['袋装', '瓶装', '盒装', '包装', '装', '个', '只', '支', '条', '米',
                      '克', 'g', 'ml', '毫升', '厘米', 'cm', '英文', '中文', '白色', '黑色',
                      '透明', '彩色', '大号', '小号', '中号', 'kg', 'mm']

        # 清理并分词
        cleaned = product_name.lower()
        for word in noise_words:
            cleaned = cleaned.replace(word.lower(), ' ')

        # 提取非空词
        keywords = [w.strip() for w in cleaned.split() if w.strip() and len(w.strip()) >= 1]

        # 如果没有关键词，使用原始名称
        if not keywords:
            keywords = [product_name.lower()]

        # 添加原始名称（用于精确匹配）
        keywords.append(product_name.lower())

        return keywords

    def match(self, title_1688: str) -> Dict:
        """
        匹配1688订单标题到系统产品

        Returns:
            {
                'matched': bool,
                'product': str or None,
                'confidence': float (0-1),
                'method': str,  # exact/keyword/fuzzy/none
                'keywords_matched': list
            }
        """
        if pd.isna(title_1688) or not str(title_1688).strip():
            return {
                'matched': False,
                'product': None,
                'confidence': 0,
                'method': 'none',
                'keywords_matched': []
            }

        title_1688 = str(title_1688).strip()
        title_1688_lower = title_1688.lower()

        # 方法1: 精确匹配（系统产品名完整出现在1688标题中）
        for product in self.system_products:
            if product.lower() in title_1688_lower:
                return {
                    'matched': True,
                    'product': product,
                    'confidence': 1.0,
                    'method': 'exact',
                    'keywords_matched': [product]
                }

        # 方法2: 关键词匹配
        best_keyword_match = None
        best_keyword_score = 0

        for product, keywords in self.product_keywords.items():
            matched_keywords = []
            for keyword in keywords:
                if keyword in title_1688_lower:
                    matched_keywords.append(keyword)

            if matched_keywords:
                # 匹配度 = 匹配的关键词数 / 总关键词数
                score = len(matched_keywords) / len(keywords)
                if score > best_keyword_score:
                    best_keyword_score = score
                    best_keyword_match = {
                        'matched': True,
                        'product': product,
                        'confidence': score,
                        'method': 'keyword',
                        'keywords_matched': matched_keywords
                    }

        if best_keyword_match and best_keyword_score >= 0.5:
            return best_keyword_match

        # 方法3: 模糊匹配（相似度计算）
        best_fuzzy_match = None
        best_fuzzy_score = 0

        for product in self.system_products:
            # 计算字符串相似度
            similarity = SequenceMatcher(None, product, title_1688[:len(product)*2]).ratio()
            if similarity > best_fuzzy_score and similarity >= 0.6:
                best_fuzzy_score = similarity
                best_fuzzy_match = {
                    'matched': True,
                    'product': product,
                    'confidence': similarity,
                    'method': 'fuzzy',
                    'keywords_matched': []
                }

        if best_fuzzy_match:
            return best_fuzzy_match

        # 无法匹配
        return {
            'matched': False,
            'product': None,
            'confidence': 0,
            'method': 'none',
            'keywords_matched': []
        }


class MatchingTester:
    """匹配测试器"""

    def __init__(self, file_1688: str, file_system: str):
        """
        初始化测试器

        Args:
            file_1688: 1688订单Excel文件路径
            file_system: 采购表Excel文件路径
        """
        self.file_1688 = file_1688
        self.file_system = file_system

        # 加载数据
        self.df_1688 = None
        self.df_system = None
        self.system_products = []

        self._load_data()

    def _load_data(self):
        """加载两个Excel文件"""
        # 加载1688数据
        self.df_1688 = pd.read_excel(self.file_1688)
        self.df_1688['订单创建时间'] = pd.to_datetime(self.df_1688['订单创建时间'], errors='coerce')

        # 加载系统数据
        with open(self.file_system, "rb") as f:
            content = f.read()
        self.df_system = pd.read_excel(BytesIO(content), sheet_name=0, header=0)
        self.df_system['日期'] = pd.to_datetime(self.df_system['日期'], errors='coerce')

        # 获取系统中的唯一产品列表
        self.system_products = self.df_system['产品名称'].dropna().unique().tolist()

    def filter_by_month(self, year: int, month: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        按月份筛选数据

        Returns:
            (df_1688_filtered, df_system_filtered)
        """
        # 筛选1688数据
        df_1688_month = self.df_1688[
            (self.df_1688['订单创建时间'].dt.year == year) &
            (self.df_1688['订单创建时间'].dt.month == month)
        ].copy()

        # 筛选系统数据
        df_system_month = self.df_system[
            (self.df_system['日期'].dt.year == year) &
            (self.df_system['日期'].dt.month == month)
        ].copy()

        return df_1688_month, df_system_month

    def test_matching(self, year: int = 2025, month: int = 10,
                     use_filtered_products: bool = False) -> Dict:
        """
        测试匹配效果

        Args:
            year: 年份
            month: 月份
            use_filtered_products: 是否只使用该月份出现的产品作为候选

        Returns:
            匹配测试结果
        """
        print("=" * 100)
        print(f"产品名称匹配测试 - {year}年{month}月")
        print("=" * 100)

        # 筛选数据
        df_1688_month, df_system_month = self.filter_by_month(year, month)

        print(f"\n【数据概览】")
        print(f"1688订单数: {len(df_1688_month)} 条")
        print(f"系统订单数: {len(df_system_month)} 条")

        # 决定使用哪些产品作为匹配候选
        if use_filtered_products:
            candidate_products = df_system_month['产品名称'].dropna().unique().tolist()
            print(f"候选产品数: {len(candidate_products)} 种（仅{month}月出现的产品）")
        else:
            candidate_products = self.system_products
            print(f"候选产品数: {len(candidate_products)} 种（系统全部产品）")

        # 初始化匹配器
        matcher = ProductMatcher(candidate_products)

        # 执行匹配
        results = []
        for idx, row in df_1688_month.iterrows():
            title = row['货品标题']
            order_no = row['订单编号']
            amount = row['实付款(元)']

            match_result = matcher.match(title)
            match_result['order_no'] = order_no
            match_result['title_1688'] = title
            match_result['amount'] = amount

            results.append(match_result)

        # 统计结果
        total = len(results)
        matched = sum(1 for r in results if r['matched'])
        unmatched = total - matched

        # 按匹配方法分类
        exact_matches = [r for r in results if r['method'] == 'exact']
        keyword_matches = [r for r in results if r['method'] == 'keyword']
        fuzzy_matches = [r for r in results if r['method'] == 'fuzzy']
        no_matches = [r for r in results if r['method'] == 'none']

        # 打印统计
        print(f"\n【匹配统计】")
        print(f"总订单数: {total}")
        print(f"匹配成功: {matched} ({matched/total*100:.1f}%)")
        print(f"  - 精确匹配: {len(exact_matches)} ({len(exact_matches)/total*100:.1f}%)")
        print(f"  - 关键词匹配: {len(keyword_matches)} ({len(keyword_matches)/total*100:.1f}%)")
        print(f"  - 模糊匹配: {len(fuzzy_matches)} ({len(fuzzy_matches)/total*100:.1f}%)")
        print(f"未匹配: {unmatched} ({unmatched/total*100:.1f}%)")

        # 匹配置信度分布
        if matched > 0:
            confidences = [r['confidence'] for r in results if r['matched']]
            avg_conf = sum(confidences) / len(confidences)
            print(f"\n平均匹配置信度: {avg_conf:.2f}")

        # 显示详细结果
        self._print_detailed_results(exact_matches, keyword_matches, fuzzy_matches, no_matches)

        return {
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
            'exact_matches': exact_matches,
            'keyword_matches': keyword_matches,
            'fuzzy_matches': fuzzy_matches,
            'no_matches': no_matches,
            'results': results
        }

    def _print_detailed_results(self, exact, keyword, fuzzy, no_match):
        """打印详细匹配结果"""

        print("\n" + "=" * 100)
        print("【匹配详情】")
        print("=" * 100)

        # 1. 精确匹配
        if exact:
            print(f"\n✓ 精确匹配 ({len(exact)} 条):")
            print("-" * 100)
            for i, r in enumerate(exact[:10], 1):
                print(f"{i}. 1688标题: {r['title_1688'][:60]}...")
                print(f"   → 系统产品: {r['product']}")
                print(f"   置信度: {r['confidence']:.0%}")
                print()
            if len(exact) > 10:
                print(f"   ... 还有 {len(exact) - 10} 条精确匹配")

        # 2. 关键词匹配
        if keyword:
            print(f"\n✓ 关键词匹配 ({len(keyword)} 条):")
            print("-" * 100)
            for i, r in enumerate(keyword[:10], 1):
                print(f"{i}. 1688标题: {r['title_1688'][:60]}...")
                print(f"   → 系统产品: {r['product']}")
                print(f"   匹配关键词: {', '.join(r['keywords_matched'])}")
                print(f"   置信度: {r['confidence']:.0%}")
                print()
            if len(keyword) > 10:
                print(f"   ... 还有 {len(keyword) - 10} 条关键词匹配")

        # 3. 模糊匹配
        if fuzzy:
            print(f"\n✓ 模糊匹配 ({len(fuzzy)} 条):")
            print("-" * 100)
            for i, r in enumerate(fuzzy[:5], 1):
                print(f"{i}. 1688标题: {r['title_1688'][:60]}...")
                print(f"   → 系统产品: {r['product']}")
                print(f"   置信度: {r['confidence']:.0%}")
                print()
            if len(fuzzy) > 5:
                print(f"   ... 还有 {len(fuzzy) - 5} 条模糊匹配")

        # 4. 未匹配
        if no_match:
            print(f"\n✗ 未匹配 ({len(no_match)} 条):")
            print("-" * 100)
            for i, r in enumerate(no_match[:10], 1):
                print(f"{i}. 1688标题: {r['title_1688'][:80]}...")
                print(f"   金额: ¥{r['amount']:.2f}")
                print()
            if len(no_match) > 10:
                print(f"   ... 还有 {len(no_match) - 10} 条未匹配")

    def export_results(self, results: Dict, output_file: str = "matching_results.xlsx"):
        """导出匹配结果到Excel"""
        # 转换为DataFrame
        data = []
        for r in results['results']:
            data.append({
                '订单编号': r['order_no'],
                '1688标题': r['title_1688'],
                '金额': r['amount'],
                '是否匹配': '是' if r['matched'] else '否',
                '匹配产品': r['product'] if r['product'] else '',
                '匹配方法': r['method'],
                '置信度': f"{r['confidence']:.0%}",
                '匹配关键词': ', '.join(r['keywords_matched']) if r['keywords_matched'] else ''
            })

        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)
        print(f"\n✅ 匹配结果已导出到: {output_file}")


def main():
    """主函数"""
    print("\n" + "=" * 100)
    print("1688订单产品匹配测试工具")
    print("=" * 100)

    # 初始化测试器
    tester = MatchingTester(
        file_1688="../采购数据.xlsx",
        file_system="../采购表-2（最新版.xlsx"
    )

    # 测试场景1: 使用全部产品作为候选
    print("\n\n【测试场景1: 使用系统全部产品作为候选】")
    print("适用于: 1688订单的产品可能对应系统中任意月份出现的产品")
    results1 = tester.test_matching(year=2025, month=10, use_filtered_products=False)

    # 测试场景2: 只使用10月份出现的产品作为候选
    print("\n\n【测试场景2: 只使用10月份出现的产品作为候选】")
    print("适用于: 假设1688订单的产品都是10月份采购的")
    results2 = tester.test_matching(year=2025, month=10, use_filtered_products=True)

    # 导出结果
    tester.export_results(results1, "matching_results_all_products.xlsx")
    tester.export_results(results2, "matching_results_oct_only.xlsx")

    print("\n" + "=" * 100)
    print("测试完成！")
    print("=" * 100)
    print("\n建议:")
    print("1. 查看导出的Excel文件，检查匹配准确性")
    print("2. 对于未匹配的订单，可以手动添加产品映射规则")
    print("3. 如果匹配率偏低，可以优化关键词提取逻辑")
    print()


if __name__ == "__main__":
    main()
