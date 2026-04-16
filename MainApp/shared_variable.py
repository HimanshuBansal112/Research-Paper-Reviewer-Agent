import os
from langchain_google_genai import ChatGoogleGenerativeAI
from django.db import connection

from .paper import Paper_List
from .models import Paper_Output_List

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model= "gemini-2.5-flash",
    temperature=1.0,
    max_retries=2,
    google_api_key=api_key,
)

papers = Paper_List()
def is_table_available():
    return 'MainApp_paper_output_list' in connection.introspection.table_names()

if is_table_available():
    papers.reset_to_output(Paper_Output_List.instance().get_papers())
