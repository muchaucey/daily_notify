#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ==================== 配置区域 ====================
SMTP_SERVER = 'xxx'
SMTP_PORT = 465
SENDER_EMAIL = 'xxx'
SENDER_PASSWORD = 'xxx'
RECEIVER_EMAIL = 'xxx'
PB_THRESHOLD = 1.2  # 阈值
STOCK_CODE = "601919"  # 中远海控
# ================================================

class PBMonitor:
    def __init__(self):
        # f57:代码, f58:名称, f43:最新价, f167:PB
        self.url = f"https://push2.eastmoney.com/api/qt/stock/get?secid=1.{STOCK_CODE}&fields=f57,f58,f43,f167"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        }

    def get_data(self):
        """获取并解析PB数据"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            
            if not json_data or 'data' not in json_data or json_data['data'] is None:
                print("Error: 接口返回数据为空")
                return None
            
            data = json_data['data']
            
            raw_pb = data.get('f167')
            raw_price = data.get('f43')
            name = data.get('f58', '未知股票')

            if raw_pb == "-" or raw_price == "-":
                print("Error: 数据字段为 '-' (可能处于竞价阶段或停牌)")
                return None

            # =========== 核心修正区域 ===========
            # 根据日志：1446.0 -> 14.46，96.0 -> 0.96
            # 必须除以 100 还原真实数值
            price_value = float(raw_price) / 100.0
            pb_value = float(raw_pb) / 100.0
            # ====================================

            return {
                'name': name,
                'price': price_value,
                'pb': pb_value
            }
        except Exception as e:
            print(f"请求过程中出现异常: {str(e)}")
            return None

    def send_email(self, pb, name, price):
        """发送报警邮件"""
        try:
            subject = f"【告警】{name} PB值：{pb:.2f}"
            content = (f"监测对象：{name} ({STOCK_CODE})\n"
                       f"当前股价：{price:.2f}\n"
                       f"当前 PB ：{pb:.2f}\n"
                       f"触发阈值：低于 {PB_THRESHOLD}")
            
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            print(f"通知邮件已发送！当前PB: {pb:.2f}")
        except Exception as e:
            print(f"邮件发送失败: {e}")

    def run(self):
        print(f"--- 启动监控: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        result = self.get_data()
        
        if result:
            pb = result['pb']
            name = result['name']
            price = result['price']
            print(f"成功获取数据 -> 股票: {name}, 现价: {price:.2f}, PB: {pb:.2f}")
            
            if pb < PB_THRESHOLD:
                print("触发阈值，正在发送邮件...")
                self.send_email(pb, name, price)
            else:
                print(f"当前 PB {pb:.2f} 高于阈值 {PB_THRESHOLD}，未触发告警。")
        else:
            print("未能成功获取 PB 数据。")

if __name__ == '__main__':
    PBMonitor().run()