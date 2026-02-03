import streamlit as st
import akshare as ak
import pandas as pd
import datetime
import plotly.express as px

# 页面配置
st.set_page_config(page_title="全球资产动量轮动策略", layout="wide")

# ===========================
# 1. 策略配置与标的池
# ===========================
st.sidebar.header("⚙️ 策略参数设置")

# 标的池定义 (代码需根据实际ETF代码调整，这里选取了流动性较好的代表)
ASSETS = {
    "159915": "创业板ETF",   # A股成长/科技
    "510300": "沪深300ETF",  # A股蓝筹/大盘
    "513100": "纳指100ETF",  # 美股科技 (QDII)
    "518880": "黄金ETF",     # 避险/大宗商品
    "511880": "银华日利"     # 货币/现金管理 (避险港湾)
}

# 现金/避险资产的代码
CASH_ASSET_CODE = "511880"

# 参数设置
lookback_period = st.sidebar.number_input(
    "动量回顾周期 (天)", 
    min_value=5, 
    max_value=250, 
    value=20, 
    step=1,
    help="计算过去多少天的收益率作为动量指标。常用：20天(月频)、60天(季频)。"
)

top_n = 1  # 动量策略通常只持有第1名

st.title("🚀 全球资产动量轮动策略看板")
st.markdown(f"**策略逻辑**：计算过去 **{lookback_period}个交易日** 的涨幅。持有排名第一的资产。如果排名第一的资产收益率为负，则切换至货币ETF。")

# ===========================
# 2. 数据获取函数 (使用缓存加速)
# ===========================
@st.cache_data(ttl=3600)  # 缓存1小时，避免频繁请求
def get_market_data(assets_dict, period_days):
    df_list = []
    
    # 获取当前日期和推算的起始日期（多取一些数据以确保计算准确）
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=period_days*2 + 30)).strftime("%Y%m%d")

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(assets_dict)
    count = 0

    for code, name in assets_dict.items():
        count += 1
        status_text.text(f"正在获取 {name} ({code}) 数据...")
        progress_bar.progress(count / total)
        
        try:
            # 使用 AkShare 获取 ETF 历史行情
            stock_data = ak.fund_etf_hist_em(symbol=code, period="daily", start_date=start_date, end_date=end_date)
            
            if stock_data.empty:
                continue

            # 整理数据
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data = stock_data.sort_values('日期')
            
            # 获取最新价格和N天前价格
            if len(stock_data) >= period_days:
                latest_price = stock_data.iloc[-1]['收盘']
                latest_date = stock_data.iloc[-1]['日期'].strftime("%Y-%m-%d")
                
                # N天前的价格 (用于计算动量)
                # 注意：实际交易中要防止由于停牌等导致的天数不对，这里做简化处理
                prev_price = stock_data.iloc[-1 - period_days]['收盘']
                
                # 计算收益率 (动量)
                momentum = (latest_price - prev_price) / prev_price * 100
                
                df_list.append({
                    "代码": code,
                    "名称": name,
                    "最新日期": latest_date,
                    "当前价格": latest_price,
                    f"{period_days}日涨幅(%)": round(momentum, 2),
                    "历史数据": stock_data  # 存入历史数据用于画图
                })
        except Exception as e:
            st.error(f"获取 {name} 数据失败: {e}")
            
    status_text.empty()
    progress_bar.empty()
    
    return pd.DataFrame(df_list)

# ===========================
# 3. 核心逻辑与展示
# ===========================

period_days = lookback_period  # 别名补丁，防止变量名不统一报错

if st.button("🔄 刷新数据 / 运行策略", type="primary"):
    df = get_market_data(ASSETS, lookback_period)

    if not df.empty:
        # 1. 排名
        df = df.sort_values(by=f"{period_days}日涨幅(%)", ascending=False).reset_index(drop=True)
        
        # 2. 策略判定
        top_asset = df.iloc[0]
        top_name = top_asset['名称']
        top_momentum = top_asset[f"{period_days}日涨幅(%)"]
        
        # 货币ETF的信息
        cash_row = df[df['代码'] == CASH_ASSET_CODE]
        cash_name = "货币ETF"
        if not cash_row.empty:
            cash_name = cash_row.iloc[0]['名称']

        st.divider()
        
        # === 信号展示区 ===
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📢 本期交易信号")
            
            # 逻辑判断：绝对动量检查
            # 如果第一名是货币ETF，或者第一名的涨幅 <= 0，则持有货币
            # 注意：如果货币ETF本身排第一，那自然买货币
            
            is_defensive = False
            final_target = top_name
            
            if top_momentum <= 0 and top_asset['代码'] != CASH_ASSET_CODE:
                is_defensive = True
                final_target = cash_name
                st.warning(f"⚠️ 警报：排名第一的 {top_name} 收益率为负 ({top_momentum}%)，触发绝对动量风控。")
                st.success(f"✅ **建议持仓：{final_target} ({CASH_ASSET_CODE})** [避险模式]")
            else:
                st.success(f"✅ **建议持仓：{final_target} ({top_asset['代码']})** [进攻模式]")
                st.info(f"理由：{top_name} 在过去 {lookback_period} 天表现最强，且趋势向上。")

        with col2:
            st.metric(label=f"当前最强 ({top_name}) 动量", value=f"{top_momentum}%")

        # === 排行榜表格 ===
        st.subheader("📊 资产动量排行榜")
        
        # 格式化显示，高亮前三名
        def highlight_top(s):
            is_max = s == s.max()
            return ['background-color: #d4edda' if v else '' for v in is_max]

        st.dataframe(
            df[["代码", "名称", "当前价格", f"{period_days}日涨幅(%)", "最新日期"]],
            use_container_width=True,
            hide_index=True
        )

        # === 可视化图表 ===
        st.subheader("📈 收益率走势对比 (归一化)")
        
        # 合并所有标的的历史数据进行绘图
        plot_df = pd.DataFrame()
        for index, row in df.iterrows():
            hist_data = row['历史数据']
            # 截取最近 N*2 天的数据画图
            display_days = lookback_period * 2
            subset = hist_data.tail(display_days).copy()
            # 归一化：让起点都变成 1
            start_price = subset.iloc[0]['收盘']
            subset['累计净值'] = subset['收盘'] / start_price
            subset['名称'] = row['名称']
            plot_df = pd.concat([plot_df, subset])

        fig = px.line(
            plot_df, 
            x='日期', 
            y='累计净值', 
            color='名称',
            title=f'过去 {lookback_period*2} 天各资产走势对比 (起点归一)',
            markers=False
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("未能获取数据，请检查网络或稍后再试。")

else:
    st.info("👈 请在左侧调整参数，并点击上方按钮开始分析。")

# 侧边栏说明
st.sidebar.markdown("---")
st.sidebar.markdown(
"""
### 💡 说明
1. **数据来源**：东方财富 (via AkShare)。
2. **纳指ETF**：因涉及QDII，数据可能比A股资产滞后一天。
3. **货币ETF**：作为风控锚点。当所有风险资产动量均小于0时，应切换至货币ETF。
""")