import autogen
import os
import openai
from memgpt.autogen.memgpt_agent import create_autogen_memgpt_agent
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

#The user Agent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    system_message="A human admin",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: x.get("content","").rstrip().endswitch("TERMINATE"),
    code_execution_config={
        "work_dir": "groupchat",
        "last_n_messages": 2,
    }
)


#The proxy agent that coordinates everything
Tessarect = autogen.AssistantAgent(
    name="Tessarect",
    system_message="You are a personal assistent for ({user_proxy.name}). You should help him with his work",
    llm_config=llm_config,
    code_execution_config={
        "work_dir": "groupchat",
        "last_n_messages": 2,
        "use_docker": False
    }
  )

Coder = autogen.AssistantAgent(
    name="Coder",
    system_message=" I am 10x engineer, trained in multiple programming languages.",
    llm_config=llm_config,
    code_execution_config={
        "work_dir": "code",
        "last_n_messages": 2,
        "use_docker": False
    }
  )

#True for debug
DEBUG = True
interface_kwargs = {
    "debug" : DEBUG,
    "show_innner_thoughts": DEBUG,
    "show_function_outputs" : DEBUG
}

# coder = create_autogen_memgpt_agent(
#     autogen_name="coding_agent",
#     persona_description=" I am 10x engineer, trained in multiple programming languages. My job is write code, and output ({user_proxy.name}) or to working directory respectively." + 
#                          "You report to ({tessarect.name}) because that agent has all the schedule work for ({user_proxy.name}).",
#     user_description= "You part of a group of agents that work together to improve the workoutput of the human user. Your skills are for programming, cyber security and devOps and that is your role",
#     interface_kwargs=interface_kwargs
# )

# Initiate group chat
# grpChat = autogen.GroupChat(agents=[user_proxy, Coder,Tessarect], messages=[], max_round=5)
# manager = autogen.GroupChatManager(groupchat=grpChat, llm_config=llm_config)

# Begin the group chat with a message from the user
user_proxy.initiate_chat(
    Tessarect,
    message="Ask for your next task"
)