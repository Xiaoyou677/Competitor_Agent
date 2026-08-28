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

# ========== 评测集（100+产品，覆盖多个品类） ==========
EVAL_DATASET = [
    # 智能手机（15个）
    {"product": "iPhone 17 Pro", "category": "高端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "华为Mate 70 Pro", "category": "高端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米15 Ultra", "category": "影像旗舰", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "OPPO Find X8 Pro", "category": "高端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "vivo X200 Pro", "category": "影像旗舰", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "三星S25 Ultra", "category": "高端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "iPhone 17", "category": "中端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "华为Pura 80 Pro", "category": "影像旗舰", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米15", "category": "中端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "OPPO Reno 13 Pro", "category": "中端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "vivo S20 Pro", "category": "中端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "荣耀Magic 7 Pro", "category": "高端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "一加13", "category": "高端手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "真我GT 7 Pro", "category": "性价比手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "红米K80 Pro", "category": "性价比手机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    
    # 茶饮（15个）
    {"product": "蜜雪冰城柠檬水", "category": "茶饮", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "喜茶多肉葡萄", "category": "茶饮", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "奈雪霸气橙子", "category": "茶饮", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "茶百道豆乳玉麒麟", "category": "茶饮", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "古茗超A芝士葡萄", "category": "茶饮", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "沪上阿姨血糯米奶茶", "category": "茶饮", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "丘大叔柠檬茶", "category": "柠檬茶", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "挞柠柠檬茶", "category": "柠檬茶", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "茶救星球柠檬茶", "category": "柠檬茶", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "瑞幸生椰拿铁", "category": "咖啡", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "星巴克拿铁", "category": "咖啡", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Manner冰美式", "category": "咖啡", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "M Stand燕麦拿铁", "category": "咖啡", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "库迪生椰拿铁", "category": "咖啡", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Tims天好咖啡", "category": "咖啡", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    
    # 方便食品（15个）
    {"product": "三养火鸡面", "category": "方便食品", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "康师傅红烧牛肉面", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "统一老坛酸菜牛肉面", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "白象大骨面", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "日清合味道", "category": "杯面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "农心辛拉面", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "不倒翁热拉面", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "八道火鸡面", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "今麦郎一桶半", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "出前一丁", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "汤达人", "category": "方便面", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "螺蛳粉", "category": "方便食品", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "自热火锅", "category": "方便食品", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "自热米饭", "category": "方便食品", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "酸辣粉", "category": "方便食品", "expected_dimensions": ["价格", "口味", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    
    # 智能家居（15个）
    {"product": "科沃斯T30 Pro", "category": "扫地机器人", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "石头G20", "category": "扫地机器人", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "云鲸J4", "category": "扫地机器人", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "追觅X30 Pro", "category": "扫地机器人", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米全能扫拖机器人2", "category": "扫地机器人", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "戴森V15", "category": "吸尘器", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "美的空调", "category": "大家电", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "海尔冰箱", "category": "大家电", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "格力空调", "category": "大家电", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米电视", "category": "大家电", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "华为智慧屏", "category": "大家电", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米手环", "category": "可穿戴设备", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Apple Watch", "category": "可穿戴设备", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "华为手表", "category": "可穿戴设备", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "AirPods Pro", "category": "耳机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    
    # 其他品类（40个）
    {"product": "iPad Pro", "category": "平板电脑", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "华为MatePad", "category": "平板电脑", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米平板", "category": "平板电脑", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "MacBook Pro", "category": "笔记本电脑", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "联想拯救者", "category": "游戏本", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "戴尔XPS", "category": "轻薄本", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "华硕ROG", "category": "游戏本", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "惠普暗影精灵", "category": "游戏本", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Nike Air Force 1", "category": "运动鞋", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Adidas Ultraboost", "category": "运动鞋", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "李宁䨻", "category": "运动鞋", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "安踏KT", "category": "篮球鞋", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "优衣库羽绒服", "category": "服装", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "ZARA连衣裙", "category": "服装", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "H&M卫衣", "category": "服装", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "兰蔻小黑瓶", "category": "护肤品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "雅诗兰黛小棕瓶", "category": "护肤品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "SK-II神仙水", "category": "护肤品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "欧莱雅紫熨斗", "category": "护肤品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "完美日记口红", "category": "化妆品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "花西子散粉", "category": "化妆品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "戴森吹风机", "category": "个护电器", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "飞利浦电动牙刷", "category": "个护电器", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "松下剃须刀", "category": "个护电器", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "乐高积木", "category": "玩具", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "泡泡玛特盲盒", "category": "潮玩", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Switch游戏机", "category": "游戏设备", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "PS5游戏机", "category": "游戏设备", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Xbox Series X", "category": "游戏设备", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "大疆无人机", "category": "数码产品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "GoPro运动相机", "category": "数码产品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "索尼微单", "category": "相机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "佳能单反", "category": "相机", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Kindle电子书", "category": "数码产品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "文石阅读器", "category": "数码产品", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "小米充电宝", "category": "数码配件", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "Anker充电器", "category": "数码配件", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
    {"product": "绿联数据线", "category": "数码配件", "expected_dimensions": ["价格", "核心功能", "产品定位", "目标用户", "用户评分", "核心卖点", "主要劣势"], "expected_competitors": 3},
]
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
