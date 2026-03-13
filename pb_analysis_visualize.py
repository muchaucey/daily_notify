#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PB值分析结果可视化脚本
将分析结果用图表展示出来
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import matplotlib.font_manager as fm

# 设置中文字体 - 尝试多个字体配置
import matplotlib.font_manager as fm

# 获取系统中可用的中文字体
try:
    # Windows系统常见中文字体
    font_paths = [
        'C:\\Windows\\Fonts\\SimHei.ttf',      # 黑体
        'C:\\Windows\\Fonts\\msyh.ttc',        # 微软雅黑
        'C:\\Windows\\Fonts\\SimSun.ttc',      # 宋体
    ]
    
    font_name = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            # 获取字体名称
            font = fm.FontProperties(fname=font_path)
            font_name = font.get_name()
            break
    
    if font_name:
        plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
    else:
        # 备用方案：使用系统默认中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
except:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False

# ==================== 配置区域 ====================
INPUT_CSV = "pb_analysis_result.csv"
OUTPUT_DIR = "pb_analysis_charts"
# ================================================

class PBVisualizer:
    def __init__(self, csv_file):
        """初始化可视化工具"""
        self.csv_file = csv_file
        self.df = None
        
        # 创建输出目录
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"✓ 创建输出目录: {OUTPUT_DIR}")
    
    def load_data(self):
        """加载CSV数据"""
        print(f"[加载数据] 读取 {self.csv_file}...")
        try:
            self.df = pd.read_csv(self.csv_file)
            self.df['日期'] = pd.to_datetime(self.df['日期'])
            print(f"✓ 成功加载 {len(self.df)} 条数据")
            return True
        except Exception as e:
            print(f"❌ 加载数据失败: {str(e)}")
            return False
    
    def plot_price_trend(self):
        """绘制股价走势图"""
        print("[绘图] 生成股价走势图...")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(self.df['日期'], self.df['收盘价'], label='收盘价', 
                linewidth=2, color='#1f77b4', marker='o', markersize=2, alpha=0.8)
        ax.plot(self.df['日期'], self.df['收盘价_MA5'], label='5日均线', 
                linewidth=1.5, color='#ff7f0e', linestyle='--', alpha=0.7)
        ax.plot(self.df['日期'], self.df['收盘价_MA20'], label='20日均线', 
                linewidth=1.5, color='#2ca02c', linestyle='--', alpha=0.7)
        ax.plot(self.df['日期'], self.df['收盘价_MA50'], label='50日均线', 
                linewidth=1.5, color='#d62728', linestyle='--', alpha=0.7)
        
        ax.set_xlabel('日期', fontsize=12, fontweight='bold')
        ax.set_ylabel('股价 (元)', fontsize=12, fontweight='bold')
        ax.set_title('中国移动(601728) - 股价走势与移动平均线', 
                     fontsize=14, fontweight='bold', pad=20)
        
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 日期格式化
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_file = os.path.join(OUTPUT_DIR, '01_股价走势.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_file}")
        plt.close()
    
    def plot_volume_trend(self):
        """绘制成交量走势图"""
        print("[绘图] 生成成交量走势图...")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 根据涨跌幅着色
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in self.df['涨跌幅(%)']]
        
        ax.bar(self.df['日期'], self.df['成交量'], color=colors, alpha=0.6, width=0.6)
        
        ax.set_xlabel('日期', fontsize=12, fontweight='bold')
        ax.set_ylabel('成交量 (股)', fontsize=12, fontweight='bold')
        ax.set_title('中国移动(601728) - 成交量走势 (红=下跌, 绿=上涨)', 
                     fontsize=14, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 日期格式化
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_file = os.path.join(OUTPUT_DIR, '02_成交量走势.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_file}")
        plt.close()
    
    def plot_daily_return(self):
        """绘制日涨跌幅分布"""
        print("[绘图] 生成日涨跌幅分布图...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 左图：时间序列
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in self.df['涨跌幅(%)']]
        ax1.bar(self.df['日期'], self.df['涨跌幅(%)'], color=colors, alpha=0.6, width=0.6)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax1.set_xlabel('日期', fontsize=11, fontweight='bold')
        ax1.set_ylabel('涨跌幅 (%)', fontsize=11, fontweight='bold')
        ax1.set_title('日涨跌幅走势', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 右图：直方图分布
        ax2.hist(self.df['涨跌幅(%)'].dropna(), bins=50, color='#1f77b4', alpha=0.7, edgecolor='black')
        ax2.axvline(x=self.df['涨跌幅(%)'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'平均: {self.df["涨跌幅(%)"].mean():.4f}%')
        ax2.set_xlabel('涨跌幅 (%)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('频数', fontsize=11, fontweight='bold')
        ax2.set_title('日涨跌幅分布', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        fig.suptitle('中国移动(601728) - 日涨跌幅分析', 
                    fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        output_file = os.path.join(OUTPUT_DIR, '03_日涨跌幅分布.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_file}")
        plt.close()
    
    def plot_volatility(self):
        """绘制波动率分析"""
        print("[绘图] 生成波动率分析图...")
        
        # 计算各种周期的波动率
        self.df['波动率_5日'] = self.df['涨跌幅(%)'].rolling(window=5).std()
        self.df['波动率_20日'] = self.df['涨跌幅(%)'].rolling(window=20).std()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(self.df['日期'], self.df['波动率_5日'], label='5日波动率', 
                linewidth=1.5, color='#1f77b4', alpha=0.8)
        ax.plot(self.df['日期'], self.df['波动率_20日'], label='20日波动率', 
                linewidth=1.5, color='#ff7f0e', alpha=0.8)
        
        ax.fill_between(self.df['日期'], self.df['波动率_5日'], alpha=0.2, color='#1f77b4')
        ax.fill_between(self.df['日期'], self.df['波动率_20日'], alpha=0.2, color='#ff7f0e')
        
        ax.set_xlabel('日期', fontsize=12, fontweight='bold')
        ax.set_ylabel('波动率 (%)', fontsize=12, fontweight='bold')
        ax.set_title('中国移动(601728) - 股价波动率走势', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.legend(loc='best', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_file = os.path.join(OUTPUT_DIR, '04_波动率分析.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_file}")
        plt.close()
    
    def plot_price_distribution(self):
        """绘制价格分布分析"""
        print("[绘图] 生成价格分布分析图...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('中国移动(601728) - 价格分布分析', 
                    fontsize=14, fontweight='bold', y=0.995)
        
        # 1. 价格分布直方图
        axes[0, 0].hist(self.df['收盘价'], bins=40, color='#1f77b4', alpha=0.7, edgecolor='black')
        axes[0, 0].axvline(self.df['收盘价'].mean(), color='red', linestyle='--', 
                          linewidth=2, label=f'均值: {self.df["收盘价"].mean():.2f}')
        axes[0, 0].axvline(self.df['收盘价'].median(), color='green', linestyle='--', 
                          linewidth=2, label=f'中位数: {self.df["收盘价"].median():.2f}')
        axes[0, 0].set_xlabel('收盘价 (元)', fontweight='bold')
        axes[0, 0].set_ylabel('频数', fontweight='bold')
        axes[0, 0].set_title('收盘价分布', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2. 价格箱线图 (按月份)
        self.df['月份'] = self.df['日期'].dt.to_period('M').astype(str)
        price_by_month = [self.df[self.df['月份'] == month]['收盘价'].values 
                         for month in self.df['月份'].unique()[-10:]]
        bp = axes[0, 1].boxplot(price_by_month, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('#ff7f0e')
        axes[0, 1].set_ylabel('收盘价 (元)', fontweight='bold')
        axes[0, 1].set_title('近10月价格箱线图', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        plt.setp(axes[0, 1].xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
        
        # 3. 最高价、最低价、收盘价比较
        axes[1, 0].plot(self.df['日期'], self.df['最高价'], label='最高价', 
                       linewidth=1, color='#d62728', alpha=0.7)
        axes[1, 0].plot(self.df['日期'], self.df['收盘价'], label='收盘价', 
                       linewidth=1.5, color='#1f77b4', alpha=0.8)
        axes[1, 0].plot(self.df['日期'], self.df['最低价'], label='最低价', 
                       linewidth=1, color='#2ca02c', alpha=0.7)
        axes[1, 0].fill_between(self.df['日期'], self.df['最高价'], self.df['最低价'], 
                               alpha=0.1, color='gray')
        axes[1, 0].set_xlabel('日期', fontweight='bold')
        axes[1, 0].set_ylabel('价格 (元)', fontweight='bold')
        axes[1, 0].set_title('最高价/收盘价/最低价对比', fontweight='bold')
        axes[1, 0].legend(fontsize=9)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        
        # 4. 统计信息
        stats_text = f"""
收盘价统计:
  最高价: ¥{self.df['收盘价'].max():.2f}
  最低价: ¥{self.df['收盘价'].min():.2f}
  平均价: ¥{self.df['收盘价'].mean():.2f}
  当前价: ¥{self.df['收盘价'].iloc[-1]:.2f}
  
成交量统计 (万股):
  最高: {self.df['成交量'].max()/1e4:.1f}
  最低: {self.df['成交量'].min()/1e4:.1f}
  平均: {self.df['成交量'].mean()/1e4:.1f}
  
涨跌幅统计:
  平均: {self.df['涨跌幅(%)'].mean():.4f}%
  标准差: {self.df['涨跌幅(%)'].std():.4f}%
  最高涨幅: {self.df['涨跌幅(%)'].max():.2f}%
  最大跌幅: {self.df['涨跌幅(%)'].min():.2f}%
        """
        
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center',
                       family='sans-serif', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        output_file = os.path.join(OUTPUT_DIR, '05_价格分布分析.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_file}")
        plt.close()
    
    def plot_monthly_return(self):
        """绘制月度收益率分析"""
        print("[绘图] 生成月度收益率分析图...")
        
        self.df['月份'] = self.df['日期'].dt.to_period('M')
        monthly_data = []
        
        for month in self.df['月份'].unique():
            month_df = self.df[self.df['月份'] == month]
            if len(month_df) > 0:
                month_return = (month_df['收盘价'].iloc[-1] - month_df['收盘价'].iloc[0]) / month_df['收盘价'].iloc[0] * 100
                monthly_data.append({
                    '月份': str(month),
                    '月度收益率': month_return
                })
        
        monthly_df = pd.DataFrame(monthly_data)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        colors = ['#2ca02c' if x >= 0 else '#d62728' for x in monthly_df['月度收益率']]
        ax.bar(range(len(monthly_df)), monthly_df['月度收益率'], color=colors, alpha=0.7, width=0.6)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        
        ax.set_xlabel('月份', fontsize=12, fontweight='bold')
        ax.set_ylabel('收益率 (%)', fontsize=12, fontweight='bold')
        ax.set_title('中国移动(601728) - 月度收益率走势', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xticks(range(len(monthly_df)))
        ax.set_xticklabels(monthly_df['月份'], rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for i, v in enumerate(monthly_df['月度收益率']):
            ax.text(i, v + (0.3 if v > 0 else -0.3), f'{v:.2f}%', 
                   ha='center', va='bottom' if v > 0 else 'top', fontsize=8)
        
        plt.tight_layout()
        output_file = os.path.join(OUTPUT_DIR, '06_月度收益率.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_file}")
        plt.close()
    
    def plot_summary_dashboard(self):
        """绘制总结面板"""
        print("[绘图] 生成总结面板...")
        
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle('中国移动(601728) - PB值分析总结面板', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
        
        # 1. 主要统计信息
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        latest_price = self.df['收盘价'].iloc[-1]
        price_change = latest_price - self.df['收盘价'].iloc[0]
        price_change_pct = price_change / self.df['收盘价'].iloc[0] * 100
        
        summary_text = f"""数据周期: {self.df['日期'].min().strftime('%Y-%m-%d')} ~ {self.df['日期'].max().strftime('%Y-%m-%d')}   |   数据样本: {len(self.df)}条   |   当前PB: {self.df['当前PB'].iloc[-1]:.2f}

当前股价: ¥{latest_price:.2f}   |   周期涨幅: {price_change_pct:+.2f}%   |   历史最高: ¥{self.df['收盘价'].max():.2f}   |   历史最低: ¥{self.df['收盘价'].min():.2f}"""
        
        ax1.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11, 
                family='sans-serif', transform=ax1.transAxes,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3, pad=1))
        
        # 2. 收盘价走势
        ax2 = fig.add_subplot(gs[1, :])
        ax2.plot(self.df['日期'], self.df['收盘价'], linewidth=2, color='#1f77b4', marker='o', markersize=2)
        ax2.fill_between(self.df['日期'], self.df['收盘价'], alpha=0.2, color='#1f77b4')
        ax2.set_ylabel('股价 (元)', fontweight='bold')
        ax2.set_title('股价走势', fontweight='bold', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        
        # 3. 成交量
        ax3 = fig.add_subplot(gs[2, 0])
        colors = ['#d62728' if x < 0 else '#2ca02c' for x in self.df['涨跌幅(%)']]
        ax3.bar(self.df['日期'], self.df['成交量']/1e8, color=colors, alpha=0.6, width=0.6)
        ax3.set_ylabel('成交量 (亿股)', fontweight='bold')
        ax3.set_title('成交量走势', fontweight='bold', fontsize=11)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        
        # 4. 日涨跌幅分布
        ax4 = fig.add_subplot(gs[2, 1])
        ax4.hist(self.df['涨跌幅(%)'].dropna(), bins=40, color='#1f77b4', alpha=0.7, edgecolor='black')
        ax4.axvline(self.df['涨跌幅(%)'].mean(), color='red', linestyle='--', linewidth=2)
        ax4.set_xlabel('涨跌幅 (%)', fontweight='bold')
        ax4.set_ylabel('频数', fontweight='bold')
        ax4.set_title('日涨跌幅分布', fontweight='bold', fontsize=11)
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.savefig(os.path.join(OUTPUT_DIR, '00_总结面板.png'), dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {os.path.join(OUTPUT_DIR, '00_总结面板.png')}")
        plt.close()
    
    def run(self):
        """运行完整的可视化流程"""
        print(f"\n{'='*60}")
        print(f"🎨 启动PB值分析可视化")
        print(f"{'='*60}\n")
        
        if not self.load_data():
            return False
        
        print(f"\n[开始绘图] 生成图表中...\n")
        
        self.plot_summary_dashboard()
        self.plot_price_trend()
        self.plot_volume_trend()
        self.plot_daily_return()
        self.plot_volatility()
        self.plot_price_distribution()
        self.plot_monthly_return()
        
        print(f"\n{'='*60}")
        print(f"✓ 所有图表已生成！")
        print(f"📁 输出目录: {OUTPUT_DIR}/")
        print(f"{'='*60}\n")
        
        return True


if __name__ == '__main__':
    visualizer = PBVisualizer(INPUT_CSV)
    visualizer.run()
