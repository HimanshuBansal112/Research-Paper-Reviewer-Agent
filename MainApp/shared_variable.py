from langchain.chat_models import init_chat_model

from .paper import Paper_List
from .models import Paper_Output_List

llm = init_chat_model("google_genai:gemini-2.5-flash")

papers = Paper_List()
papers.reset_to_output(Paper_Output_List.instance().get_papers())