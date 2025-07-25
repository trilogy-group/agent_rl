import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()

# Enable verbose mode to see prompts
llm = init_chat_model("openai:gpt-4o-mini", temperature=0)

# Enable debug logging
import logging
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("langchain.chat_models")
# logger.setLevel(logging.DEBUG)