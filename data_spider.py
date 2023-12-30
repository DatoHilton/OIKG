import urllib.request
import time

from fuzzywuzzy import fuzz
from selenium import webdriver
import json
import os
from selenium.webdriver.common.by import By
import http.client


def luogu_spider(url):
    driver = webdriver.Chrome()
    driver.implicitly_wait(1)
    driver.get(url)
    driver.refresh()

    res = []
    row = driver.find_elements(By.XPATH, "//div[@class='row']")
    names = driver.find_elements(By.XPATH, "//div[@class='title']/a")
    difficulties = driver.find_elements(By.XPATH, "//div[@class='difficulty']/a")
    rates = driver.find_elements(By.XPATH, "//div[@class='progress-frame has-tooltip']/div")

    num = len(names)
    for i in range(num):
        id, name, url, difficulty, rate = row[i].find_elements(By.XPATH, ".//span")[1].text, names[i].text, names[
            i].get_attribute("href"), difficulties[i].text, float(
            rates[i].get_attribute("style").split("width: ")[1].split("%")[0])
        # 爬来源
        source = {'source': '', 'year': '', 'pos': ''}
        sources = row[i].find_elements(By.XPATH, "./div[@class='tags']/div/a")
        for a in sources:
            span = a.find_element(By.XPATH, f".//span")
            rgb = span.get_attribute("style").split("rgb")[2][:-1]
            if rgb == '(19, 194, 194)':
                source['source'] = span.text
            elif rgb == '(82, 196, 26)':
                source['pos'] = span.text
            elif rgb == '(52, 152, 219)':
                source['year'] = span.text
        # 切换算法
        button = driver.find_element(By.XPATH, "//*[text()='显示算法']")
        button.click()
        # 爬算法
        algorithm = []
        algorithms = row[i].find_elements(By.XPATH, "./div[@class='tags']/div/a")
        for a in algorithms:
            span = a.find_element(By.XPATH, f".//span")
            algorithm.append(span.text)
        # 切换回来源
        button = driver.find_element(By.XPATH, "//*[text()='显示来源']")
        button.click()
        # print(id, name, url, source, algorithm, difficulty, rate)
        res.append({"id": id, "name": name, "url": url, "source": source, "algorithm": algorithm, "rate": rate})
    return res


def wiki_spider():
    wiki_url = "https://oi-wiki.org/"
    driver = webdriver.Chrome()
    driver.implicitly_wait(1)
    driver.get(wiki_url)
    driver.refresh()

    urls = []
    htmls = []

    # 先获取分类页面
    category_elements = driver.find_elements(By.XPATH, "//a[@class='md-nav__link']")
    for category_element in category_elements:
        urls.append(category_element.get_attribute('href'))
    driver.close()
    # print("-----get category finished-----")

    cnt = 0
    urls = urls[0:]  # *****************全部：[0:]    算法：[56:-1]*********************
    for url in urls:
        cnt += 1
        # 根据url，请求html
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        # 部分页过长，传输会切片，降级到HTTP/1.0
        http.client.HTTPConnection._http_vsn = 10
        http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = \
            res.read().decode('utf-8').split("<div class=md-content data-md-component=content>")[1].split(
                "</div></main>")[0]
        name = html.split('<h1>')[1].split('</h1>')[0]
        htmls.append([url, name, html.lower().replace('\n','').replace(' ','')])
        # print(f"-----get htmls {cnt}/{len(urls)}-----")
    # print("-----get htmls finished-----")

    return htmls


def spider_main():
    # """爬取洛谷"""
    # print("正在爬取洛谷...")
    # start_luogu = time.time()
    # if not os.path.exists('./data/'):
    #     os.makedirs('./data/')
    #
    # luogu_page_cnt = 0  # 爬取洛谷的页数
    # for page in range(1, 189):
    #     try:
    #         luogu_url = f"https://www.luogu.com.cn/problem/list?page={page}"
    #         data = luogu_spider(luogu_url)
    #
    #         # 逐个将爬取的数据保存为单独的JSON对象
    #         for item in data:
    #             with open('./data/luogu.json', 'a', encoding='utf-8') as f:
    #                 json.dump(item, f, ensure_ascii=False)
    #                 f.write('\n')  # 每个JSON对象后面添加一个换行符
    #         luogu_page_cnt += 1
    #     except Exception as e:
    #         print(e)
    #
    # end_luogu = time.time()
    # luogu_time = end_luogu - start_luogu
    # print(f"----------洛谷爬取完成！爬取{luogu_page_cnt}页，用时{int(luogu_time)}秒。----------")
    #
    # """从luogu.json中生成algorithm.dict，用于爬取oi-wiki"""
    # all_algorithms = set()
    # with open('data/luogu.json', 'r', encoding='utf-8') as file:
    #     for data in file:
    #         data_json = json.loads(data)
    #         algorithm = data_json.get('algorithm', [])
    #         all_algorithms.update(algorithm)
    #
    # # 去除空值
    # all_algorithms.discard('')
    #
    # # 将算法写入 algorithm.txt 文件
    # if not os.path.exists('dict'):
    #     os.makedirs('dict')
    # with open('dict/algorithm.txt', 'w', encoding='utf-8') as txt_file:
    #     for algorithm in all_algorithms:
    #         txt_file.write(f"{algorithm}\n")

    """爬取oi-wiki"""
    print("正在爬取oi-wiki...")
    spider_web = False  # 是否爬取oi-wiki的网页，如果已经爬过一次，有了./data/webs.txt就设置为False
    start_wiki = time.time()
    algorithm_dict_file = open('./dict/algorithm.txt', 'r', encoding='utf-8')
    algorithm_dict = algorithm_dict_file.readlines()
    algorithm_dict_file.close()
    if spider_web:
        res = wiki_spider()
        print("html爬取完成，准备根据算法匹配html")
        webs = open('./data/webs.txt', 'w', encoding='utf-8')
        webs.write('\n'.join(i[0]+"::::::::" + i[1] + "::::::::" + i[2] for i in res))
        webs.close()
    webs = open('./data/webs.txt', 'r', encoding='utf-8')
    lines = webs.readlines()
    webs.close()
    res = []
    for i in lines:
        res.append(i.split('::::::::'))
    all_data = []
    for algorithm in algorithm_dict:  # 枚举算法
        explains = []
        algorithm = algorithm.replace('\n', '')
        algorithm_s = algorithm.split(',')
        records = {}
        urls = {}
        for a in algorithm_s:  # 枚举一个算法可能的名字
            a = a.replace(' ', '').split('（')[0]
            for website in res:
                # similarity = fuzz.partial_ratio(algorithm.lower(), website[2])
                cnt = website[2].count(a.lower())
                if cnt > 0:
                    if website[1] in records.keys():
                        records[website[1]] += cnt
                    else:
                        records[website[1]] = cnt
                        urls[website[1]] = website[0]
        for record in records.items():
            if record[1] >= 1:
                explains.append({'url': urls[record[0]], 'name': record[0], 'frequency': record[1]})
        all_data.append({'algorithm': algorithm, 'explains': explains})
    end_wiki = time.time()
    wiki_time = end_wiki - start_wiki
    print(f"----------oi-wiki爬取完成！用时{int(wiki_time)}秒。----------")

    """将爬取信息写入algorithm.json中"""
    with open('data/algorithm.json', 'w', encoding='utf-8') as json_file:
        for item in all_data:
            json_file.write(json.dumps(item, ensure_ascii=False) + '\n')


spider_main()
