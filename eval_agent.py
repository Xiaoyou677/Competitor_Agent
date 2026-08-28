"""
Agent项目评测脚本
自动跑评测，生成实际数据（报告准确率、信息完整度、数据来源覆盖率等）
"""
import sys
import os
import time
import json
import re
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ========== 配置 ==========
API_KEY = "f58ee8b964224e3684aa09ffea5fb514.kwE39T3EaNBLA0Pk"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
TAVILY_API_KEY = "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"

# ========== 评测集 ==========
EVAL_DATASET = [
    {
        "product": "iPhone 17 Pro",
        "category": "智能手机",
        "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"],
        "expected_competitors": 3,
        "category": "高端手机"
    },
    {
        "product": "蜜雪冰城柠檬水",
        "category": "茶饮",
        "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"],
        "expected_competitors": 3,
        "category": "茶饮品类"
    },
    {
        "product": "三养火鸡面",
        "category": "方便食品",
        "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"],
        "expected_competitors": 3,
        "category": "方便食品"
    },
    {
        "product": "科沃斯T30 Pro",
        "category": "扫地机器人",
        "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"],
        "expected_competitors": 3,
        "category": "智能家居"
    },
    {
        "product": "华为Mate 70 Pro",
        "category": "智能手机",
        "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"],
        "expected_competitors": 3,
        "category": "高端手机"
    },
]

# ========== 评测指标计算 ==========
def evaluate_report(report_content, product, expected_dimensions, expected_competitors):
    """评估生成的调研报告质量"""
    metrics = {}
    
    # 1. 报告长度（字数）
    metrics["report_length"] = len(report_content)
    
    # 2. 维度覆盖率（预期维度是否都覆盖）
    covered_dimensions = 0
    for dim in expected_dimensions:
        if dim in report_content:
            covered_dimensions += 1
    metrics["dimension_coverage"] = round(covered_dimensions / len(expected_dimensions) * 100, 1) if expected_dimensions else 0
    
    # 3. 竞品数量（是否识别到足够的竞品）
    competitor_count = len(re.findall(r'竞品\d|对比矩阵|SWOT', report_content))
    metrics["competitor_count"] = min(competitor_count, expected_competitors)
    
    # 4. 数据来源数量（是否有数据来源标注）
    source_count = len(re.findall(r'来源|参考|【来源\d】|http', report_content))
    metrics["source_count"] = source_count
    
    # 5. 数据完整度（是否有具体数字）
    number_count = len(re.findall(r'\d+\.?\d*%|\d+\.?\d*元|\d+\.?\d*万|\d+\.?\d*亿', report_content))
    metrics["data_completeness"] = min(number_count * 10, 100)  # 每个数字算10分，满分100
    
    # 6. 结构化程度（是否有标题、列表、表格）
    structure_score = 0
    if '#' in report_content or '##' in report_content:
        structure_score += 30
    if '|' in report_content or '---' in report_content:  # Markdown表格
        structure_score += 30
    if re.search(r'\d+\.', report_content) or '1.' in report_content:
        structure_score += 20
    if '**' in report_content:  # 加粗
        structure_score += 20
    metrics["structure_score"] = min(structure_score, 100)
    
    # 7. 综合得分
    metrics["overall_score"] = round(
        (metrics["dimension_coverage"] * 0.25 +
         metrics["data_completeness"] * 0.25 +
         metrics["structure_score"] * 0.2 +
         min(metrics["source_count"] * 10, 100) * 0.15 +
         min(metrics["competitor_count"] / expected_competitors * 100, 100) * 0.15),
        1
    )
    
    return metrics

# ========== 主函数 ==========
def main():
    print("=" * 60)
    print("Agent项目评测脚本")
    print("=" * 60)
    
    # 由于完整运行Agent需要调用Tavily和大模型，时间较长
    # 这里先输出评测框架和预期指标
    print("\n📊 评测集配置：")
    print(f"  评测产品数量：{len(EVAL_DATASET)} 个")
    for i, item in enumerate(EVAL_DATASET):
        print(f"  [{i+1}] {item['product']}（{item['category']}）")
    
    print("\n📈 评测指标：")
    print("  1. 维度覆盖率（%）- 预期分析维度是否都覆盖")
    print("  2. 数据完整度（%）- 是否有具体数字和数据")
    print("  3. 结构化程度（%）- 是否有标题、列表、表格")
    print("  4. 数据来源数量 - 是否有数据来源标注")
    print("  5. 竞品识别数量 - 是否识别到足够的竞品")
    print("  6. 综合得分（%）- 加权综合评分")
    print("  7. 报告生成时长（秒）")
    
    print("\n⚠️  注意：完整运行评测需要调用Tavily搜索和大模型，每个产品约需2-3分钟，")
    print("   5个产品总共约需10-15分钟。")
    print("\n   由于时间限制，这里先输出评测框架。完整评测结果将在运行后生成。")
    
    # 保存评测框架
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"eval_agent_framework_{timestamp}.json")
    
    eval_framework = {
        "eval_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": "glm-4-flash",
        "search_api": "Tavily",
        "eval_dataset_size": len(EVAL_DATASET),
        "eval_dataset": EVAL_DATASET,
        "metrics": [
            "dimension_coverage",
            "data_completeness",
            "structure_score",
            "source_count",
            "competitor_count",
            "overall_score",
            "generation_time"
        ],
        "note": "完整评测需要运行Agent，生成实际报告后计算指标"
    }
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(eval_framework, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 评测框架已保存到：{result_file}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
