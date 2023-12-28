import os
from fuzzywuzzy import fuzz


def longest_common_substring_length(str1, str2):
    m, n = len(str1), len(str2)

    # 创建一个二维数组用于存储最长公共子串的长度
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                max_len = max(max_len, dp[i][j])

    return max_len


class QuestionClassifier:
    def __init__(self):
        cur_dir = './'
        if 'dict' not in os.listdir(cur_dir):
            cur_dir = '../'
        # 特征词路径
        self.algorithm_path = os.path.join(cur_dir, 'dict/algorithm.txt')
        self.pos_path = os.path.join(cur_dir, 'dict/pos.txt')
        self.problem_path = os.path.join(cur_dir, 'dict/problem.txt')
        self.source_path = os.path.join(cur_dir, 'dict/source.txt')
        self.year_path = os.path.join(cur_dir, 'dict/year.txt')
        # 加载特征词
        self.algorithm_wds = [i.strip() for i in open(self.algorithm_path, encoding="utf-8") if i.strip()]
        self.pos_wds = [i.strip() for i in open(self.pos_path, encoding="utf-8") if i.strip()]
        self.problem_wds = [i.strip() for i in open(self.problem_path, encoding="utf-8") if i.strip()]
        self.source_wds = [i.strip() for i in open(self.source_path, encoding="utf-8") if i.strip()]
        self.year_wds = [i.strip() for i in open(self.year_path, encoding="utf-8") if i.strip()]
        self.region_words = set(self.algorithm_wds + self.pos_wds + self.problem_wds + self.source_wds + self.year_wds)
        # 构建字典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.algorithm_qwds = ['算法', '数据结构', '方法', '思路', '标答', '题解', '解析', '知识点']
        self.problem_qwds = ['题目', '问题', '习题', '例题']
        self.explain_qwds = ['解释', '讲解', '说明', '详细解答']
        self.source_qwds = ['来源', '出处', '从哪儿来', '出现']
        self.year_qwds = ['年份', '哪一年', '何年', '哪年', '年份']
        self.pos_qwds = ['省份', '地区', '所在地', '哪个省', '地方']
        print('model init finished ......')

    def classify(self, _question):
        _data = {}
        oi_dict = self.check_oi(_question)
        if not oi_dict:
            return {}
        _data['args'] = oi_dict
        types = []
        for type_ in oi_dict.values():
            types += type_

        question_types = []

        # 题目-算法
        if self.check_words(self.algorithm_qwds, _question) and ('problem' in types):
            question_type = 'problem_algorithm'
            question_types.append(question_type)

        # 题目-来源
        if self.check_words(self.source_qwds, _question) and ('problem' in types):
            question_type = 'problem_source'
            question_types.append(question_type)

        # 题目-年份
        if self.check_words(self.year_qwds, _question) and ('problem' in types):
            question_type = 'problem_year'
            question_types.append(question_type)

        # 题目-地区
        if self.check_words(self.pos_qwds, _question) and ('problem' in types):
            question_type = 'problem_pos'
            question_types.append(question_type)

        # 算法-题目
        if self.check_words(self.problem_qwds, _question) and ('algorithm' in types):
            question_type = 'algorithm_problem'
            question_types.append(question_type)

        _data['question_types'] = question_types

        return _data

    def check_oi(self, _question):
        region_wds = []
        problem_wds = []
        for pattern in self.region_words:
            if pattern == '':
                continue
            if 'algorithm' in self.wdtype_dict[pattern]:
                for name in pattern.split(','):
                    similarity = fuzz.partial_ratio(_question.lower(), name.lower())
                    if similarity >= 80:
                        region_wds.append(pattern)
                        break
            if 'pos' in self.wdtype_dict[pattern] or 'year' in self.wdtype_dict[pattern]:
                similarity = fuzz.partial_ratio(_question.lower(), pattern.lower())
                if similarity >= 99:
                    region_wds.append(pattern)
            if 'problem' in self.wdtype_dict[pattern]:
                similarity = fuzz.partial_ratio(_question.lower(), pattern.lower().split(']')[-1])
                if similarity >= 66:
                    problem_wds.append(pattern)
            if 'source' in self.wdtype_dict[pattern]:
                similarity = fuzz.partial_ratio(_question.lower(), pattern.lower())
                if similarity >= 55:
                    region_wds.append(pattern)
        problem = ['', 0]
        for name in problem_wds:
            length = longest_common_substring_length(name, _question)
            if length > problem[1]:
                problem = [name, length]
        if problem[1] != 0:
            region_wds.append(problem[0])
        final_dict = {i: self.wdtype_dict.get(i) for i in region_wds}

        return final_dict

    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.algorithm_wds:
                wd_dict[wd].append('algorithm')
            if wd in self.pos_wds:
                wd_dict[wd].append('pos')
            if wd in self.problem_wds:
                wd_dict[wd].append('problem')
            if wd in self.source_wds:
                wd_dict[wd].append('source')
            if wd in self.year_wds:
                wd_dict[wd].append('year')
        return wd_dict

    @staticmethod
    def check_words(wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)
