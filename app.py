# -*- coding: utf-8 -*-
"""
电商用户价值数据分析与可视化平台
Glassmorphism Design · Streamlit + Pyecharts
"""
import streamlit as st
import tomllib
import pandas as pd
import numpy as np
import tempfile, os, json
from datetime import timedelta
from pyecharts.charts import Bar, Line, Pie, Scatter, HeatMap, Sankey
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import streamlit.components.v1 as components

# ===== 加载配置文件 =====
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_config():
    """加载 config.toml 配置，返回嵌套字典"""
    config_path = os.path.join(_BASE_DIR, "config.toml")
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}

CFG = _load_config()

# ===== 页面配置 =====
_app = CFG.get("app", {})
st.set_page_config(
    page_title=_app.get("page_title", "电商用户价值分析平台"),
    page_icon=_app.get("page_icon", "📊"),
    layout=_app.get("layout", "wide"),
)

# ===== 背景图列表 =====
import base64
_bg = CFG.get("backgrounds", {})
_BG_DIR = os.path.join(_BASE_DIR, _bg.get("dir", "bg_images"))
BACKGROUNDS = {}
for name, fname in _bg.get("options", {}).items():
    BACKGROUNDS[name] = fname if fname else None
if not BACKGROUNDS:
    BACKGROUNDS = {
        "纯净白（默认）": None,
        "深空蓝紫": "bg1_deep_space.jpg",
        "日落暖橙": "bg2_sunset.jpg",
        "极光青绿": "bg3_aurora.jpg",
        "梦幻粉紫": "bg4_dreamy.jpg",
        "苹果灰蓝": "bg5_apple_gray.jpg",
        "黑金奢华": "bg6_black_gold.jpg",
    }

def _bg_to_data_url(filename):
    path = os.path.join(_BG_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/jpeg;base64,{b64}"

# ===== 全局 CSS · Glassmorphism =====
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=SF+Pro+Display:wght@400;500;600;700&display=swap');

:root {
    --ios-bg:           #f5f5f7;
    --ios-surface:      rgba(255,255,255,0.65);
    --ios-glass:        rgba(255,255,255,0.55);
    --ios-border:       rgba(0,0,0,0.06);
    --ios-border-hover: rgba(0,0,0,0.10);
    --ios-shadow-sm:    0 1px 2px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.03);
    --ios-shadow-md:    0 4px 12px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    --ios-shadow-lg:    0 8px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
    --ios-shadow-xl:    0 16px 48px rgba(0,0,0,0.10), 0 4px 12px rgba(0,0,0,0.05);
    --ios-blue:         #007AFF;
    --ios-blue-glow:    rgba(0,122,255,0.15);
    --ios-purple:       #AF52DE;
    --ios-purple-glow:  rgba(175,82,222,0.14);
    --ios-pink:         #FF2D55;
    --ios-pink-glow:   rgba(255,45,85,0.13);
    --ios-orange:       #FF9500;
    --ios-orange-glow: rgba(255,149,0,0.12);
    --ios-green:        #34C759;
    --ios-teal:         #5AC8FA;
    --ios-text:         #1D1D1F;
    --ios-text2:        #424245;
    --ios-text3:        #86868B;
    --ios-text4:        #AEAEB2;
    --ios-radius:       18px;
    --ios-radius-sm:    12px;
}

/* ========== 全局 ========== */
.stApp {
    color: var(--ios-text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
}

/* 背景层 */
.bg-layer {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1;
    transition: opacity 0.6s ease;
}

/* 默认浅色背景 + 光晕 */
.bg-default {
    background: var(--ios-bg);
}
.bg-default::before {
    content: '';
    position: fixed;
    top: -200px;
    right: -150px;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, var(--ios-blue-glow) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: floatGlow 12s ease-in-out infinite alternate;
}
.bg-default::after {
    content: '';
    position: fixed;
    bottom: -180px;
    left: -120px;
    width: 450px;
    height: 450px;
    background: radial-gradient(circle, var(--ios-purple-glow) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: floatGlow 15s ease-in-out infinite alternate-reverse;
}
@keyframes floatGlow {
    0%   { transform: translate(0, 0) scale(1); opacity: 0.6; }
    100% { transform: translate(30px, -20px) scale(1.1); opacity: 0.9; }
}

/* ========== 液态玻璃卡片 ========== */
@keyframes liquidShimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes liquidGlow {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.8; }
}
@keyframes liquidFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-2px); }
}

/* Tab 容器无边框 */
[data-baseweb="tab-list"] {
    border: none !important;
    box-shadow: none !important;
}

.glass-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.06) 0%,
            rgba(255,255,255,0.02) 50%,
            rgba(255,255,255,0.06) 100%
        ) !important;
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    border-radius: var(--ios-radius);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 10px 22px;
    margin-bottom: 8px;
    position: relative;
    overflow: visible;
    transition: all 0.5s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow:
        0 8px 32px rgba(0,0,0,0.12),
        inset 0 1px 0 rgba(255,255,255,0.12),
        inset 0 -1px 0 rgba(0,0,0,0.05);
    animation: liquidFloat 6s ease-in-out infinite;
}

/* 四边框彩虹光带 — gradient border 技法 */
.glass-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--ios-radius);
    padding: 1.5px;
    background: linear-gradient(
        90deg,
        rgba(120,180,255,0.8) 0%,
        rgba(180,140,255,0.9) 25%,
        rgba(255,180,220,0.85) 50%,
        rgba(180,140,255,0.9) 75%,
        rgba(120,180,255,0.8) 100%
    );
    background-size: 200% 100%;
    pointer-events: none;
    z-index: 2;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    animation: liquidShimmer 3.5s linear infinite;
}

/* 全容器液态微光 — 始终可见 */
.glass-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(
        135deg,
        rgba(120,180,255,0.05) 0%,
        rgba(180,140,255,0.03) 30%,
        rgba(255,180,220,0.04) 55%,
        rgba(180,140,255,0.03) 75%,
        rgba(120,180,255,0.05) 100%
    );
    background-size: 300% 300%;
    pointer-events: none;
    z-index: -1;
    animation: liquidShimmer 8s linear infinite;
}

.glass-card:hover {
    border-color: rgba(255,255,255,0.30);
    transform: translateY(-3px) scale(1.005);
    box-shadow:
        0 16px 48px rgba(120,180,255,0.14),
        inset 0 1px 0 rgba(255,255,255,0.20),
        inset 0 -1px 0 rgba(0,0,0,0.05);
}
.glass-card:hover::before {
    animation: liquidShimmer 1.2s linear infinite;
    padding: 2px;
}
.glass-card:hover::after {
    background-size: 200% 200%;
    animation: liquidShimmer 4s linear infinite;
}

/* ========== KPI 卡片 — 液态玻璃 ========== */
.kpi-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.07) 0%,
            rgba(255,255,255,0.03) 50%,
            rgba(255,255,255,0.07) 100%
        ) !important;
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    border-radius: var(--ios-radius);
    border: 1px solid rgba(255,255,255,0.14);
    padding: 5px 6px;
    margin: 0 10px 10px 10px;
    text-align: center;
    position: relative;
    overflow: visible;
    transition: all 0.5s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow:
        0 6px 24px rgba(0,0,0,0.10),
        inset 0 1px 0 rgba(255,255,255,0.12),
        inset 0 -1px 0 rgba(0,0,0,0.04);
    animation: liquidFloat 5s ease-in-out infinite;
}

/* 顶部主题色条 */
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: var(--ios-radius) var(--ios-radius) 0 0;
    opacity: 0.9;
    z-index: 2;
    animation: liquidShimmer 4s linear infinite;
}
.kpi-card:nth-child(1)::before {
    background: linear-gradient(90deg, #007AFF, #5AC8FA, #007AFF);
    background-size: 200% 100%;
}
.kpi-card:nth-child(2)::before {
    background: linear-gradient(90deg, #34C759, #30D158, #34C759);
    background-size: 200% 100%;
}
.kpi-card:nth-child(3)::before {
    background: linear-gradient(90deg, #FF9500, #FF6B00, #FF9500);
    background-size: 200% 100%;
}
.kpi-card:nth-child(4)::before {
    background: linear-gradient(90deg, #AF52DE, #DA8FFF, #AF52DE);
    background-size: 200% 100%;
}

/* 全容器液态微光 */
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border-radius: var(--ios-radius);
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.04) 0%,
        rgba(255,255,255,0.01) 40%,
        rgba(255,255,255,0.04) 60%,
        rgba(255,255,255,0.01) 100%
    );
    background-size: 250% 250%;
    pointer-events: none;
    z-index: -1;
    animation: liquidShimmer 7s linear infinite;
}

.kpi-card:hover {
    transform: translateY(-3px) scale(1.03);
    border-color: rgba(255,255,255,0.35);
    box-shadow:
        0 10px 28px rgba(0,0,0,0.18),
        inset 0 1px 0 rgba(255,255,255,0.25),
        0 0 16px rgba(120,180,255,0.10);
}
.kpi-card:hover::before {
    height: 4px;
    animation: liquidShimmer 2s linear infinite;
}

.kpi-label {
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 0.6rem;
    font-weight: 600;
    color: var(--ios-text3);
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin-bottom: 4px;
    position: relative;
    z-index: 2;
}
.kpi-value {
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--ios-text);
    letter-spacing: -0.4px;
    position: relative;
    z-index: 2;
}
.kpi-sub {
    font-family: 'SF Mono', 'SF Pro Display', monospace;
    font-size: 0.58rem;
    color: var(--ios-text3);
    margin-top: 3px;
    position: relative;
    z-index: 1;
}

/* ========== 标题系统 ========== */
.main-title {
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 1.82rem;
    font-weight: 800;
    color: var(--ios-text);
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
}
.sub-title {
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 0.88rem;
    font-weight: 650;
    color: var(--ios-text);
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 10px;
    position: relative;
    z-index: 1;
}
.sub-title::before {
    content: '';
    width: 4px;
    height: 16px;
    border-radius: 3px;
    background: linear-gradient(180deg, var(--ios-blue), var(--ios-teal));
    flex-shrink: 0;
}

