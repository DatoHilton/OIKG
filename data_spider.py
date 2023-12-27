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


def spider_main():
    if not os.path.exists('./data/'):
        os.makedirs('./data/')

    for page in range(1, 3):
        try:
            luogu_url = f"https://www.luogu.com.cn/problem/list?page={page}"
            data = luogu_spider(luogu_url)

            # 逐个将爬取的数据保存为单独的JSON对象
            for item in data:
                with open('./data/luogu.json', 'a', encoding='utf-8') as f:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')  # 每个JSON对象后面添加一个换行符

            print(f"{luogu_url} finished")
        except Exception as e:
            print(e)


spider_main()
