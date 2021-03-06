import re
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
import time
import pymysql
# 实现无可视化界面
from selenium.webdriver.chrome.options import Options
# 实现规避检测
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys


def set_option():
    """
    谷歌浏览器常规反反爬的参数设置
    """
    # 实现无可视化界面的操作
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # 实现规避检测
    option = ChromeOptions()
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    return chrome_options, option


if __name__ == '__main__':
    chrome_options, option = set_option()
    executable_path = "../chromedriver_win32/chromedriver.exe"

    # 连接database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='123456',
        database='infoVirus',
        port=3306,
        charset='utf8',
    )

    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    create_time = ''
    update_time = ''
    category_id = '1'
    success_count = 1
    # 让selenium规避被检测到的风险
    bro = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options, options=option)
    # 爬取的url主页
    bro.get(url='https://www.ncbi.nlm.nih.gov/gene/?term=virus')
    # 获取当前页源码数据
    page_text = bro.page_source
    index_page_tree = etree.HTML(page_text)

    all_page = int(index_page_tree.xpath('//*[@id="pageno2"]/@last')[0])

    init_url = "https://www.ncbi.nlm.nih.gov"

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }

    start_page = int(input("请输入开始页："))
    end_page = int(input("请输入结束页："))
    for page_num in range(start_page, end_page):
        # 模拟浏览器换页
        bro.find_element_by_id('pageno').click()
        bro.find_element_by_id('pageno').clear()
        bro.find_element_by_id('pageno').send_keys(page_num)
        bro.find_element_by_id('pageno').send_keys(Keys.ENTER)
        print("正在爬取第" + str(page_num) + "页。。。")
        # 获取当前页的源码页面
        cru_page = bro.page_source
        cru_page_text = etree.HTML(cru_page)
        tr_list = cru_page_text.xpath('//*[@id="ui-ncbigrid-7"]/tbody/tr')
        # 解析数据
        for tr in tr_list:
            virus_gene_name = tr.xpath('./td[1]/div[2]/a//text()')[0]
            virus_gene_id = str(tr.xpath('./td[1]/span//text()')[0])

            # 拼接url加上id
            detail_url = init_url + tr.xpath('.//a/@href')[0]
            response = requests.get(detail_url, headers=headers)  # 得到响应
            detail_page_text = response.text
            soup = BeautifulSoup(detail_page_text, 'lxml')
            title_div = soup.findAll(name="div", attrs={"class": re.compile("rprt-header")})
            summary_div = soup.findAll(name="div", attrs={"class": re.compile("rprt-section gene-summary")})
            content = str(title_div[0]) + str(summary_div[0])

            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            update_time = create_time
            # SQL 插入语句
            sql = "insert into info_virus (create_time, update_time, title, source, content, category_id) " \
                  "values (%s,%s,%s,%s,%s,%s)"
            # 执行SQL语句
            cursor.execute(sql, [create_time, update_time, virus_gene_name, virus_gene_id, content, category_id])
            # 提交事务
            conn.commit()
            print("插入第", success_count, "组数据成功！")
            success_count += 1
            # print("名称：" + virus_gene_name, virus_gene_id, "来源id：" + virus_gene_id + content)
            # input()
        print("爬取第" + str(page_num) + "页完成！")
        time.sleep(5)
    # 关闭数据库连接
    cursor.close()
    conn.close()
