"""
邮件配置文件
"""

# QQ邮箱配置示例
EMAIL_CONFIG = {
    'smtp_server': 'smtp.qq.com',      # QQ邮箱SMTP服务器
    'smtp_port': 465,                   # QQ邮箱SMTP端口（SSL）
    'sender_email': 'your_email@qq.com',     # 发送人邮箱
    'sender_password': 'your_app_password',  # QQ邮箱授权密码（不是登录密码）
    'receiver_email': 'receiver@example.com' # 接收人邮箱
}

# Gmail配置示例（如需使用）
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp.gmail.com',
#     'smtp_port': 587,
#     'sender_email': 'your_email@gmail.com',
#     'sender_password': 'your_app_password',
#     'receiver_email': 'receiver@example.com'
# }

# 163邮箱配置示例（如需使用）
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp.163.com',
#     'smtp_port': 465,
#     'sender_email': 'your_email@163.com',
#     'sender_password': 'your_app_password',
#     'receiver_email': 'receiver@example.com'
# }
