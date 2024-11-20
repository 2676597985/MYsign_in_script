from urllib.parse import urlencode

import requests
import json
import schedule
import time
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义签到请求的URL
base_url = "http://www.ufokc.com/sign-in-management-system-back/index.php?r=sign/WxSign"

# 定义签到参数模板
params_template = {
    'sr_id': '',
    'name': '梁嘉翘',
    'code': '20220739029',
    'week': '',
    'type': '正常签到',
    's_type': '课程',
}

# 定义请求头
headers = {
    "Host": "www.ufokc.com",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip,compress,br,deflate",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.53(0x18003531) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wx694dda7a5f554038/17/page-frame.html"
}

# 当前周数
current_week = 12

# 计算下周一的日期
next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)

# 定义签到任务
sign_in_tasks = {
    'Monday': [
        {'sr_id': '469441', 'time': '10:11'}
    ],
    'Tuesday': [
        {'sr_id': '337860', 'time': '10:11'},
        {'sr_id': '338988', 'time': '16:01'},
        {'sr_id': '346556', 'time': '18:51'}
    ],
    'Wednesday': [
        {'sr_id': '337869', 'time': '10:11'}
    ],
    'Thursday': [
        {'sr_id': '363626', 'time': '08:21'},
        {'sr_id': '338995', 'time': '10:11'}
    ],
    'Friday': [
        {'sr_id': '328221', 'time': '08:21'},
        {'sr_id': '468709', 'time': '10:11'}
    ]
}


# 定义签到函数
def sign_in(sr_id, week):
    params = params_template.copy()
    params['sr_id'] = sr_id
    params['week'] = str(week)
    encoded_params = urlencode(params)
    sign_url = f"{base_url}&{encoded_params}"
    response = requests.get(sign_url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            logging.info(f"签到成功，返回的数据为：{json.dumps(data, ensure_ascii=False, indent=4)}")
        except json.JSONDecodeError as e:
            logging.error(f"签到失败，无法解析JSON响应：{e}")
            logging.error(f"响应内容：{response.text}")
    else:
        logging.error(f"签到失败，状态码：{response.status_code}")
        logging.error(f"响应内容：{response.text}")


# 设置定时任务
def schedule_sign_in():
    for day, tasks in sign_in_tasks.items():
        for task in tasks:
            time_str = task['time']
            try:
                # 验证时间格式
                datetime.strptime(time_str, '%H:%M')
                if day == 'Monday':
                    schedule.every().monday.at(time_str).do(sign_in, task['sr_id'], current_week)
                elif day == 'Tuesday':
                    schedule.every().tuesday.at(time_str).do(sign_in, task['sr_id'], current_week)
                elif day == 'Wednesday':
                    schedule.every().wednesday.at(time_str).do(sign_in, task['sr_id'], current_week)
                elif day == 'Thursday':
                    schedule.every().thursday.at(time_str).do(sign_in, task['sr_id'], current_week)
                elif day == 'Friday':
                    schedule.every().friday.at(time_str).do(sign_in, task['sr_id'], current_week)
            except ValueError:
                logging.error(f"无效的时间格式：{time_str}")


# 更新周数
def update_week():
    global current_week
    current_week += 1
    logging.info(f"更新周数为 {current_week}")
    schedule.clear()  # 清除所有任务
    schedule_sign_in()  # 重新设置任务


# 主循环
if __name__ == "__main__":
    schedule_sign_in()
    while True:
        now = datetime.now()
        if now >= next_monday:
            next_monday += timedelta(days=7)
            update_week()
        schedule.run_pending()
        time.sleep(1)