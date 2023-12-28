import random

from py2neo import Graph


class AnswerSearcher:
    def __init__(self):
        try:
            print("正在连接Neo4j数据库...")
            self.g = Graph("http://localhost:7474", auth=("neo4j", "123456"))
            print("----------Neo4j数据库连接成功！----------")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
        self.num_limit = 20

    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                res = self.g.run(query).data()
                answers += res
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'problem_algorithm':
            desc = [i['n.name'] for i in answers]
            desc = list(set(desc))
            subject = answers[0]['m.name']
            final_answer = f"'{subject}'这道题目涉及的算法有：{';'.join(desc[:self.num_limit])}"
        elif question_type == 'algorithm_problem':
            desc = [f"{i['n.id']} {i['n.name']} {i['n.url']}" for i in answers]
            desc = list(set(desc))
            length = len(desc) - 1
            subject = answers[0]['m.name']
            if len(desc) == 0:
                final_answer = f'抱歉，数据库中目前还没有{subject}的题目'
            else:
                t1, t2 = random.randint(0, length), 0
                res = '\n1. ' + desc[t1]
                if len(desc) >= 2:
                    t2 = random.randint(0, length)
                    while t2 == t1:
                        t2 = random.randint(0, length)
                    res += '\n2. ' + desc[t2]
                if len(desc) >= 3:
                    t3 = random.randint(0, length)
                    while t3 == t2 or t3 == t1:
                        t3 = random.randint(0, length)
                    res += '\n3. ' + desc[t3]
                final_answer = f"'{subject}'这个算法的题目有：{res}"
        elif question_type == 'problem_source':
            desc = [i['n.name'] for i in answers]
            desc = list(set(desc))
            subject = answers[0]['m.name']
            if desc[0] == '':
                final_answer = f"'{subject}'这道题目的来源是：洛谷"
            else:
                final_answer = f"'{subject}'这道题目的来源是：{';'.join(desc[:self.num_limit])}"
        elif question_type == 'problem_year':
            desc = [i['n.name'] for i in answers]
            desc = list(set(desc))
            subject = answers[0]['m.name']
            if desc[0] == '':
                final_answer = f"'{subject}'这道题目的年份未知哦"
            else:
                final_answer = f"'{subject}'这道题目的年份是：{';'.join(desc[:self.num_limit])}"
        elif question_type == 'problem_pos':
            desc = [i['n.name'] for i in answers]
            desc = list(set(desc))
            subject = answers[0]['m.name']
            if desc[0] == '':
                final_answer = f"'{subject}'这道题目的地区未知哦"
            else:
                final_answer = f"'{subject}'这道题目是{';'.join(desc[:self.num_limit])}的题"

        return final_answer
