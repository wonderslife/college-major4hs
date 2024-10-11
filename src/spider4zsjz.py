import json
import logging
import time
import openpyxl
import os
import qianfan
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from datetime import datetime

#### 爬取招生简章，并用大模型规模归纳总结，按学校保存

logging.basicConfig(level=logging.INFO)

# 初始化浏览器驱动
driver = webdriver.Chrome()

# 打开 Excel 文件
wb = openpyxl.load_workbook('教育部\yangguanggaokao_20241003.xlsx')
ws = wb.active


# 循环读取 sclink 字段的值并打开链接

for index,row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
    # qianfan每25个随机休息2-10秒
    if index % 25 == 0:
        sleep_time = random.randint(2, 10)
        logging.info(f'正在休息 {sleep_time} 秒')
        time.sleep(sleep_time)
    sclink = row[5]
    name = row[0]
    logging.info(f"正在解析 {name} 的招生简章，明细链接:{sclink}")
    if sclink:
        # 在这里可以进行对打开页面的操作
        #driver.get(sclink)
        scid = sclink.split("/")[-1].split("--")[1]
        zsjz_link = "https://gaokao.chsi.com.cn/zsgs/zhangcheng/listZszc--"+scid
        logging.info(f'正在解析 {zsjz_link} 的招生简章')
        
        driver.get(zsjz_link)
        
        driver.set_window_size(1552, 832)
        time.sleep(1)
        try:
            zszc_link = driver.find_element(By.CSS_SELECTOR,"a.zszc-zc-title").get_attribute("href")
        except NoSuchElementException:
            continue
        driver.get(zszc_link)
        time.sleep(1)
        page_text = driver.find_element(By.TAG_NAME,"body").text

    # 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk，如何获取请查看https://cloud.baidu.com/doc/Reference/s/9jwvz2egb
        os.environ["QIANFAN_ACCESS_KEY"] = "cd8b9ae5abc748c7a69066ab5c264376"
        os.environ["QIANFAN_SECRET_KEY"] = "e384b45b9d974721a0f5d1c1e3dd22ab"

        chat_comp = qianfan.ChatCompletion()

        prompt = "你是一个经验丰富的归纳者,请用300字突出其中的关键信息,包括报考、招生、录取、体检、收费、毕业、就业、其他要求等内容:"

    # 指定特定模型
        resp = chat_comp.do(model="ERNIE-Speed-128K", messages=[{
            "role": "user",
            "content": prompt+page_text
        }])
    
        digest_text = resp["body"].get("result") 

        zsjz_detail = {
            "schoolName": name,
            "zsjz_link" : zsjz_link,
            "zsjz_digest" : digest_text
        }

        current_date = datetime.now().strftime('%Y%m%d')
        with open(f'C:\\Users\\wonder\\Documents\\college-major4hs\\教育部\\school_detail\\{name}-2-{current_date}.json', 'w', encoding='utf-8') as json_file:
            json.dump(zsjz_detail, json_file, ensure_ascii=False, indent=4)

# 关闭浏览器
driver.quit()
### 循环高校名单，获取明细，获取招生简章链接，获取链接中的第一个招生简章


### 读取招生简章，然后用大模型归纳，将归纳的结果记录到json文件中