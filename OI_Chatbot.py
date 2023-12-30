from chatbot.classifier import QuestionClassifier
from chatbot.parser import QuestionPaser
from chatbot.search import AnswerSearcher


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        std_answer = '对不起，我没能理解您的问题。我的词汇量有限，请输入更加标准的词语'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return std_answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return std_answer
        else:
            return '\n'.join(final_answers)


if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input("请输入您要咨询的问题:")
        answer = handler.chat_main(question)
        print('OI机器人:', answer + '\n')


"""
"津津的储蓄计划"这道题目属于哪一类的算法问题？
超级玛丽这道题用到了哪些算法？
树网的核这道题需要注意哪些知识点？

请推荐几道枚举算法的习题
我想练习费用流算法，有没有适合的题目推荐？
能否给我列举一些经典的动态规划算法相关的题目？

超级玛丽是哪年的题？
超级玛丽是哪个地方的题？
超级玛丽的来源是哪儿？

时态同步是哪年的题？
时态同步是哪个地方的题？
时态同步的来源是哪儿？请帮我

我想了解一下动态规划算法。
"""