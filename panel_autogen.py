#https://github.com/yeyu2/Youtube_demos/blob/main/panel_autogen.py
import autogen
import panel as pn
import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()

config_list = [
    {
        "api_type": os.getenv("api_type"),
        "api_key": os.getenv("api_key"),
        "api_base": os.getenv("api_base")
    }
]

openai.api_key = os.getenv("api_key")
openai.api_base = os.getenv("api_base")

llm_config = {
    "config_list": config_list,
    "seed": int(os.getenv("seed")),
    "request_timeout" : int(os.getenv("request_timeout")),
    "temperature": 0.7
}

def write_file(file_name, file_content):
    with open(file_name, "w") as file1:
        file1.writelines(file_content)

# user_proxy = autogen.UserProxyAgent(
#    name="Tessarect",
#    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
#    system_message="""Human Admin. You are admin. Interact with the task manager for best response to provided task. If it's a simple task not related to coding, reply immediately.
#    Task execution needs to be approved by this admin. Only say APPROVED in most cases, and say EXIT when nothing to be done further. Do not say others.
#     """,
#    code_execution_config=False,
#    default_auto_reply="Approved", 
#    human_input_mode="NEVER",
#    llm_config=llm_config,
# )


user_proxy = autogen.UserProxyAgent(
   name="Tessarect",
   is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
   system_message="""Human Admin. You are admin. Give short instructions to the engineer, if its a simple prompt reply immediately..
   Task execution needs to be approved by this admin. Only say APPROVED in most cases, and say EXIT when nothing to be done further. Do not say others.
    """,
   code_execution_config=False,
   default_auto_reply="Approved", 
   human_input_mode="NEVER",
   llm_config=llm_config,
)

# task_manager = autogen.AssistantAgent(
#     name="task manager",
#     system_message='''Task manager. Evalute the task until Tessarect approval, if its a simple prompt reply immediately. Task execution needs to be approved by this admin.
# The plan may involve an engineer who can write code.
# Explain the task first in short but be clear.
# ''',
#     llm_config=llm_config,
# )

engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message='''Engineer. You follow an approved task. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)

# scientist = autogen.AssistantAgent(
#     name="Scientist",
#     llm_config=llm_config,
#     system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code."""
# )



coder = autogen.UserProxyAgent(
    name="Coder",
    system_message="Coder. Output the code written by the engineer to the directory and do nothing else. ",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "code"},
)

coder.register_function( function_map={"write_file": write_file})

executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result. ",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)




#groupchat = autogen.GroupChat(agents=[user_proxy, task_manager,  engineer, executor], messages=[], max_round=50)
groupchat = autogen.GroupChat(agents=[user_proxy, coder, executor], messages=[], max_round=50)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

#avatar = {user_proxy.name:"👨‍💼", task_manager.name:"🗓", engineer.name:"👩‍💻", executor.name:"🛠"}
avatar = {user_proxy.name:"👨‍💼", task_manager.name:"🗓", engineer.name:"👩‍💻", executor.name:"🛠"}

def print_messages(recipient, messages, sender, config):

    chat_interface.send(messages[-1]['content'], user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    return False, None  # required to ensure the agent communication flow continues

user_proxy.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

engineer.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
# scientist.register_reply(
#     [autogen.Agent, None],
#     reply_func=print_messages, 
#     config={"callback": None},
# ) 

task_manager.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

executor.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
# critic.register_reply(
#     [autogen.Agent, None],
#     reply_func=print_messages, 
#     config={"callback": None},
# ) 

def write_file(file_name, file_content):
    with open(file_name, "w") as file1:
        file1.writelines(file_content)

pn.extension(design="material")
def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    user_proxy.initiate_chat(manager, message=contents)
    
chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send("What Can Netonline AI do for you ?", user="System", respond=False)
chat_interface.servable()