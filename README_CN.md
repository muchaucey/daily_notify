# 中远海控PB值监控程序

这是一个Python程序，用于监控中远海控的PB值，当PB值小于1时自动发邮件通知。

## 功能介绍

- 实时获取中远海控（股票代码：601919）的PB值
- 当PB值低于1倍时自动发送邮件告警
- 支持定时检查（可配置检查频率）
- 支持多种邮箱服务商（QQ、163、Gmail等）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 配置邮箱信息

编辑 `config.py` 文件，填入你的邮箱信息：

#### QQ邮箱配置（推荐）

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.qq.com',
    'smtp_port': 465,
    'sender_email': 'your_email@qq.com',
    'sender_password': 'your_app_password',  # 授权密码
    'receiver_email': 'receiver@example.com'
}
```

**QQ邮箱授权密码获取步骤：**

1. 登录QQ邮箱：https://mail.qq.com
2. 点击右上角设置 → 账户
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 点击"生成授权码"
5. 按照提示生成16位授权码
6. 在配置中使用这个授权码作为 `sender_password`

#### Gmail配置

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password',
    'receiver_email': 'receiver@example.com'
}
```

#### 163邮箱配置

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.163.com',
    'smtp_port': 465,
    'sender_email': 'your_email@163.com',
    'sender_password': 'your_app_password',
    'receiver_email': 'receiver@example.com'
}
```

## 使用方式

### 方式1：运行一次检查

```bash
python pb_monitor.py
```

这会立即检查一次中远海控的PB值，如果小于1则发送邮件。

### 方式2：定时检查（推荐）

```bash
python scheduler.py
```

程序会每5分钟检查一次PB值，如果小于1则发送邮件。可以在 `scheduler.py` 中修改检查间隔。

#### 修改检查频率

编辑 `scheduler.py`，修改最后一行：

```python
# 设置每N分钟检查一次（将数字改为你想要的分钟数）
start_scheduler(check_interval=5)  # 默认5分钟
```

### 方式3：Windows计划任务（后台运行）

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（如：每天上午9点）
4. 设置操作：
   - 程序/脚本: `python.exe` 的完整路径
   - 添加参数: `C:\path\to\scheduler.py`
   - 起始于: 脚本所在目录

## 程序文件说明

- **pb_monitor.py**: 核心监控程序，包含获取PB值和发送邮件的逻辑
- **scheduler.py**: 定时执行脚本，可设置检查间隔
- **config.py**: 邮箱配置文件，需要填入你的邮箱信息
- **requirements.txt**: 依赖包列表

## 常见问题

### 1. 提示"获取数据失败"

- 检查网络连接是否正常
- 可能是接口变更，可以尝试手动访问 `https://qt.gtimg.cn/q=sh601919` 测试

### 2. 发送邮件失败

- 检查邮箱配置信息是否正确
- 确认使用的是"授权密码"而不是登录密码
- 检查防火墙是否阻止了SMTP连接
- 尝试使用其他邮箱服务商

### 3. 如何只发送一次邮件？

修改 `scheduler.py` 的最后几行：

```python
if __name__ == '__main__':
    monitor = PBMonitor()
    monitor.check_and_notify()
```

### 4. 如何修改发送的邮件内容？

编辑 `pb_monitor.py` 中的 `send_email()` 方法，修改邮件标题和内容。

## 注意事项

- ⚠️ 不要将 `config.py` 上传到公开的代码仓库，避免泄露邮箱密码
- 邮箱授权码是安全的，即使泄露也可以在邮箱设置中删除
- 建议在 `.gitignore` 中添加 `config.py`

## 许可证

MIT

## 支持

如有问题，请检查以上常见问题或查阅相关文档。