/* ========== 侧边栏 — 液态玻璃（无背景） ========== */
section[data-testid="stSidebar"] {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-right: 1px solid rgba(255,255,255,0.12) !important;
    box-shadow: inset -1px 0 1px rgba(255,255,255,0.08) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 18px 22px !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: #000 !important;
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="multiselect"] > div,
section[data-testid="stSidebar"] input[type="text"],
section[data-testid="stSidebar"] textarea {
    background: rgba(0,0,0,0.10) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] div,
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] input,
section[data-testid="stSidebar"] [data-baseweb="multiselect"] div,
section[data-testid="stSidebar"] [data-baseweb="multiselect"] span,
section[data-testid="stSidebar"] [data-baseweb="multiselect"] input {
    color: #fff !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="single-value"],
section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="placeholder"],
section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="single-value"],
section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="placeholder"] {
    color: #fff !important;
}

/* ========== Tabs — iOS Segmented Control 风格 ========== */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: transparent !important;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border-radius: 11px;
    padding: 3px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.08);
}
.stTabs [data-baseweb="tab"] {
    padding: 8px 20px;
    border-radius: 9px;
    background: transparent;
    transition: all 0.28s cubic-bezier(0.22, 1, 0.36, 1);
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 0.81rem;
    font-weight: 550;
    border: none;
    color: var(--ios-text3);
    margin: 0;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--ios-text2);
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,255,255,0.12) !important;
    color: var(--ios-text) !important;
    font-weight: 650;
    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.2),
        0 0 0 1px rgba(255,255,255,0.1);
}

/* ========== 页面布局 ========== */
.block-container {
    max-width: 1220px;
    padding: 18px 32px 56px 32px;
    position: relative;
    z-index: 1;
}
div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
div[data-testid="column"] {
    padding-left: 7px !important;
    padding-right: 7px !important;
}
div[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
}

/* ========== 数据表格 ========== */
.stDataFrame {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-radius: var(--ios-radius-sm);
    border: 0.5px solid var(--ios-border);
    overflow: hidden;
}
.stDataFrame table {
    color: var(--ios-text2) !important;
    font-size: 0.76rem;
    font-family: 'Inter', -apple-system, sans-serif;
}
th[data-testid="tableHeader"] {
    background: rgba(245,245,247,0.6) !important;
    font-weight: 600;
    color: var(--ios-text) !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ========== 通用组件覆盖 ========== */
.stRadio label, .stSelectbox label, .stMultiselect label {
    color: var(--ios-text) !important;
    font-family: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 0.8rem;
}
#MainMenu, footer {
    visibility: hidden;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}

/* ========== Streamlit 原生容器液态玻璃 ========== */
/* selectbox / multiselect / date input 共用液态玻璃 */
div[data-baseweb="select"] > div,
div[data-baseweb="multiselect"] > div,
div[data-testid="stDateInput"] > div > div {
    background: transparent !important;
    color: #000 !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.15), 0 0 0 1px rgba(255,255,255,0.04) !important;
    transition: all 0.3s ease !important;
}
div[data-baseweb="select"] [data-baseweb="input"],
div[data-baseweb="select"] [data-baseweb="input"] input,
div[data-baseweb="multiselect"] [data-baseweb="input"],
div[data-baseweb="multiselect"] [data-baseweb="input"] input {
    color: var(--ios-text) !important;
}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="multiselect"] > div:focus-within,
div[data-testid="stDateInput"] > div > div:focus-within {
    border-color: rgba(0,122,255,0.35) !important;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.25), 0 0 0 1px rgba(0,122,255,0.15) !important;
}
/* 下拉弹出菜单 — 液态玻璃 */
ul[data-baseweb="menu"] {
    background: rgba(28,28,32,0.92) !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.1),
        0 4px 16px rgba(0,0,0,0.3) !important;
}
li[data-baseweb="menu-item"] {
    color: var(--ios-text) !important;
}
li[data-baseweb="menu-item"]:hover {
    background: rgba(0,122,255,0.08) !important;
}

/* Tab 内容区域 — 液态玻璃 */
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-radius: 0 0 14px 14px;
    border: none !important;
    border-top: none !important;
    padding: 16px 14px;
    margin-top: -3px;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.05);
}

/* st.markdown 容器（非 glass-card 内的） */
.stMarkdown:not(.glass-card *) {
    color: var(--ios-text2);
}

/* 分隔线 */
hr {
    border: none !important;
    height: 0.5px !important;
    background: var(--ios-border) !important;
    margin: 14px 0 !important;
}

/* st.status 容器 */
.stStatusWidget {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px !important;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 0 0 1px rgba(255,255,255,0.03);
}

/* 表格容器 — 无背景液态玻璃 */
.stTable, .stDataFrame {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-radius: var(--ios-radius-sm);
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 0 0 1px rgba(255,255,255,0.02);
}

/* ========== 精致滚动条 ========== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.12);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.3);
    transition: background 0.2s;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0,0,0,0.22);
}

/* ========== 入场动画 — 精致弹性 ========== */
@keyframes iosFadeInUp {
    from {
        opacity: 0;
        transform: translateY(16px) scale(0.98);
        filter: blur(4px);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
        filter: blur(0);
    }
}
.glass-card {
    animation: iosFadeInUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
.kpi-card {
    animation: iosFadeInUp 0.42s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
.kpi-card:nth-child(1) { animation-delay: 0s; }
.kpi-card:nth-child(2) { animation-delay: 0.07s; }
.kpi-card:nth-child(3) { animation-delay: 0.14s; }
.kpi-card:nth-child(4) { animation-delay: 0.21s; }

/* ========== 分层标签芯片 ========== */
.seg-chip {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-family: 'SF Mono', 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.3px;
    background: rgba(255,255,255,0.08);
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.12);
}


/* ========== Streamlit containers - liquid glass ========== */
.stMarkdown > div[data-testid="stMarkdownContainer"],
.stHtml > div[data-testid="stHtmlContainer"] {
    background: transparent !important;
}
main .stMarkdown,
main .stHtml {
    background: transparent !important;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"],
div[data-testid="stColumns"] > div[data-testid="column"] {
    background: transparent !important;
}
/* Chart container glass effect */
.stHtml iframe,
.stHtml [data-testid="iframe"] {
    border-radius: var(--ios-radius) !important;
    overflow: hidden;
}


/* Force all Streamlit structural containers transparent */
.stTabs {
    background: transparent !important;
}
section[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlock"] {
    background: transparent !important;
}
[data-testid="stAppViewBlockContainer"],
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}


/* Force all Streamlit structural containers transparent */
.stTabs {
    background: transparent !important;
}
section[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlock"] {
    background: transparent !important;
}
[data-testid="stAppViewBlockContainer"],
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}


