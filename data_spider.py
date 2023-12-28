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
    urls = urls[130:150]  # *****************全部：[0:]    算法：[56:-1]*********************
    for url in urls:
        cnt += 1
        # 根据url，请求html
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.63 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        res = urllib.request.urlopen(req)
        html = \
            res.read().decode('utf-8').split("<div class=md-content data-md-component=content>")[1].split(
                "</div></main>")[
                0]
        name = html.split('<h1>')[1].split('</h1>')[0]
        htmls.append([url, name, html.lower()])
    #     print(f"-----get htmls {cnt}/{len(urls)}-----")
    # print("-----get htmls finished-----")

    return htmls


def spider_main():
    """爬取洛谷"""
    print("正在爬取洛谷...")
    if not os.path.exists('./data/'):
        os.makedirs('./data/')

    luogu_page_cnt = 0  # 爬取洛谷的页数
    for page in range(1, 2):
        try:
            luogu_url = f"https://www.luogu.com.cn/problem/list?page={page}"
            data = luogu_spider(luogu_url)

            # 逐个将爬取的数据保存为单独的JSON对象
            for item in data:
                with open('./data/luogu.json', 'a', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')  # 每个JSON对象后面添加一个换行符
            luogu_page_cnt += 1
        except Exception as e:
            print(e)

    print(f"----------洛谷爬取完成！爬取{luogu_page_cnt}页----------")

    """从luogu.json中生成algorithm.dict，用于爬取oi-wiki"""
    all_algorithms = set()
    with open('data/luogu.json', 'r', encoding='utf-8') as file:
        for data in file:
            data_json = json.loads(data)
            algorithm = data_json.get('algorithm', [])
            all_algorithms.update(algorithm)

    # 去除空值
    all_algorithms.discard('')

    # 将算法写入 algorithm.txt 文件
    if not os.path.exists('dict'):
        os.makedirs('dict')
    with open('dict/algorithm.txt', 'w', encoding='utf-8') as txt_file:
        for algorithm in all_algorithms:
            txt_file.write(f"{algorithm}\n")

    """爬取oi-wiki"""
    print("正在爬取oi-wiki...")
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
                cnt = website[2].count(a.lower())
                if cnt >= 10:  # 算法词在网页出现的频繁度 超参数，可设置
                    explains.append({'url': website[0], 'name': website[1], 'frequency': cnt})
        all_data.append({'algorithm': algorithm, 'explains': explains})
    print("----------oi-wiki爬取完成！----------")

    """将爬取信息写入algorithm.json中"""
    with open('data/algorithm.json', 'w', encoding='utf-8') as json_file:
        for item in all_data:
            json_file.write(json.dumps(item, ensure_ascii=False) + '\n')


spider_main()


{"algorithm": "二分", "explains": [{"url": "https://oi-wiki.org/dp/opt/slope/", "frequency": 11}, {"url": "https://oi-wiki.org/dp/opt/quadrangle/", "frequency": 13}]}