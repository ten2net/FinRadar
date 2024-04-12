from typing import Dict, Optional, Union

from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
import chainlit as cl
import os


class FactorAgent(AssistantAgent):
    def load(self):
     
      alphaFactorFileName:str="Alpha101.txt"
      filepath = os.path.dirname(os.path.realpath(__file__)) + "/" +alphaFactorFileName
      with open(filepath, 'r', encoding='utf-8') as f:
        alphaFactories = f.readlines()      
        self.sources = "\n".join([x.strip() for x in alphaFactories])
        
      sample_json = """
      {
        "expr": 生成的因子表达式,
        "desc": 对该因子表达式的解释说明
      }
      """        
      
      # self.name = "FactorAgent"
      
      system_message=f"""
      你是一个量化分析师。
      你可以通过阅读多个alpha因子表达式，总结其内在规律，并且可以创新性的生成可用的因子表达式。
      对于生成的表达式，你能够解释其有效性，并且能够用清晰简洁的语言解释其各个变量的含义。
      
      指令描述：生成因子表达式
      样例数据：{self.sources}\n
      你的任务是学习以上样例数据资源之后，总结其规律，输出一个类似的因子表达式。\n 
      你在生成表达式时，请仅使用样例数据里的函数，每次生成1个，生成的表达式中，不要带Alpha#xxx,期望因子的相关性低 \n
      
      Please return nothing but a JSON in the following format:\n
      {sample_json}\n 
      """
      print(system_message)
      self.update_system_message(system_message)
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        cl.run_sync(
            cl.Message(
                content=f'*发消息给 "{recipient.name}":*\n\n{message}',
                author="FactorAgent",
            ).send()
        )
        super(FactorAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )
