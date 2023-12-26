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


def spider_main():
    if not os.path.exists('./data/'):
        os.makedirs('./data/')
    all_data = []  # 创建一个列表，用于存储所有的数据
    for page in range(1, 3):
        try:
            luogu_url = f"https://www.luogu.com.cn/problem/list?page={page}"
            data = luogu_spider(luogu_url)

            # 将当前页面爬取的数据添加到 all_data 列表中
            all_data.extend(data)

            print(f"{luogu_url} finished")
        except Exception as e:
            print(e)

    # 将 all_data 列表中的数据保存为 JSON 文件
    with open('./data/luogu.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


spider_main()
