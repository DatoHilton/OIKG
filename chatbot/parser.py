class QuestionPaser:
    @staticmethod
    def build_entitydict(args):
        entity_dict = {}
        for arg, types in args.items():
            for _type in types:
                if _type not in entity_dict:
                    entity_dict[_type] = [arg]
                else:
                    entity_dict[_type].append(arg)
        return entity_dict

    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {'question_type': question_type}
            sql = []
            if question_type == 'problem_algorithm':
                sql = self.sql_transfer(question_type, entity_dict.get('problem'))
            elif question_type == 'algorithm_problem':
                sql = self.sql_transfer(question_type, entity_dict.get('algorithm'))
            elif question_type == 'problem_source':
                sql = self.sql_transfer(question_type, entity_dict.get('problem'))
            elif question_type == 'problem_year':
                sql = self.sql_transfer(question_type, entity_dict.get('problem'))
            elif question_type == 'problem_pos':
                sql = self.sql_transfer(question_type, entity_dict.get('problem'))

            if sql:
                sql_['sql'] = sql
                sqls.append(sql_)

        return sqls

    @staticmethod
    def sql_transfer(question_type, entities):
        if not entities:
            return []
        sql = []

        # 根据题目查找算法
        if question_type == 'problem_algorithm':
            sql = [f"MATCH (m:problem)-->(n:algorithm) WHERE m.name = '{i}' RETURN m.name, n.name" for i in entities]
        elif question_type == 'algorithm_problem':
            sql = [f"MATCH (n:problem)-->(m:algorithm) WHERE m.name = '{i}' RETURN m.name, n.name, n.id, n.url" for i in entities]
        elif question_type == 'problem_source':
            sql = [f"MATCH (m:problem)-->(n:source) WHERE m.name = '{i}' RETURN m.name, n.name" for i in entities]
        elif question_type == 'problem_year':
            sql = [f"MATCH (m:problem)-->(n:year) WHERE m.name = '{i}' RETURN m.name, n.name" for i in entities]
        elif question_type == 'problem_pos':
            sql = [f"MATCH (m:problem)-->(n:pos) WHERE m.name = '{i}' RETURN m.name, n.name" for i in entities]

        return sql
