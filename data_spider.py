import urllib.request

from selenium import webdriver
import json
import os
from selenium.webdriver.common.by import By


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
        source = {'source': [], 'year': 0, 'pos': ''}
        sources = row[i].find_elements(By.XPATH, "./div[@class='tags']/div/a")
        for a in sources:
            span = a.find_element(By.XPATH, f".//span")
            rgb = span.get_attribute("style").split("rgb")[2][:-1]
            if rgb == '(19, 194, 194)':
                source['source'].append(span.text)
            elif rgb == '(82, 196, 26)':
                source['pos'] = span.text
            elif rgb == '(52, 152, 219)':
                source['year'] = int(span.text)
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
    print("-----get category finished-----")

    cnt = 0
    urls = urls[130:150]  # *****************全部：[0:]    算法：[56:-1]*********************
    for url in urls:
        cnt += 1
        # 根据url，请求html
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8').split("<div class=md-content data-md-component=content>")[1].split("</div></main>")[0]
        htmls.append([url, html.lower()])
        print(f"-----get htmls {cnt}/{len(urls)}-----")
    print("-----get htmls finished-----")

    return htmls


def spider_main():
    # if not os.path.exists('./data/'):
    #     os.makedirs('./data/')
    # all_data = []  # 创建一个列表，用于存储所有的数据
    # for page in range(1, 3):
    #     try:
    #         luogu_url = f"https://www.luogu.com.cn/problem/list?page={page}"
    #         data = luogu_spider(luogu_url)
    #
    #         # 将当前页面爬取的数据添加到 all_data 列表中
    #         all_data.extend(data)
    #
    #         print(f"{luogu_url} finished")
    #     except Exception as e:
    #         print(e)
    #
    # # 将 all_data 列表中的数据保存为 JSON 文件
    # with open('./data/luogu.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_data, f, ensure_ascii=False, indent=4)
    # print("--------------------luogu finish--------------------")

    #############################################################
    #########################假设已经有dict########################
    #############################################################
    algorithm_dict_file = open('./dict/algorithm.txt', 'r', encoding='utf-8')
    algorithm_dict = algorithm_dict_file.readlines()
    algorithm_dict_file.close()
    res = wiki_spider()
    all_data = []
    for algorithm in algorithm_dict:  # 枚举算法
        explains = []
        algorithm = algorithm.replace(' ', '').replace('\n', '')
        algorithm_s = algorithm.split(',')
        for a in algorithm_s:  # 枚举一个算法可能的名字
            for website in res:
                cnt = website[1].count(a.lower())
                if cnt >= 10:  # *************算法词在网页出现的频繁度 超参数，可设置**********************
                    explains.append({'url': website[0], 'frequency': cnt})
        all_data.append({'algorithm': algorithm, 'explains': explains})
    print("--------------------oi-wiki finish--------------------")


spider_main()
