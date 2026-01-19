"""
获取中远海控PB值监控程序
当PB值小于1时发邮件通知
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
from config import EMAIL_CONFIG


class PBMonitor:
    """PB值监控类"""
    
    def __init__(self):
        self.stock_code = "601919"  # 中远海控股票代码
        self.email_config = EMAIL_CONFIG
    
    def get_pb_value(self):
        """
        获取股票的PB值
        使用新浪财经或腾讯财经接口获取数据
        """
        try:
            # 尝试使用腾讯财经接口
            url = f"https://qt.gtimg.cn/q=sh{self.stock_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gb2312'
            
            # 解析腾讯财经返回的数据
            data = response.text
            
            # 腾讯接口格式: v_sh601919="公司名称~000~当前价~0~0~0...pb值..."
            if 'v_sh' in data:
                # 提取数据，pb值在倒数第二个字段
                parts = data.split('~')
                if len(parts) > 50:
                    pb_value = float(parts[49]) if parts[49] else None
                    stock_name = parts[1]
                    current_price = float(parts[3])
                    
                    return {
                        'status': 'success',
                        'name': stock_name,
                        'price': current_price,
                        'pb': pb_value
                    }
            
            # 备用方案：使用东方财富接口
            return self._get_pb_from_eastmoney()
            
        except Exception as e:
            print(f"获取PB值出错: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_pb_from_eastmoney(self):
        """从东方财富获取PB值"""
        try:
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                'fltt': '2',
                'invt': '2',
                'fields': 'f57,f58,f152',
                'secid': f'1.{self.stock_code}'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                pb_value = result.get('f152')  # PB值
                stock_name = result.get('f57')  # 股票名称
                
                return {
                    'status': 'success',
                    'name': stock_name,
                    'pb': pb_value
                }
        except Exception as e:
            print(f"从东方财富获取数据出错: {e}")
        
        return {
            'status': 'error',
            'message': '无法获取PB值'
        }
    
    def send_email(self, pb_value, stock_name):
        """
        发送邮件通知
        """
        try:
            # 创建邮件内容
            subject = f"【告警】中远海控 PB值低于1倍！当前PB值: {pb_value:.2f}"
            
            body = f"""
            <html>
                <body>
                    <p>股票监控告警通知</p>
                    <p>
                        <b>股票名称:</b> {stock_name}<br>
                        <b>股票代码:</b> {self.stock_code}<br>
                        <b>当前PB值:</b> <span style="color: red; font-weight: bold;">{pb_value:.2f}</span><br>
                        <b>检测时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    </p>
                    <p>
                        当前PB值已低于1倍，请关注股票动向！
                    </p>
                </body>
            </html>
            """
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP_SSL(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                server.login(
                    self.email_config['sender_email'],
                    self.email_config['sender_password']
                )
                server.send_message(msg)
            
            print(f"邮件已发送至 {self.email_config['receiver_email']}")
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
    
    def check_and_notify(self):
        """
        检查PB值并在需要时发送通知
        """
        print(f"开始检查中远海控PB值... [{datetime.now()}]")
        
        # 获取PB值
        result = self.get_pb_value()
        
        if result['status'] != 'success':
            print(f"获取数据失败: {result.get('message')}")
            return False
        
        pb_value = result.get('pb')
        stock_name = result.get('name', '中远海控')
        
        print(f"股票: {stock_name}")
        print(f"当前PB值: {pb_value}")
        
        # 判断是否需要发送邮件
        if pb_value and pb_value < 1.0:
            print(f"PB值 {pb_value} 小于1，准备发送邮件...")
            return self.send_email(pb_value, stock_name)
        else:
            print(f"PB值 {pb_value} 未低于1，无需发送邮件")
            return False


def main():
    """主函数"""
    monitor = PBMonitor()
    monitor.check_and_notify()


if __name__ == '__main__':
    main()
