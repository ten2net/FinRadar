from typing import Dict, Optional, Union

from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
import chainlit as cl

import sys
# sys.path.append("path/to/your/module")

from libs import FactorAgent

TASK = "Plot a chart of NVDA stock price change YTD and save it on disk."
TASK = "开始工作"
# TASK = "撰写西安市未央区防洪抢险应急预案."


async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res


class ChainlitAssistantAgent(AssistantAgent):
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
                author="AssistantAgent",
            ).send()
        )
        super(ChainlitAssistantAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )


class ChainlitUserProxyAgent(UserProxyAgent):
    def get_human_input(self, prompt: str) -> str:
        if prompt.startswith(
            "Provide feedback to assistant. Press enter to skip and use auto-reply"
        ):
            res = cl.run_sync(
                ask_helper(
                    cl.AskActionMessage,
                    content="继续、提供更多反馈还是结束任务退出?",
                    actions=[
                        cl.Action(
                            name="continue", value="continue", label="✅ 继续"
                        ),
                        cl.Action(
                            name="feedback",
                            value="feedback",
                            label="💬 提供更多反馈",
                        ),
                        cl.Action( 
                            name="exit",
                            value="exit", 
                            label="🔚 退出会话" 
                        ),
                    ],
                )
            )
            if res.get("value") == "continue":
                return ""
            if res.get("value") == "exit":
                return "exit"

        reply = cl.run_sync(ask_helper(cl.AskUserMessage, content=prompt, timeout=60))

        return reply["content"].strip()

    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        cl.run_sync(
            cl.Message(
                content=f'*发消息给 "{recipient.name}"*:\n\n{message}',
                author="UserProxyAgent",
            ).send()
        )
        super(ChainlitUserProxyAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {
        "assistant": "斐纳斯研究助手", 
        "UserProxyAgent": "用户代理", 
        "Chatbot": "斐纳斯"
    }
    return rename_dict.get(orig_author, orig_author)

@cl.on_chat_start
async def on_chat_start():
    
    # await cl.Avatar(
    #     name="Tool 1",
    #     url="https://avatars.githubusercontent.com/u/128686189?s=400&u=a1d1553023f8ea0921fba0debbe92a8c5f840dd9&v=4",
    # ).send()

    # await cl.Message(
    #     content="This message should not have an avatar!", author="Tool 0"
    # ).send()

    # await cl.Message(
    #     content="This message should have an avatar!", author="Tool 1"
    # ).send()

    # await cl.Message(
    #     content="This message should not have an avatar!", author="Tool 2"
    # ).send()    
    
    
    config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
    # assistant = ChainlitAssistantAgent(
    #     "assistant", llm_config={"config_list": config_list}
    # )
    assistant = FactorAgent(
        "assistant", llm_config={"config_list": config_list}
    )
    assistant.load()
    user_proxy = ChainlitUserProxyAgent(
        "user_proxy",
        code_execution_config={
            "work_dir": "workspace",
            "use_docker": False,
        },
    )
    # await cl.Message(content=f"欢迎使用蜂乃思雷达").send()
    await cl.Message(content=f"启动代理来处理任务: {TASK}...").send()
    await cl.make_async(user_proxy.initiate_chat)(
        assistant,
        message=TASK,
    )
