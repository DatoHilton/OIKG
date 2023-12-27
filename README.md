## OIKG：天津大学智能与计算学部2023年知识图谱课程大作业

### 项目概述

待补充

### 项目结构

```bash
├─data                # 建图所用数据，由爬虫得到
│  ├─algorithm.json   # 根据洛谷爬得的算法，通过oi-wiki爬取算法讲解
│  └─luogu.json       # 洛谷爬得数据
├─dict                # 导出的数据（节点们）
│  ├─algorithm.txt    # 算法名
│  ├─pos.txt          # 省份
│  ├─problem.txt      # 题目
│  ├─source.txt       # 来源
│  └─year.txt         # 年份
├─build_OIgraph.py    # 建图脚本
├─data_spider.py      # 爬虫脚本
```

### 依赖项

- **数据库：Neo4j**

- **开发语言：Python**

### 快速开始

1.启动Neo4j数据库：打开命令提示符

```bash
> neo4j.bat console
```

2.数据爬取：执行`data_spider.py`脚本

3.图谱构建：执行`build_OIgraph.py`脚本

4.查看图谱：图谱部署在浏览器 http://localhost:7474/browser/