/* === NUCLEAR: Force ALL containers transparent === */
[data-baseweb="tab-panel"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stLayoutWrapper"],
[data-testid="stColumn"],
[data-testid="stElementContainer"],
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdown"],
[data-testid="stIFrame"] {
    background: transparent !important;
    background-color: transparent !important;
}


/* Kill ALL backdrop-filter on structural containers */
[data-baseweb="tab-panel"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stLayoutWrapper"],
[data-testid="stColumn"],
[data-testid="stElementContainer"] {
    backdrop-filter: none !important;
    border: none !important;
    box-shadow: none !important;
}

/* ========== 内联弹窗（无刷新） ========== */
.oc-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 999999;
    background: transparent !important;
    animation: ocFadeIn 0.25s ease;
}
@keyframes ocFadeIn {
    from { opacity: 0; } to { opacity: 1; }
}
.oc-box {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: min(92vw, 800px);
    max-height: 88vh;
    background: rgba(255,255,255,0.25) !important;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 32px rgba(0,0,0,0.10), inset 0 1px 0 rgba(255,255,255,0.3);
    overflow: hidden;
    animation: ocSlideIn 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
@keyframes ocSlideIn {
    from { opacity: 0; transform: translate(-50%, -48%) scale(0.96); }
    to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}
.oc-head {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 24px;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}
.oc-head h3 {
    margin: 0; font-size: 1.05rem; font-weight: 700;
    background: linear-gradient(135deg, #007AFF, #AF52DE);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.oc-close {
    width: 32px; height: 32px; border-radius: 50%; border: none;
    background: rgba(0,0,0,0.06); color: #86868B; font-size: 18px;
    cursor: pointer; transition: all 0.2s;
    display: flex; align-items: center; justify-content: center;
}
.oc-close:hover { background: rgba(255,59,48,0.12); color: #FF3B30; transform: scale(1.1); }
.oc-body { padding: 20px 24px; overflow-y: auto; max-height: calc(88vh - 70px); }
.oc-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 20px; }
.oc-metric {
    background: linear-gradient(135deg, rgba(0,122,255,0.06), rgba(175,82,222,0.06));
    border-radius: 14px; padding: 14px 16px; text-align: center;
    border: 1px solid rgba(0,0,0,0.04);
}
.oc-metric .lb { font-size: 0.7rem; color: #000; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.oc-metric .vl { font-size: 1.2rem; font-weight: 800; color: #000; }
.oc-section { margin-bottom: 18px; }
.oc-section h4 { font-size: 0.82rem; font-weight: 700; color: #000; margin: 0 0 10px; display: flex; align-items: center; gap: 6px; }
.oc-section h4::before { content: ''; width: 3px; height: 14px; border-radius: 2px; background: linear-gradient(180deg, #007AFF, #5AC8FA); }
.oc-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.oc-bar-label { width: 140px; font-size: 0.75rem; color: #000; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.oc-bar-track { flex: 1; height: 22px; background: rgba(0,0,0,0.04); border-radius: 6px; overflow: hidden; position: relative; }
.oc-bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1); min-width: 2px; }
.oc-bar-val { width: 90px; font-size: 0.75rem; font-weight: 700; color: #000; }
.oc-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.oc-table th { padding: 8px 10px; background: rgba(0,0,0,0.04); font-weight: 600; color: #000; text-align: left; border-bottom: 1px solid rgba(0,0,0,0.08); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.3px; }
.oc-table td { padding: 8px 10px; color: #000; border-bottom: 1px solid rgba(0,0,0,0.04); }
.oc-table tr:hover td { background: rgba(0,122,255,0.04); }
.oc-hint { font-size: 0.72rem; color: #000; text-align: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.06); }
@media (prefers-color-scheme: dark) {
    .oc-box { background: rgba(30,30,35,0.25) !important; backdrop-filter: blur(24px) saturate(180%); -webkit-backdrop-filter: blur(24px) saturate(180%); }
    .oc-head { border-bottom-color: rgba(255,255,255,0.08); }
    .oc-metric { background: linear-gradient(135deg, rgba(0,122,255,0.12), rgba(175,82,222,0.12)); border-color: rgba(255,255,255,0.06); }
    .oc-metric .lb { color: #fff; }
    .oc-metric .vl { color: #fff; }
    .oc-section h4 { color: #fff; }
    .oc-bar-label { color: #fff; }
    .oc-bar-track { background: rgba(255,255,255,0.06); }
    .oc-bar-val { color: #fff; }
    .oc-table th { background: rgba(255,255,255,0.06); color: #fff; border-bottom-color: rgba(255,255,255,0.08); }
    .oc-table td { color: #fff; border-bottom-color: rgba(255,255,255,0.05); }
    .oc-table tr:hover td { background: rgba(0,122,255,0.08); }
    .oc-close { background: rgba(255,255,255,0.1); color: #fff; }
    .oc-close:hover { background: rgba(255,59,48,0.15); color: #FF3B30; }
}
</style>
""", unsafe_allow_html=True)


# ===== 数据加载与缓存 =====
_data_cfg = CFG.get("data", {})
_DATA_DIR = _BASE_DIR
_CSV  = os.path.join(_DATA_DIR, _data_cfg.get("csv_file", "Online Retail.csv"))
_XLSX = os.path.join(_DATA_DIR, _data_cfg.get("xlsx_file", "Online Retail.xlsx"))
_CACHE_TTL = _data_cfg.get("cache_ttl", 3600)
_MIN_QTY  = _data_cfg.get("min_quantity", 0)
_MIN_PRICE = _data_cfg.get("min_unit_price", 0)

@st.cache_data(ttl=86400)  # 缓存24小时
def load_data():
    if not os.path.exists(_CSV):
        _tmp = pd.read_excel(_XLSX)
        _tmp.to_csv(_CSV, index=False)
        del _tmp
    # 使用更小的数据类型优化内存
    dtypes = {
        "InvoiceNo": "category",
        "StockCode": "category",
        "Description": "category",
        "Quantity": "int32",
        "UnitPrice": "float32",
        "CustomerID": "float32",
        "Country": "category",
        "InvoiceDate": "string",
    }
    df = pd.read_csv(_CSV, dtype=dtypes, parse_dates=["InvoiceDate"])
    df = df.dropna(subset=["CustomerID"])
    df = df[df["Quantity"] > _MIN_QTY]
    df = df[df["UnitPrice"] > _MIN_PRICE]
    df["Amount"]   = (df["Quantity"] * df["UnitPrice"]).astype("float32")
    df["CustomerID"]  = df["CustomerID"].astype("int32").astype(str)
    df["Year"]   = df["InvoiceDate"].dt.year.astype("int16")
    df["Month"]  = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["Date"]   = df["InvoiceDate"].dt.date
    return df


_rfm_cfg = CFG.get("rfm", {})
_RFM_BINS = _rfm_cfg.get("n_bins", 5)
_RFM_THR  = _rfm_cfg.get("high_threshold", 4)
_L = _rfm_cfg.get("labels", {})
_L_IV = _L.get("important_value", "重要价值用户")
_L_ID = _L.get("important_develop", "重要发展用户")
_L_IR = _L.get("important_retain", "重要保持用户")
_L_IT = _L.get("important_retrieve", "重要挽留用户")
_L_GV = _L.get("general_value", "一般价值用户")
_L_GD = _L.get("general_develop", "一般发展用户")
_L_GR = _L.get("general_retain", "一般保持用户")
_L_GT = _L.get("general_retrieve", "一般挽留用户")
_SL = _rfm_cfg.get("sankey_labels", {})
_SL_HR = _SL.get("high_r", "高活跃")
_SL_LR = _SL.get("low_r", "低活跃")
_SL_HF = _SL.get("high_f", "高频")
_SL_LF = _SL.get("low_f", "低频")
_SL_HM = _SL.get("high_m", "高消费")
_SL_LM = _SL.get("low_m", "低消费")

@st.cache_data(ttl=_CACHE_TTL)
def compute_rfm(df, end_date):
    snapshot = pd.to_datetime(end_date) + timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        R=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        F=("InvoiceNo",   "nunique"),
        M=("Amount",      "sum"),
    ).reset_index()
    rfm["R_score"] = pd.qcut(rfm["R"], _RFM_BINS, labels=list(range(_RFM_BINS, 0, -1))).astype(int)
    rfm["F_score"] = pd.qcut(rfm["F"].rank(method="first"), _RFM_BINS, labels=list(range(1, _RFM_BINS+1))).astype(int)
    rfm["M_score"] = pd.qcut(rfm["M"], _RFM_BINS, labels=list(range(1, _RFM_BINS+1))).astype(int)

    def label(r, f, m):
        if r>=_RFM_THR and f>=_RFM_THR and m>=_RFM_THR: return _L_IV
        if r>=_RFM_THR and f<_RFM_THR and m>=_RFM_THR:  return _L_ID
        if r<_RFM_THR  and f>=_RFM_THR and m>=_RFM_THR:  return _L_IR
        if r<_RFM_THR  and f<_RFM_THR  and m>=_RFM_THR:  return _L_IT
        if r>=_RFM_THR and f>=_RFM_THR and m<_RFM_THR:   return _L_GV
        if r>=_RFM_THR and f<_RFM_THR  and m<_RFM_THR:   return _L_GD
        if r<_RFM_THR  and f>=_RFM_THR and m<_RFM_THR:   return _L_GR
        return _L_GT

    rfm["Segment"] = rfm.apply(
        lambda x: label(x["R_score"], x["F_score"], x["M_score"]), axis=1
    )
    return rfm


# ===== Pyecharts 渲染器 =====
def render_pe(chart, height=350, chart_id=None, detail_html=None):
    """渲染 pyecharts 图表。传入 detail_html 时，点击图表节点弹出内联详情卡片（无页面刷新）。"""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
    chart.render(path=tmp.name)
    tmp.close()
    with open(tmp.name, 'r', encoding='utf-8') as f:
        html = f.read()
    os.unlink(tmp.name)
    html = html.replace(
        '<body>',
        '<body style="margin:0;padding:0;background:transparent;">'
    )

    if chart_id and detail_html:
        cid = chart_id
        detail_json = json.dumps(detail_html, ensure_ascii=False).replace('</', r'<\/')

        # 弹窗 HTML + CSS + JS 注入到同一个 iframe
        popup_block = f'''
<style>
.oc-overlay{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;background:transparent!important}}
.oc-box{{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:min(92vw,720px);max-height:85vh;background:rgba(255,255,255,0.25)!important;backdrop-filter:blur(24px) saturate(180%);-webkit-backdrop-filter:blur(24px) saturate(180%);border-radius:20px;border:1px solid rgba(255,255,255,0.25);box-shadow:0 8px 32px rgba(0,0,0,0.10),inset 0 1px 0 rgba(255,255,255,0.3);overflow:hidden}}
.oc-head{{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;border-bottom:1px solid rgba(0,0,0,0.06)}}
.oc-head h3{{margin:0;font-size:1.05rem;font-weight:700;background:linear-gradient(135deg,#007AFF,#AF52DE);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.oc-close{{width:32px;height:32px;border-radius:50%;border:none;background:rgba(0,0,0,0.06);color:#000;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center}}
.oc-close:hover{{background:rgba(255,59,48,0.12);color:#FF3B30}}
.oc-body{{padding:20px 24px;overflow-y:auto;max-height:calc(85vh - 70px)}}
.oc-metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-bottom:20px}}
.oc-metric{{background:linear-gradient(135deg,rgba(0,122,255,0.06),rgba(175,82,222,0.06));border-radius:14px;padding:14px 16px;text-align:center;border:1px solid rgba(0,0,0,0.04)}}
.oc-metric .lb{{font-size:0.7rem;color:#000;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}}
.oc-metric .vl{{font-size:1.1rem;font-weight:800;color:#000}}
.oc-section{{margin-bottom:18px}}
.oc-section h4{{font-size:0.82rem;font-weight:700;color:#000;margin:0 0 10px;display:flex;align-items:center;gap:6px}}
.oc-section h4::before{{content:"";width:3px;height:14px;border-radius:2px;background:linear-gradient(180deg,#007AFF,#5AC8FA)}}
.oc-bar-row{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.oc-bar-label{{width:130px;font-size:0.72rem;color:#000;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.oc-bar-track{{flex:1;height:20px;background:rgba(0,0,0,0.04);border-radius:6px;overflow:hidden}}
.oc-bar-fill{{height:100%;border-radius:6px;min-width:2px}}
.oc-bar-val{{width:80px;font-size:0.72rem;font-weight:700;color:#000}}
.oc-table{{width:100%;border-collapse:collapse;font-size:0.75rem}}
.oc-table th{{padding:7px 8px;background:rgba(0,0,0,0.03);font-weight:600;color:#000;text-align:left;border-bottom:1px solid rgba(0,0,0,0.06);font-size:0.68rem;text-transform:uppercase;letter-spacing:0.3px}}
.oc-table td{{padding:7px 8px;color:#000;border-bottom:1px solid rgba(0,0,0,0.03)}}
.oc-table tr:hover td{{background:rgba(0,122,255,0.04)}}
.oc-hint{{font-size:0.7rem;color:#000;text-align:center;margin-top:10px;padding-top:10px;border-top:1px solid rgba(0,0,0,0.04)}}
</style>
<div id="oc_{cid}" class="oc-overlay" onclick="if(event.target===this)this.style.display='none'">
  <div class="oc-box">
    <div class="oc-head">
      <h3 id="oc_t_{cid}">详情</h3>
      <button class="oc-close" onclick="document.getElementById('oc_{cid}').style.display='none'">×</button>
    </div>
    <div class="oc-body" id="oc_b_{cid}"></div>
  </div>
</div>
<script>
(function(){{
  var D={detail_json};
  var ov=document.getElementById("oc_{cid}");
  var bd=document.getElementById("oc_b_{cid}");
  var tt=document.getElementById("oc_t_{cid}");
  function sp(n){{
    if(!ov||!bd)return;
    var h=D[n];
    if(!h)h="<div style='text-align:center;padding:40px;color:#000;'>暂无详情</div>";
    bd.innerHTML=h;tt.textContent=n+" · 详情";ov.style.display="block";
  }}
  function bind(){{
    try{{
      var dom=document.querySelector("[_echarts_instance_]");
      if(!dom){{setTimeout(bind,300);return;}}
      var inst=echarts.getInstanceByDom(dom);
      if(!inst){{setTimeout(bind,300);return;}}
      inst.on("click",function(p){{var n=p.name||"";if(n)sp(n);}});
    }}catch(e){{setTimeout(bind,300);}}
  }}
  setTimeout(bind,500);
  document.addEventListener("keydown",function(e){{if(e.key==="Escape"&&ov)ov.style.display="none";}});
}})();
</script>
'''
        html = html.replace('</body>', popup_block + '</body>')

    components.html(html, height=height + 30)


# ===== 经营概览 · 弹窗详情内容生成器 =====
def _build_detail_monthly(df):
    """月度销售趋势 → 点击月份弹出详情"""
    monthly = df.groupby("Month").agg(销售额=("Amount", "sum"), 订单数=("InvoiceNo", "nunique"), 用户数=("CustomerID", "nunique")).reset_index()
    monthly["客单价"] = (monthly["销售额"] / monthly["订单数"]).round(2)
    result = {}
    for _, row in monthly.iterrows():
        m = row["Month"]
        mdf = df[df["Month"] == m]
        top5_prod = mdf.groupby("Description")["Amount"].sum().sort_values(ascending=False).head(5)
        top5_ctry = mdf.groupby("Country")["Amount"].sum().sort_values(ascending=False).head(5)
        max_p = top5_prod.max() if len(top5_prod) > 0 else 1
        max_c = top5_ctry.max() if len(top5_ctry) > 0 else 1
        prod_bars = "".join(
            f'<div class="oc-bar-row"><span class="oc-bar-label" title="{n}">{n[:18]}</span>'
            f'<div class="oc-bar-track"><div class="oc-bar-fill" style="width:{v/max_p*100:.1f}%;background:linear-gradient(90deg,#f472b6,#fbbf24)"></div></div>'
            f'<span class="oc-bar-val">¥{v:,.0f}</span></div>'
            for n, v in zip(top5_prod.index, top5_prod.values)
        )
        ctry_bars = "".join(
            f'<div class="oc-bar-row"><span class="oc-bar-label">{n}</span>'
            f'<div class="oc-bar-track"><div class="oc-bar-fill" style="width:{v/max_c*100:.1f}%;background:linear-gradient(90deg,#38bdf8,#a78bfa)"></div></div>'
            f'<span class="oc-bar-val">¥{v:,.0f}</span></div>'
            for n, v in zip(top5_ctry.index, top5_ctry.values)
        )
        result[m] = (
            f'<div class="oc-metrics">'
            f'<div class="oc-metric"><div class="lb">销售额</div><div class="vl">¥{row["销售额"]/1e6:.2f}M</div></div>'
            f'<div class="oc-metric"><div class="lb">订单数</div><div class="vl">{int(row["订单数"]):,}</div></div>'
            f'<div class="oc-metric"><div class="lb">用户数</div><div class="vl">{int(row["用户数"]):,}</div></div>'
            f'<div class="oc-metric"><div class="lb">客单价</div><div class="vl">¥{row["客单价"]:,.2f}</div></div>'
            f'</div>'
            f'<div class="oc-section"><h4>🏆 TOP5 商品</h4>{prod_bars}</div>'
            f'<div class="oc-section"><h4>🌍 TOP5 国家</h4>{ctry_bars}</div>'
            f'<div class="oc-hint">💡 点击其他月份查看 · ESC 关闭</div>'
        )
    return result


def _build_detail_country(df):
    """国家销售额 TOP10 → 点击国家弹出详情"""
    top10 = df.groupby("Country").agg(销售额=("Amount", "sum"), 订单数=("InvoiceNo", "nunique"), 用户数=("CustomerID", "nunique")).sort_values("销售额", ascending=False).head(10)
    top10["客单价"] = (top10["销售额"] / top10["订单数"]).round(2)
    result = {}
    for country, row in top10.iterrows():
        cdf = df[df["Country"] == country]
        monthly = cdf.groupby("Month")["Amount"].sum()
        max_m = monthly.max() if len(monthly) > 0 else 1
        trend_bars = "".join(
            f'<div class="oc-bar-row"><span class="oc-bar-label">{m}</span>'
            f'<div class="oc-bar-track"><div class="oc-bar-fill" style="width:{v/max_m*100:.1f}%;background:linear-gradient(90deg,#a78bfa,#38bdf8)"></div></div>'
            f'<span class="oc-bar-val">¥{v:,.0f}</span></div>'
            for m, v in zip(monthly.index, monthly.values)
        )
        top5_prod = cdf.groupby("Description")["Amount"].sum().sort_values(ascending=False).head(5)
        max_p = top5_prod.max() if len(top5_prod) > 0 else 1
        prod_bars = "".join(
            f'<div class="oc-bar-row"><span class="oc-bar-label" title="{n}">{n[:18]}</span>'
            f'<div class="oc-bar-track"><div class="oc-bar-fill" style="width:{v/max_p*100:.1f}%;background:linear-gradient(90deg,#f472b6,#fbbf24)"></div></div>'
            f'<span class="oc-bar-val">¥{v:,.0f}</span></div>'
            for n, v in zip(top5_prod.index, top5_prod.values)
        )
        result[country] = (
            f'<div class="oc-metrics">'
            f'<div class="oc-metric"><div class="lb">销售额</div><div class="vl">¥{row["销售额"]/1e6:.2f}M</div></div>'
            f'<div class="oc-metric"><div class="lb">订单数</div><div class="vl">{int(row["订单数"]):,}</div></div>'
            f'<div class="oc-metric"><div class="lb">用户数</div><div class="vl">{int(row["用户数"]):,}</div></div>'
            f'<div class="oc-metric"><div class="lb">客单价</div><div class="vl">¥{row["客单价"]:,.2f}</div></div>'
            f'</div>'
            f'<div class="oc-section"><h4>📈 月度销售趋势</h4>{trend_bars}</div>'
            f'<div class="oc-section"><h4>🏆 TOP5 商品</h4>{prod_bars}</div>'
            f'<div class="oc-hint">💡 点击其他国家查看 · ESC 关闭</div>'
        )
    return result


def _build_detail_rfm(rfm, df):
    """RFM 分层饼图/柱状图 → 点击分层弹出详情"""
    SEGMENT_COLORS = {
        "重要价值用户": "#a78bfa", "重要发展用户": "#38bdf8", "重要保持用户": "#fbbf24", "重要挽留用户": "#fb7185",
        "一般价值用户": "#60a5fa", "一般发展用户": "#34d399", "一般保持用户": "#c084fc", "一般挽留用户": "#94a3b8",
    }
    seg_counts = rfm["Segment"].value_counts()
    result = {}
    for seg_name in SEGMENT_COLORS:
        if seg_name not in seg_counts.index:
            continue
        seg_rfm = rfm[rfm["Segment"] == seg_name]
        seg_uids = seg_rfm["CustomerID"].tolist()
        seg_df = df[df["CustomerID"].isin(seg_uids)]
        n_users = len(seg_uids)
        total_sales = seg_df["Amount"].sum()
        avg_r = seg_rfm["R"].mean()
        avg_f = seg_rfm["F"].mean()
        avg_m = seg_rfm["M"].mean()
        avg_order = total_sales / seg_df["InvoiceNo"].nunique() if seg_df["InvoiceNo"].nunique() else 0
        top5_ctry = seg_df.groupby("Country")["Amount"].sum().sort_values(ascending=False).head(5)
        max_c = top5_ctry.max() if len(top5_ctry) > 0 else 1
        ctry_bars = "".join(
            f'<div class="oc-bar-row"><span class="oc-bar-label">{n}</span>'
            f'<div class="oc-bar-track"><div class="oc-bar-fill" style="width:{v/max_c*100:.1f}%;background:linear-gradient(90deg,#fbbf24,#fb7185)"></div></div>'
            f'<span class="oc-bar-val">¥{v:,.0f}</span></div>'
            for n, v in zip(top5_ctry.index, top5_ctry.values)
        )
        top_users = seg_rfm.sort_values("M", ascending=False).head(10)
        rows = "".join(
            f'<tr><td>{r["CustomerID"]}</td><td>{r["R"]}天</td><td>{r["F"]}次</td><td>¥{r["M"]:,.0f}</td>'
            f'<td>{r["R_score"]}/{r["F_score"]}/{r["M_score"]}</td></tr>'
            for _, r in top_users.iterrows()
        )
        color = SEGMENT_COLORS.get(seg_name, "#999")
        result[seg_name] = (
            f'<div class="oc-metrics">'
            f'<div class="oc-metric"><div class="lb">用户数</div><div class="vl">{n_users:,}</div></div>'
            f'<div class="oc-metric"><div class="lb">销售额</div><div class="vl">¥{total_sales/1e6:.2f}M</div></div>'
            f'<div class="oc-metric"><div class="lb">平均 R</div><div class="vl">{avg_r:.0f}天</div></div>'
            f'<div class="oc-metric"><div class="lb">平均 F</div><div class="vl">{avg_f:.1f}次</div></div>'
            f'<div class="oc-metric"><div class="lb">平均 M</div><div class="vl">¥{avg_m:,.0f}</div></div>'
            f'<div class="oc-metric"><div class="lb">客单价</div><div class="vl">¥{avg_order:,.2f}</div></div>'
            f'</div>'
            f'<div class="oc-section"><h4>🌍 TOP5 国家</h4>{ctry_bars}</div>'
            f'<div class="oc-section"><h4>👥 TOP10 用户</h4>'
            f'<table class="oc-table"><thead><tr><th>用户ID</th><th>R</th><th>F</th><th>M</th><th>R/F/M分</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            f'<div class="oc-hint">💡 点击其他分层查看 · ESC 关闭</div>'
        )
        # 同时存入缩写名，适配柱状图的 x 轴标签
        short = LEGEND_NAME_MAP.get(seg_name, seg_name)
        if short != seg_name:
            result[short] = result[seg_name]
    return result


# ===== Dialog 弹窗函数 =====

@st.dialog("📅 月度销售详情", width="large")
def dialog_month_detail(month, df):
    mdf = df[df["Month"] == month]
    daily = mdf.groupby("Date").agg(销售额=("Amount","sum"), 订单数=("InvoiceNo","nunique")).reset_index()
    total_sales = mdf["Amount"].sum()
    total_orders = mdf["InvoiceNo"].nunique()
    total_users = mdf["CustomerID"].nunique()
    avg_order = total_sales / total_orders if total_orders else 0

    st.markdown(f'<p style="font-size:0.85rem;color:#94a3b8;margin-bottom:8px;">当前月份：{month}</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("销售额", f"{total_sales/1e6:.2f}M")
    with c2: st.metric("订单数", f"{total_orders:,}")
    with c3: st.metric("用户数", f"{total_users:,}")
    with c4: st.metric("客单价", f"{avg_order:,.2f}")

    # 日销售趋势
    daily_chart = (
        Line(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
        .add_xaxis([str(d) for d in daily["Date"].tolist()])
        .add_yaxis("销售额", daily["销售额"].round(2).tolist(), is_smooth=True,
                   label_opts=opts.LabelOpts(is_show=False),
                   linestyle_opts=opts.LineStyleOpts(width=2.5, color="#a78bfa"),
                   areastyle_opts=opts.AreaStyleOpts(opacity=0.2))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, color="#94a3b8", font_size=8)),
            yaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )
    st.markdown('<p class="sub-title" style="font-size:0.85rem;">📈 日销售趋势</p>', unsafe_allow_html=True)
    render_pe(daily_chart, height=280)

    # TOP5商品 + TOP5国家 两栏
    cl, cr = st.columns(2)
    with cl:
        top5_prod = mdf.groupby("Description")["Amount"].sum().sort_values(ascending=False).head(5)
        prod_bar = (
            Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
            .add_xaxis(top5_prod.index.tolist()[::-1])
            .add_yaxis("销售额", top5_prod.values.round(2).tolist()[::-1],
                       label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(
                           color=JsCode("new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f472b6'},{offset:1,color:'#fbbf24'}])"),
                           border_radius=[0,6,6,0]))
            .reversal_axis()
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#94a3b8", font_size=10)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st.markdown('<p class="sub-title" style="font-size:0.85rem;">🏆 TOP5 商品</p>', unsafe_allow_html=True)
        render_pe(prod_bar, height=280)
    with cr:
        top5_ctry = mdf.groupby("Country")["Amount"].sum().sort_values(ascending=False).head(5)
        ctry_bar = (
            Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
            .add_xaxis(top5_ctry.index.tolist())
            .add_yaxis("销售额", top5_ctry.values.round(2).tolist(),
                       label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(
                           color=JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#38bdf8'},{offset:1,color:'#a78bfa'}])"),
                           border_radius=[6,6,0,0]))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30, color="#94a3b8", font_size=10)),
                yaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st.markdown('<p class="sub-title" style="font-size:0.85rem;">🌍 TOP5 国家</p>', unsafe_allow_html=True)
        render_pe(ctry_bar, height=280)

    # 各时段订单分布
    hour = mdf.groupby(mdf["InvoiceDate"].dt.hour).agg(订单数=("InvoiceNo","nunique")).reset_index()
    hour.columns = ["小时","订单数"]
    hour_chart = (
        Line(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="250px"))
        .add_xaxis(hour["小时"].tolist())
        .add_yaxis("订单数", hour["订单数"].tolist(), is_smooth=True,
                   areastyle_opts=opts.AreaStyleOpts(opacity=0.2),
                   label_opts=opts.LabelOpts(is_show=False),
                   linestyle_opts=opts.LineStyleOpts(width=2.5, color="#fbbf24"))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="小时", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8")),
            yaxis_opts=opts.AxisOpts(name="订单数", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )
    st.markdown('<p class="sub-title" style="font-size:0.85rem;">⏰ 各时段订单分布</p>', unsafe_allow_html=True)
    render_pe(hour_chart, height=250)


@st.dialog("🌍 国家销售详情", width="large")
def dialog_country_detail(country, df):
    cdf = df[df["Country"] == country]
    total_sales = cdf["Amount"].sum()
    total_orders = cdf["InvoiceNo"].nunique()
    total_users = cdf["CustomerID"].nunique()
    avg_order = total_sales / total_orders if total_orders else 0

    st.markdown(f'<p style="font-size:0.85rem;color:#94a3b8;margin-bottom:8px;">当前国家：{country}</p>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("销售额", f"{total_sales/1e6:.2f}M")
    with c2: st.metric("订单数", f"{total_orders:,}")
    with c3: st.metric("用户数", f"{total_users:,}")
    with c4: st.metric("客单价", f"{avg_order:,.2f}")

    # 月度趋势
    monthly = cdf.groupby("Month").agg(销售额=("Amount","sum"), 订单数=("InvoiceNo","nunique")).reset_index()
    mo_chart = (
        Line(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
        .add_xaxis(monthly["Month"].tolist())
        .add_yaxis("销售额", monthly["销售额"].round(2).tolist(), is_smooth=True,
                   label_opts=opts.LabelOpts(is_show=False),
                   linestyle_opts=opts.LineStyleOpts(width=2.5, color="#a78bfa"),
                   areastyle_opts=opts.AreaStyleOpts(opacity=0.2))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, color="#94a3b8", font_size=9)),
            yaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )
    st.markdown('<p class="sub-title" style="font-size:0.85rem;">📈 月度销售趋势</p>', unsafe_allow_html=True)
    render_pe(mo_chart, height=280)

    # TOP5商品 + 时段分布 两栏
    cl, cr = st.columns(2)
    with cl:
        top5 = cdf.groupby("Description")["Amount"].sum().sort_values(ascending=False).head(5)
        prod_bar = (
            Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
            .add_xaxis(top5.index.tolist()[::-1])
            .add_yaxis("销售额", top5.values.round(2).tolist()[::-1],
                       label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(
                           color=JsCode("new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f472b6'},{offset:1,color:'#fbbf24'}])"),
                           border_radius=[0,6,6,0]))
            .reversal_axis()
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#94a3b8", font_size=10)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st.markdown('<p class="sub-title" style="font-size:0.85rem;">🏆 TOP5 商品</p>', unsafe_allow_html=True)
        render_pe(prod_bar, height=280)
    with cr:
        hour = cdf.groupby(cdf["InvoiceDate"].dt.hour).agg(订单数=("InvoiceNo","nunique")).reset_index()
        hour.columns = ["小时","订单数"]
        hour_chart = (
            Line(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
            .add_xaxis(hour["小时"].tolist())
            .add_yaxis("订单数", hour["订单数"].tolist(), is_smooth=True,
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.2),
                       label_opts=opts.LabelOpts(is_show=False),
                       linestyle_opts=opts.LineStyleOpts(width=2.5, color="#38bdf8"))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(name="小时", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8")),
                yaxis_opts=opts.AxisOpts(name="订单数", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st.markdown('<p class="sub-title" style="font-size:0.85rem;">⏰ 各时段订单分布</p>', unsafe_allow_html=True)
        render_pe(hour_chart, height=280)


@st.dialog("📊 RFM 分层详情", width="large")
def dialog_segment_detail(seg_name, rfm, df):
    seg_uids = rfm[rfm["Segment"] == seg_name]["CustomerID"].tolist()
    seg_df = df[df["CustomerID"].isin(seg_uids)]
    seg_rfm = rfm[rfm["Segment"] == seg_name]
    n_users = len(seg_uids)
    total_sales = seg_df["Amount"].sum()
    avg_r = seg_rfm["R"].mean()
    avg_f = seg_rfm["F"].mean()
    avg_m = seg_rfm["M"].mean()
    avg_order_val = total_sales / seg_df["InvoiceNo"].nunique() if seg_df["InvoiceNo"].nunique() else 0

    st.markdown(f'<p style="font-size:0.85rem;color:#94a3b8;margin-bottom:8px;">当前分层：{seg_name}</p>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.metric("用户数", f"{n_users:,}")
    with c2: st.metric("销售额", f"{total_sales/1e6:.2f}M")
    with c3: st.metric("平均R", f"{avg_r:.0f}天")
    with c4: st.metric("平均F", f"{avg_f:.1f}次")
    with c5: st.metric("平均M", f"{avg_m:,.0f}")
    with c6: st.metric("客单价", f"{avg_order_val:,.2f}")

    # 金额分布直方图 + TOP5国家 两栏
    cl, cr = st.columns(2)
    with cl:
        amts = seg_df["Amount"].clip(upper=seg_df["Amount"].quantile(0.99))
        counts, edges = np.histogram(amts, bins=20)
        labels = [f"{edges[i]:.0f}" for i in range(20)]
        hist = (
            Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
            .add_xaxis(labels)
            .add_yaxis("频数", counts.tolist(), label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(
                           color=JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#a78bfa'},{offset:1,color:'#38bdf8'}])"),
                           border_radius=[6,6,0,0]))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(name="订单金额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8", rotate=45, font_size=7)),
                yaxis_opts=opts.AxisOpts(name="频数", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st.markdown('<p class="sub-title" style="font-size:0.85rem;">💰 消费金额分布</p>', unsafe_allow_html=True)
        render_pe(hist, height=280)
    with cr:
        top5_ctry = seg_df.groupby("Country")["Amount"].sum().sort_values(ascending=False).head(5)
        ctry_bar = (
            Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="280px"))
            .add_xaxis(top5_ctry.index.tolist())
            .add_yaxis("销售额", top5_ctry.values.round(2).tolist(),
                       label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(
                           color=JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#fbbf24'},{offset:1,color:'#fb7185'}])"),
                           border_radius=[6,6,0,0]))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30, color="#94a3b8")),
                yaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                         axislabel_opts=opts.LabelOpts(color="#94a3b8"), splitline_opts=opts.SplitLineOpts(is_show=False)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        st.markdown('<p class="sub-title" style="font-size:0.85rem;">🌍 TOP5 国家</p>', unsafe_allow_html=True)
        render_pe(ctry_bar, height=280)

    # TOP10 用户表
    st.markdown('<p class="sub-title" style="font-size:0.85rem;">👥 TOP10 用户</p>', unsafe_allow_html=True)
    top_users = seg_rfm.sort_values("M", ascending=False).head(10)
    show = top_users[["CustomerID","R","F","M","R_score","F_score","M_score"]].copy()
    show.columns = ["用户ID","R(天)","F(次)","M(元)","R分","F分","M分"]
    show = show.reset_index(drop=True)
    st.dataframe(show, use_container_width=True)


# ===== 色板 =====
_theme = CFG.get("theme", {})
PALETTE = _theme.get("palette", {}).get("colors", ['#a78bfa', '#f472b6', '#38bdf8', '#fbbf24', '#34d399', '#fb7185', '#60a5fa', '#c084fc'])

SEGMENT_COLORS = _theme.get("segment_colors", {
    "重要价值用户": "#a78bfa",
    "重要发展用户": "#38bdf8",
    "重要保持用户": "#fbbf24",
    "重要挽留用户": "#fb7185",
    "一般价值用户": "#60a5fa",
    "一般发展用户": "#34d399",
    "一般保持用户": "#c084fc",
    "一般挽留用户": "#94a3b8",
})

LEGEND_NAME_MAP = {k: k[:4]+"..." for k in SEGMENT_COLORS}
REVERSE_LEGEND_MAP = {v: k for k, v in LEGEND_NAME_MAP.items()}
SEGMENT_ORDER = list(SEGMENT_COLORS.keys())


# ===== 图表构建函数 =====

def chart_monthly_trend(df):
    monthly = df.groupby("Month").agg(销售额=("Amount", "sum"), 订单数=("InvoiceNo", "nunique")).reset_index()
    months = monthly["Month"].tolist()
    return (
        Line(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="340px"))
        .add_xaxis(months)
        .add_yaxis("销售额", monthly["销售额"].round(2).tolist(),
                   yaxis_index=0, is_smooth=True, label_opts=opts.LabelOpts(is_show=False),
                   linestyle_opts=opts.LineStyleOpts(width=3, color="#a78bfa"),
                   itemstyle_opts=opts.ItemStyleOpts(color="#a78bfa"))
        .add_yaxis("订单数", monthly["订单数"].tolist(),
                   yaxis_index=1, is_smooth=True, label_opts=opts.LabelOpts(is_show=False),
                   linestyle_opts=opts.LineStyleOpts(width=3, color="#f472b6"),
                   itemstyle_opts=opts.ItemStyleOpts(color="#f472b6"))
        .extend_axis(yaxis=opts.AxisOpts(name="销售额", type_="value",
                     name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                     axislabel_opts=opts.LabelOpts(formatter="{value}"),
                     splitline_opts=opts.SplitLineOpts(is_show=False)))
        .extend_axis(yaxis=opts.AxisOpts(name="订单数", type_="value",
                     name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                     axislabel_opts=opts.LabelOpts(formatter="{value}"),
                     splitline_opts=opts.SplitLineOpts(is_show=False)))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, color="#94a3b8")),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#94a3b8"), is_show=True),
        )
    )


def chart_country_top10(df):
    country = df.groupby("Country").agg(销售额=("Amount", "sum")).sort_values("销售额", ascending=False).head(10)
    c = (
        Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="340px"))
        .add_xaxis(country.index.tolist())
        .add_yaxis("销售额", country["销售额"].round(2).tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(
                       color=JsCode("""
                           new echarts.graphic.LinearGradient(0,0,0,1,[
                               {offset:0, color:'#a78bfa'},
                               {offset:1, color:'#38bdf8'}
                           ])
                       """),
                       border_radius=[6,6,0,0]))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=35, color="#94a3b8")),
            yaxis_opts=opts.AxisOpts(name="销售额",
                     name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                     axislabel_opts=opts.LabelOpts(formatter="{value}"),
                     splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )
    return c


def chart_rfm_pie(rfm):
    seg_counts = rfm["Segment"].value_counts()
    data = [[k, int(seg_counts.get(k, 0))] for k in SEGMENT_ORDER if k in seg_counts.index]
    return (
        Pie(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="360px"))
        .add("", data, center=["50%", "55%"], radius=["45%", "75%"],
             label_opts=opts.LabelOpts(formatter="{b}\n{d}%", color="#94a3b8"),
             itemstyle_opts=opts.ItemStyleOpts(border_color="transparent", border_width=0))
        .set_colors([SEGMENT_COLORS.get(k, "#999") for k in [d[0] for d in data]])
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )


def chart_rfm_bar(rfm):
    agg = rfm.groupby("Segment").agg(用户数=("CustomerID", "nunique"), 销售额=("M", "sum")).reindex(SEGMENT_ORDER).fillna(0)
    segs = agg.index.tolist()
    scale = agg["用户数"].max() / agg["销售额"].max() if agg["销售额"].max() > 0 else 1
    return (
        Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="380px"))
        .add_xaxis(segs)
        .add_yaxis("用户数", agg["用户数"].astype(int).tolist(),
                   yaxis_index=0,
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(border_radius=[6,6,0,0]),
                   color=PALETTE[0])
        .add_yaxis("销售额", (agg["销售额"] * scale).round(2).tolist(),
                   yaxis_index=1,
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(border_radius=[6,6,0,0]),
                   color=PALETTE[1])
        .extend_axis(yaxis=opts.AxisOpts(name="用户数", type_="value",
                     name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                     axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                     splitline_opts=opts.SplitLineOpts(is_show=False)))
        .extend_axis(yaxis=opts.AxisOpts(name="销售额(缩放)", type_="value",
                     name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                     axislabel_opts=opts.LabelOpts(color="#94a3b8", formatter="{value}"),
                     splitline_opts=opts.SplitLineOpts(is_show=False)))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30, color="#94a3b8", font_size=10)),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#94a3b8")),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )


def chart_eda_hist(df):
    amounts = df["Amount"].clip(upper=df["Amount"].quantile(0.99))
    # 手动分箱
    n_bins = 30
    counts, edges = np.histogram(amounts, bins=n_bins)
    labels = [f"{edges[i]:.0f}-{edges[i+1]:.0f}" for i in range(n_bins)]
    return (
        Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="340px"))
        .add_xaxis(labels)
        .add_yaxis("频数", counts.tolist(), label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(
                       color=JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#a78bfa'},{offset:1,color:'#38bdf8'}])"),
                       border_radius=[6,6,0,0]))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="订单金额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8", font_size=8, rotate=45),
                                     splitline_opts=opts.SplitLineOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(name="频数", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                                     splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
        )
    )


def chart_eda_top10(df):
    top10 = df.groupby("Description").agg(销售额=("Amount", "sum")).sort_values("销售额", ascending=False).head(10)
    return (
        Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="340px"))
        .add_xaxis(top10.index.tolist()[::-1])
        .add_yaxis("销售额", top10["销售额"].round(2).tolist()[::-1],
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(
                       color=JsCode("new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f472b6'},{offset:1,color:'#fbbf24'}])"),
                       border_radius=[0,6,6,0]))
        .reversal_axis()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="销售额", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                                     splitline_opts=opts.SplitLineOpts(is_show=False)),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#94a3b8", font_size=10)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )


def chart_eda_heatmap(df):
    df = df.copy()
    df["Hour"] = df["InvoiceDate"].dt.hour
    df["Weekday"] = df["InvoiceDate"].dt.dayofweek
    wd_names = ["周一","周二","周三","周四","周五","周六","周日"]
    heat = df.groupby(["Weekday", "Hour"]).agg(订单数=("InvoiceNo", "nunique")).reset_index()
    hours = list(range(24))
    # 用 pivot 重建完整矩阵，缺失值填充为 0
    pivot = heat.pivot(index="Weekday", columns="Hour", values="订单数").reindex(index=range(7), columns=hours, fill_value=0)
    data = []
    for wi in range(7):
        for hi in hours:
            val = 0 if pd.isna(pivot.loc[wi, hi]) else int(pivot.loc[wi, hi])
            data.append([hi, wi, val])
    return (
        HeatMap(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="340px"))
        .add_xaxis(hours)
        .add_yaxis("", wd_names, data,
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(border_color="rgba(255,255,255,0.3)", border_width=1))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="小时", axislabel_opts=opts.LabelOpts(color="#94a3b8", font_size=9)),
            yaxis_opts=opts.AxisOpts(name="", axislabel_opts=opts.LabelOpts(color="#94a3b8", font_size=10)),
            visualmap_opts=opts.VisualMapOpts(
                min_=0,
                max_=max(v[2] for v in data) if data else 1,
                is_show=True,
                pos_right="5%",
                textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                range_color=["#f0f4ff", "#a78bfa", "#7c3aed"],
            ),
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter=JsCode("function(p){return p.value[2]+'单'}")),
            title_opts=opts.TitleOpts(title="", pos_left="center"),
        )
    )


def chart_eda_hour(df):
    hour = df.groupby(df["InvoiceDate"].dt.hour).agg(订单数=("InvoiceNo", "nunique")).reset_index()
    hour.columns = ["小时", "订单数"]
    return (
        Line(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="320px"))
        .add_xaxis(hour["小时"].tolist())
        .add_yaxis("订单数", hour["订单数"].tolist(), is_smooth=True, areastyle_opts=opts.AreaStyleOpts(opacity=0.25),
                   label_opts=opts.LabelOpts(is_show=False),
                   linestyle_opts=opts.LineStyleOpts(width=3, color="#38bdf8"),
                   itemstyle_opts=opts.ItemStyleOpts(color="#38bdf8"))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name="小时", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8")),
            yaxis_opts=opts.AxisOpts(name="订单数", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                                     splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )


def chart_eda_weekday(df):
    wd = df.groupby(df["InvoiceDate"].dt.dayofweek).agg(订单数=("InvoiceNo", "nunique")).reset_index()
    wd.columns = ["星期", "订单数"]
    days = ["周一","周二","周三","周四","周五","周六","周日"]
    wd["星期"] = wd["星期"].map(lambda x: days[int(x)])
    return (
        Bar(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="320px"))
        .add_xaxis(wd["星期"].tolist())
        .add_yaxis("订单数", wd["订单数"].tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   itemstyle_opts=opts.ItemStyleOpts(
                       color=JsCode("new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#fbbf24'},{offset:1,color:'#34d399'}])"),
                       border_radius=[6,6,0,0]))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color="#94a3b8")),
            yaxis_opts=opts.AxisOpts(name="订单数", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                     axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                                     splitline_opts=opts.SplitLineOpts(is_show=False)),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )


def chart_rfm_scatter(rfm):
    seg_list = SEGMENT_ORDER
    data_map = {s: [[], []] for s in seg_list}
    for _, row in rfm.iterrows():
        s = row["Segment"]
        if s in data_map:
            data_map[s][0].append(row["R"])
            data_map[s][1].append(row["M"])
    sc = Scatter(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="380px"))
    sc.add_xaxis([])
    for s in seg_list:
        if data_map[s][0]:
            sc.add_yaxis(LEGEND_NAME_MAP.get(s, s),
                         [list(z) for z in zip(data_map[s][0], data_map[s][1])],
                         color=SEGMENT_COLORS[s],
                         symbol_size=6, symbol="circle",
                         label_opts=opts.LabelOpts(is_show=False),
                         itemstyle_opts=opts.ItemStyleOpts(opacity=0.7))
    sc.set_global_opts(
        xaxis_opts=opts.AxisOpts(name="R (距最后购买天数)", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                 axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                                 splitline_opts=opts.SplitLineOpts(is_show=False)),
        yaxis_opts=opts.AxisOpts(name="M (累计消费)", name_textstyle_opts=opts.TextStyleOpts(color="#94a3b8"),
                                 axislabel_opts=opts.LabelOpts(color="#94a3b8"),
                                 splitline_opts=opts.SplitLineOpts(is_show=False)),
        legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color="#94a3b8", font_size=10),
                                    orient="vertical", pos_right="0%", pos_top="10%"),
        tooltip_opts=opts.TooltipOpts(trigger="item"),
        visualmap_opts=opts.VisualMapOpts(is_show=False),
    )
    return sc


def chart_rose(rfm):
    seg_counts = rfm["Segment"].value_counts()
    data = [[k, int(seg_counts.get(k, 0))] for k in SEGMENT_ORDER if k in seg_counts.index]
    return (
        Pie(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="380px"))
        .add("", data, center=["50%", "50%"], radius=["20%", "78%"], rosetype="area",
             label_opts=opts.LabelOpts(formatter="{b}\n{d}%", color="#94a3b8", font_size=10),
             itemstyle_opts=opts.ItemStyleOpts(border_color="transparent", border_width=0))
        .set_colors([SEGMENT_COLORS.get(k, "#999") for k in [d[0] for d in data]])
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    )


def chart_sankey(rfm):
    seg_counts = rfm["Segment"].value_counts()
    rfm["R_group"] = rfm["R_score"].apply(lambda x: _SL_HR if x >= _RFM_THR else _SL_LR)
    rfm["F_group"] = rfm["F_score"].apply(lambda x: _SL_HF if x >= _RFM_THR else _SL_LF)
    rfm["M_group"] = rfm["M_score"].apply(lambda x: _SL_HM if x >= _RFM_THR else _SL_LM)

    nodes = set()
    links = []
    for _, row in rfm.iterrows():
        srcs = [row["R_group"], row["F_group"], row["M_group"]]
        trg = row["Segment"]
        for s in srcs:
            nodes.add(s)
            nodes.add(trg)
            links.append((s, trg))

    node_list = list(nodes)
    node_idx = {n: i for i, n in enumerate(node_list)}
    link_agg = {}
    for s, t in links:
        key = (node_idx[s], node_idx[t])
        link_agg[key] = link_agg.get(key, 0) + 1

    return (
        Sankey(init_opts=opts.InitOpts(theme="white", bg_color="transparent", width="100%", height="400px"))
        .add("",
             [{"name": n} for n in node_list],
             [{"source": s, "target": t, "value": v} for (s, t), v in link_agg.items()],
             node_width=20, node_gap=12,
             pos_left="5%", pos_right="5%",
             linestyle_opt=opts.LineStyleOpts(opacity=0.3, curve=0.5, color="source"),
             label_opts=opts.LabelOpts(color="#94a3b8", font_size=10))
        .set_global_opts(tooltip_opts=opts.TooltipOpts(trigger="item"))
    )


# ===== 数据加载 =====
df = load_data()

# ===== 主界面 =====




with st.sidebar:
    st.markdown('<p class="sub-title" style="margin-bottom:20px;">⚙️ 控制面板</p>', unsafe_allow_html=True)

    # 背景选择器
    bg_options = list(BACKGROUNDS.keys())
    _ui_cfg = CFG.get("ui", {})
    bg_choice = st.selectbox("🎨 背景主题", bg_options, index=_ui_cfg.get("default_bg_index", 0))

    _dd = CFG.get("default_dates", {})
    start_date = st.date_input("开始日期", value=pd.to_datetime(_dd.get("start_date", "2010-12-01")))
    end_date   = st.date_input("结束日期", value=pd.to_datetime(_dd.get("end_date", "2011-12-09")))
    countries = st.sidebar.multiselect(
        "国家筛选",
        options=sorted(df["Country"].unique().tolist()),
        default=[],
        key="country_select"
    )

    seg_filter = st.multiselect("分层筛选", options=list(SEGMENT_COLORS.keys()), default=[], key="seg_filter_select")

    st.markdown("---")
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.75rem;text-align:center;">'
        + CFG.get("sidebar", {}).get("footer_html", 'Liquid Glass · 电商用户价值分析<br/>Powered by Streamlit + Pyecharts') +
        '</p>',
        unsafe_allow_html=True
    )


# ===== 背景层（必须在 main 区域注入，不能在 sidebar 里） =====
bg_file = BACKGROUNDS.get(bg_choice)
if bg_file:
    bg_url = _bg_to_data_url(bg_file)
    if bg_url:
        st.markdown(
            f"<div class=\"bg-layer\" style=\"background:url('{bg_url}') center/cover no-repeat fixed;\"></div>",
            unsafe_allow_html=True
        )
        # 暗色背景时文字改白
        st.markdown("""<style>
            .stApp { color: #f5f5f7 !important; }
            .glass-card {
                background: transparent !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border-color: rgba(255,255,255,0.12) !important;
                box-shadow: none !important;
            }
            .glass-card:hover {
                border-color: rgba(255,255,255,0.20) !important;
            }
            .kpi-card {
                background: transparent !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border-color: rgba(255,255,255,0.12) !important;
                box-shadow: none !important;
            }
            .kpi-card:hover {
                border-color: rgba(255,255,255,0.20) !important;
            }
            .kpi-label { color: rgba(255,255,255,0.6) !important; }
            .kpi-sub { color: rgba(255,255,255,0.25) !important; }
            .kpi-value { color: #fff !important; }
            .main-title { color: #fff !important; }
            .sub-title { color: rgba(255,255,255,0.9) !important; }
            .sub-title::before { background: linear-gradient(180deg, #5AC8FA, #007AFF) !important; }
            .seg-chip { color: rgba(255,255,255,0.85) !important; border-color: rgba(255,255,255,0.15) !important; }
            section[data-testid="stSidebar"] {
                background: transparent !important;
                backdrop-filter: none !important;
                border-right: 0.5px solid rgba(255,255,255,0.08) !important;
            }
            section[data-testid="stSidebar"] label,
            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] .stMarkdown p {
                color: #fff !important;
            }
            section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="input"],
            section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="input"] input,
            section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="single-value"],
            section[data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="placeholder"],
            section[data-testid="stSidebar"] [data-baseweb="select"] span,
            section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="input"],
            section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="input"] input,
            section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="single-value"],
            section[data-testid="stSidebar"] [data-baseweb="multiselect"] [data-baseweb="placeholder"],
            section[data-testid="stSidebar"] [data-baseweb="multiselect"] span {
                color: #fff !important;
            }
            .stTabs [data-baseweb="tab-list"] {
                background: transparent !important;
                border-color: rgba(255,255,255,0.08) !important;
            }
            .stTabs [data-baseweb="tab"] {
                color: rgba(255,255,255,0.5) !important;
            }
            .stTabs [data-baseweb="tab"]:hover {
                color: rgba(255,255,255,0.8) !important;
            }
            .stTabs [aria-selected="true"] {
                background: transparent !important;
                color: #fff !important;
            }
            .stTabs [data-baseweb="tab-panel"] {
                background: transparent !important;
                backdrop-filter: none !important;
                border: none !important;
                box-shadow: none !important;
                /* removed border: 1px solid rgba(255,255,255,0.06);
                box-shadow: none !important;
            }
            div[data-baseweb="select"] > div,
            div[data-baseweb="multiselect"] > div,
            div[data-testid="stDateInput"] > div > div {
                background: transparent !important;
                backdrop-filter: none !important;
                border: 1px solid rgba(255,255,255,0.12) !important;
                color: #fff !important;
                box-shadow: inset 0 1px 1px rgba(255,255,255,0.08) !important;
            }
            div[data-baseweb="select"] [data-baseweb="input"] input,
            div[data-baseweb="multiselect"] [data-baseweb="input"] input {
                color: #fff !important;
            }
            div[data-baseweb="select"] [data-baseweb="input"] svg,
            div[data-baseweb="multiselect"] [data-baseweb="input"] svg {
                fill: rgba(255,255,255,0.5) !important;
            }
            ul[data-baseweb="menu"] {
                background: rgba(30,30,35,0.92) !important;
                border-color: rgba(255,255,255,0.08) !important;
            }
            li[data-baseweb="menu-item"] { color: rgba(255,255,255,0.9) !important; }
            li[data-baseweb="menu-item"]:hover { background: rgba(255,255,255,0.08) !important; }
            th { background: transparent !important; color: rgba(255,255,255,0.9) !important; }
            .stDataFrame table { color: rgba(255,255,255,0.8) !important; }
            .stStatusWidget {
                background: rgba(255,255,255,0.08) !important;
                border-color: rgba(255,255,255,0.1) !important;
            }
            hr { background: rgba(255,255,255,0.1) !important; }
            ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); }
        
.stMarkdown > div[data-testid="stMarkdownContainer"],
.stHtml > div[data-testid="stHtmlContainer"] {
    background: transparent !important;
}
main .stMarkdown,
main .stHtml {
    background: transparent !important;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"],
div[data-testid="stColumns"] > div[data-testid="column"] {
    background: transparent !important;
}
</style>""", unsafe_allow_html=True)
else:
    st.markdown('<div class="bg-layer bg-default"></div>', unsafe_allow_html=True)



mask = (df["InvoiceDate"] >= pd.to_datetime(start_date)) & (df["InvoiceDate"] <= pd.to_datetime(end_date))
df_filtered = df[mask]
if countries:
    df_filtered = df_filtered[df_filtered["Country"].isin(countries)]

rfm = compute_rfm(df_filtered, str(end_date))
if seg_filter:
    rfm = rfm[rfm["Segment"].isin(seg_filter)]

total_revenue = df_filtered["Amount"].sum()
total_orders  = df_filtered["InvoiceNo"].nunique()
total_users   = df_filtered["CustomerID"].nunique()
avg_order     = total_revenue / total_orders if total_orders else 0




st.markdown(f'<p class="main-title" style="margin-bottom:4px;">📊 电商用户价值分析平台</p>', unsafe_allow_html=True)
st.markdown(f'<p style="color:#8e8e93;font-size:0.82rem;margin-bottom:18px;">数据范围：{start_date} ~ {end_date} | '
            f'国家：{len(countries) if countries else "全部"} | 分层：{len(seg_filter) if seg_filter else "全部"}</p>',
            unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="kpi-card"><p class="kpi-label">总销售额</p><p class="kpi-value">{total_revenue/1e6:,.2f}M</p><p class="kpi-sub">总销售额</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><p class="kpi-label">总订单数</p><p class="kpi-value">{total_orders:,}</p><p class="kpi-sub">总订单数</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><p class="kpi-label">用户数</p><p class="kpi-value">{total_users:,}</p><p class="kpi-sub">独立客户数</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="kpi-card"><p class="kpi-label">客单价</p><p class="kpi-value">{avg_order:,.2f}</p><p class="kpi-sub">平均客单价</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📈 经营概览", "🔍 EDA 探索", "🎯 RFM 分层", "📋 数据详情"])

with tab1:
    detail_monthly = _build_detail_monthly(df_filtered)
    detail_country = _build_detail_country(df_filtered)
    detail_rfm = _build_detail_rfm(rfm, df_filtered)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="glass-card"><p class="sub-title">📈 月度销售趋势</p>', unsafe_allow_html=True)
        render_pe(chart_monthly_trend(df_filtered), height=340, chart_id="monthly_trend", detail_html=detail_monthly)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="glass-card"><p class="sub-title">🌍 国家销售额 TOP10</p>', unsafe_allow_html=True)
        render_pe(chart_country_top10(df_filtered), height=340, chart_id="country_top10", detail_html=detail_country)
        st.markdown('</div>', unsafe_allow_html=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.markdown('<div class="glass-card"><p class="sub-title">🥧 RFM 用户分层占比</p>', unsafe_allow_html=True)
        render_pe(chart_rfm_pie(rfm), height=360, chart_id="rfm_pie", detail_html=detail_rfm)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r2:
        st.markdown('<div class="glass-card"><p class="sub-title">📊 各分层用户数与销售额</p>', unsafe_allow_html=True)
        render_pe(chart_rfm_bar(rfm), height=380, chart_id="rfm_bar", detail_html=detail_rfm)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="glass-card"><p class="sub-title">🛒 每单金额分布</p>', unsafe_allow_html=True)
        render_pe(chart_eda_hist(df_filtered), height=340)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="glass-card"><p class="sub-title">🏆 热销商品 TOP10</p>', unsafe_allow_html=True)
        render_pe(chart_eda_top10(df_filtered), height=340)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><p class="sub-title">🔥 月度销售热力图</p>', unsafe_allow_html=True)
    render_pe(chart_eda_heatmap(df_filtered), height=340)
    st.markdown('</div>', unsafe_allow_html=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="glass-card"><p class="sub-title">⏰ 小时订单分布</p>', unsafe_allow_html=True)
        render_pe(chart_eda_hour(df_filtered), height=320)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_d:
        st.markdown('<div class="glass-card"><p class="sub-title">📅 星期订单分布</p>', unsafe_allow_html=True)
        render_pe(chart_eda_weekday(df_filtered), height=320)
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown('<div class="glass-card"><p class="sub-title">🔵 RFM 三维散点图</p>', unsafe_allow_html=True)
        render_pe(chart_rfm_scatter(rfm), height=380)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_f:
        st.markdown('<div class="glass-card"><p class="sub-title">🥧 分层占比</p>', unsafe_allow_html=True)
        render_pe(chart_rose(rfm), height=380)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><p class="sub-title">🌊 RFM 分层桑基图</p>', unsafe_allow_html=True)
    render_pe(chart_sankey(rfm), height=400)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><p class="sub-title">📋 分层用户明细</p>', unsafe_allow_html=True)
    drill_seg = st.selectbox("选择分层", options=SEGMENT_ORDER, key="drill", label_visibility="collapsed")
    drill_df = rfm[rfm["Segment"] == drill_seg].sort_values("M", ascending=False).head(50)
    drill_show = drill_df[["CustomerID", "R", "F", "M", "R_score", "F_score", "M_score"]].copy()
    drill_show.columns = ["用户ID", "R(天)", "F(次)", "M(元)", "R分", "F分", "M分"]
    st.dataframe(drill_show, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="glass-card" style="margin-bottom:16px;"><p class="sub-title" style="color:#007AFF;">📋 字段说明</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    fields = [
        ("InvoiceNo", "发票编号"), ("StockCode", "商品编码"), ("Description", "商品描述"),
        ("Quantity", "购买数量"), ("InvoiceDate", "发票日期"), ("UnitPrice", "单价"),
        ("CustomerID", "客户ID"), ("Country", "国家"),
    ]
    for i, (f, d) in enumerate(fields):
        with cols[i % 4]:
            st.markdown(f'<strong style="color:#fff;">{f}</strong><br><span style="color:#94a3b8;font-size:13px">{d}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="margin-bottom:16px;margin-top:12px;"><p class="sub-title">📄 数据样本（前50行）</p>', unsafe_allow_html=True)
    st.dataframe(df_filtered.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="margin-top:12px;"><p class="sub-title" style="color:#007AFF;">🔍 数据质量报告</p>', unsafe_allow_html=True)
    nulls = df_filtered.isnull().sum()
    nulls = nulls[nulls > 0]
    items = [
        ("总行数", f"{len(df_filtered):,}"),
        ("总列数", str(len(df_filtered.columns))),
        ("缺失值列数", str(len(nulls))),
        ("日期范围", f"{df_filtered['InvoiceDate'].min()} ~ {df_filtered['InvoiceDate'].max()}"),
    ]
    if len(nulls):
        items.append(("缺失值详情", nulls.to_string()))
    else:
        items.append(("状态", "✅ 无缺失值"))

    cards_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:8px;">'
    for label, val in items:
        cards_html += f'''<div style="flex:1 1 160px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:10px;padding:12px 16px;">
<div style="color:#94a3b8;font-size:12px;margin-bottom:4px;">{label}</div>
<div style="color:#fff;font-size:15px;font-weight:600;word-break:break-all;">{val}</div>
</div>'''
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
