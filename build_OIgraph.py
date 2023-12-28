import json
import time
from py2neo import Graph, Node


class OIgraph:
    def __init__(self):
        try:
            print("正在连接Neo4j数据库...")
            start_neo = time.time()
            self.g = Graph("http://localhost:7474", auth=("neo4j", "123456"))
            end_neo = time.time()
            neo_time = end_neo - start_neo
            print(f"----------Neo4j数据库连接成功！用时{int(neo_time)}秒。----------")
            print("正在创建OI-Graph...")
            self.start_graph = time.time()
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    '''读取文件'''

    @staticmethod
    def read_nodes():
        # 构建节点
        algorithms = []  # 算法（关键节点）
        problems = []  # 题目（构建节点不需要，导出题目数据需要）
        problem_infos = []  # 题目
        algorithm_explains = []  # 算法解释
        sources = []  # 来源
        years = []  # 年份
        poses = []  # 省份

        # 构建边
        rels_algorithm_problem = []  # 算法-题目
        rels_algorithm_explain = []  # 算法-讲解
        rels_problem_source = []  # 题目-来源
        rels_problem_year = []  # 题目-年份
        rels_problem_pos = []  # 题目-省份

        with open('data/luogu.json', 'r', encoding='utf-8') as file:
            for data in file:
                problem_dict = {}

                # 读取数据
                data_json = json.loads(data)

                problem = data_json.get('name', '')
                problems.append(problem)
                # name, id, url, rate是problem的属性
                problem_dict['name'] = problem
                problem_dict['id'] = data_json.get('id', '')
                problem_dict['url'] = data_json.get('url', '')
                problem_dict['rate'] = data_json.get('rate', '')

                algorithms += data_json.get('algorithm', [])
                for algorithm in data_json['algorithm']:
                    rels_algorithm_problem.append([problem, algorithm])

                source = data_json['source'].get('source', '')
                sources.append(source)
                rels_problem_source.append([problem, source])

                year = data_json['source'].get('year', '')
                years.append(year)
                rels_problem_year.append([problem, year])

                pos = data_json['source'].get('pos', '')
                poses.append(pos)
                rels_problem_pos.append([problem, pos])

                problem_infos.append(problem_dict)

        # 去除结点空值
        poses = [pos for pos in poses if pos]
        years = [year for year in years if year]
        sources = [source for source in sources if source]

        with open('data/algorithm.json', 'r', encoding='utf-8') as file:
            for data in file:
                explain_dict = {}
                data_json = json.loads(data)

                algorithm = data_json.get('algorithm', '')
                for item in data_json['explains']:
                    # name, url是item的属性
                    explain = item.get('name', '')
                    explain_dict['name'] = explain
                    explain_dict['url'] = item.get('url', '')
                    algorithm_explains.append(explain_dict)
                    frequency = item.get('frequency', '')
                    # name, frequency是边的属性
                    rels_algorithm_explain.append([algorithm, explain, str(frequency)])

        # 去重
        algorithm_explains = [dict(t) for t in {tuple(d.items()) for d in algorithm_explains}]

        return (set(algorithms), set(problems), set(sources), set(years), set(poses), problem_infos,
                algorithm_explains, rels_algorithm_problem, rels_problem_source, rels_problem_year,
                rels_problem_pos, rels_algorithm_explain)

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

    '''创建explains的节点'''

    def create_explains_nodes(self, algorithm_explains):
        for explain_dict in algorithm_explains:
            node = Node("explain", name=explain_dict['name'], url=explain_dict['url'])
            self.g.create(node)
        return

    '''创建知识图谱实体节点类型schema，节点个数多，创建过程慢'''

    def create_graphNodes(self):
        (algorithms, problems, sources, years, poses, problem_infos, algorithm_explains,
         rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos,
         rels_algorithm_explain) = self.read_nodes()
        self.create_node('algorithm', algorithms)
        self.create_problems_nodes(problem_infos)
        self.create_explains_nodes(algorithm_explains)
        self.create_node('source', sources)
        self.create_node('year', years)
        self.create_node('pos', poses)
        return

    '''创建实体关系边'''

    def create_graphRels(self):
        (algorithms, problems, sources, years, poses, problem_infos, algorithm_explains,
         rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos,
         rels_algorithm_explain) = self.read_nodes()
        self.create_relationship('problem', 'algorithm', rels_algorithm_problem, 'algorithm_problem', '算法-题目')
        self.create_relationship('algorithm', 'explain', rels_algorithm_explain, 'algorithm_explain', '算法-讲解')
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

            # 创建参数化查询
            if rel_type == "algorithm_explain":
                frequency = edge[2]
                query = """
                MATCH (p:%s), (q:%s)
                WHERE p.name=$p_name AND q.name=$q_name
                CREATE (p)-[rel:%s{name:$rel_name, frequency:$frequency}]->(q)
                """ % (start_node, end_node, rel_type)
                parameters = {"p_name": p, "q_name": q, "rel_name": rel_name, "frequency": frequency}
            else:
                query = """
                MATCH (p:%s), (q:%s)
                WHERE p.name=$p_name AND q.name=$q_name
                CREATE (p)-[rel:%s{name:$rel_name}]->(q)
                """ % (start_node, end_node, rel_type)
                parameters = {"p_name": p, "q_name": q, "rel_name": rel_name}

            try:
                self.g.run(query, parameters)  # 执行参数化查询
            except Exception as e:
                print(e)
        return

    '''导出数据'''

    def export_data(self):
        (algorithms, problems, sources, years, poses, problem_infos, algorithm_explains,
         rels_algorithm_problem, rels_problem_source, rels_problem_year, rels_problem_pos,
         rels_algorithm_explain) = self.read_nodes()
        f_problem_name = open('dict/problem_name.txt', 'w+', encoding='utf-8')
        f_source = open('dict/source.txt', 'w+', encoding='utf-8')
        f_year = open('dict/year.txt', 'w+', encoding='utf-8')
        f_pos = open('dict/pos.txt', 'w+', encoding='utf-8')
        f_problem_id = open('dict/problem_id.txt', 'w+', encoding='utf-8')

        f_problem_name.write('\n'.join(list(problems)))
        f_source.write('\n'.join(list(sources)))
        f_year.write('\n'.join(list(years)))
        f_pos.write('\n'.join(list(poses)))
        problem_ids = [item['id'] for item in problem_infos]
        f_problem_id.write('\n'.join(problem_ids))

        f_problem_name.close()
        f_source.close()
        f_year.close()
        f_pos.close()
        f_problem_id.close()

        return


if __name__ == '__main__':
    handler = OIgraph()  # 创建图数据库
    handler.export_data()  # 输出数据，可以选择不执行
    handler.create_graphNodes()  # 创建节点
    handler.create_graphRels()  # 创建关系
    end_graph = time.time()
    graph_time = end_graph - handler.start_graph
    print(f"----------OI-Gragh创建成功！用时{int(graph_time)}秒。----------")
    print("请在浏览器中查看图谱：http://localhost:7474/browser/")

'''快速清空数据库
MATCH (n)
DETACH DELETE n
'''
