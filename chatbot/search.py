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
            subject = answers[0]['m.name']
            final_answer = f"'{subject}'这道题目涉及的算法有：{';'.join(list(set(desc))[:self.num_limit])}"

        return final_answer

