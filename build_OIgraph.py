import os
import json
from py2neo import Graph, Node


class OIgraph:
    def __init__(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前绝对路径的上层目录
        self.data_path = os.path.join(cur_dir, 'data\\luogu.json')  # 获取json文件路径
        try:
            self.g = Graph("http://localhost:7474", auth=("neo4j", "123456"))
            print("Successfully connected to Neo4j!")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    '''读取文件'''

    def read_nodes(self):

        # 构建节点
        algorithms = []  # 算法（关键节点）
        problems = []  # 题目
        problem_infos = []
        sources = []  # 来源
        years = []  # 年份
        poses = []  # 省份

        # 构建边
        rels_algorithm_problem = []  # 算法-题目
        # rels_algorithm_explain = []  # 算法-讲解
        rels_problem_source = []  # 题目-来源
        rels_problem_year = []  # 题目-年份
        rels_problem_pos = []  # 题目-省份

        with open(self.data_path, 'r', encoding='utf-8') as file:
            for data in file:
                problem_dict = {}

                # 读取数据
                data_json = json.loads(data)

                problem = data_json['name']
                problems.append(problem)
                # name, id, url, rate是problem的属性
                problem_dict['name'] = data_json['name']
                problem_dict['id'] = data_json['id']
                problem_dict['url'] = data_json['url']
                problem_dict['rate'] = data_json['rate']

                algorithms += data_json['algorithm']
                # 算法-题目
                for algorithm in data_json['algorithm']:
                    rels_algorithm_problem.append([problem, algorithm])

                source = data_json['source']['source']
                sources.append(source)
                rels_problem_source.append([problem, source])

                year = data_json['source']['year']
                years.append(year)
                rels_problem_year.append([problem, year])

                pos = data_json['source']['pos']
                poses.append(pos)
                rels_problem_pos.append([problem, pos])

                problem_infos.append(problem_dict)

        return set(algorithms), set(problems), set(sources), set(years), set(
            poses), problem_infos, rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos

    '''建立节点'''

    def create_node(self, label, nodes):
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
        return

    '''创建problems的节点'''

    def create_problems_nodes(self, problem_infos):
        for problem_dict in problem_infos:
            node = Node("problem", name=problem_dict['name'], id=problem_dict['id'], url=problem_dict['url'],
                        rate=problem_dict['rate'])
            self.g.create(node)
        return

    '''创建知识图谱实体节点类型schema，节点个数多，创建过程慢'''

    def create_graphNodes(self):
        algorithms, problems, sources, years, poses, problem_infos, rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos = self.read_nodes()
        self.create_node('algorithm', algorithms)
        self.create_problems_nodes(problem_infos)
        self.create_node('source', sources)
        self.create_node('year', years)
        self.create_node('pos', poses)
        return

    '''创建实体关系边'''

    def create_graphRels(self):
        algorithms, problems, sources, years, poses, problem_infos, rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos = self.read_nodes()
        self.create_relationship('problem', 'algorithm', rels_algorithm_problem, 'algorithm_problem', '算法-题目')
        self.create_relationship('problem', 'source', rels_problem_source, 'problem_source', '题目-来源')
        self.create_relationship('problem', 'year', rels_problem_year, 'problem_year', '题目-年份')
        self.create_relationship('problem', 'pos', rels_problem_pos, 'problem_pos', '题目-省份')

    '''创建实体关联边'''

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):  # 起点节点，终点节点，边，关系类型，关系名字
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))  # 使用###作为不同关系之间分隔的标志
        for edge in set(set_edges):
            edge = edge.split('###')  # 选取前两个关系，因为两个节点之间一般最多两个关系
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)  # match语法，p，q分别为标签，rel_type关系类别，rel_name关系名字
            try:
                self.g.run(query)  # 执行语句
            except Exception as e:
                print(e)
        return

    '''导出数据'''

    def export_data(self):
        algorithms, problems, sources, years, poses, problem_infos, rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos = self.read_nodes()
        f_algorithm = open('dict/algorithm.txt', 'w+')
        f_problem = open('dict/problem.txt', 'w+')
        f_source = open('dict/source.txt', 'w+')
        f_year = open('dict/year.txt', 'w+')
        f_pos = open('dict/pos.txt', 'w+')

        f_algorithm.write('\n'.join(list(algorithms)))
        f_problem.write('\n'.join(list(problems)))
        f_source.write('\n'.join(list(sources)))
        f_year.write('\n'.join(list(years)))
        f_pos.write('\n'.join(list(poses)))

        f_algorithm.close()
        f_problem.close()
        f_source.close()
        f_year.close()
        f_pos.close()

        return


if __name__ == '__main__':
    handler = OIgraph()  # 创建图数据库
    handler.export_data()  # 输出数据，可以选择不执行
    handler.create_graphNodes()  # 创建节点
    handler.create_graphRels()  # 创建关系
    print("Successfully built oi-gragh! Please check at http://localhost:7474/browser/")

'''快速清空数据库
MATCH (n)
DETACH DELETE n
'''