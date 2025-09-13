from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

from .shared_variable import papers, llm
from .models import Paper_Output_List
from .paper import Paper, Paper_Output, Paper_List
from .paper_processing import get_paper

@tool
def add_about_paper(index: int, rating: float, genuinity: float, summary: str):
    """
    Save the rating and genuinity score of a paper.
    Args:
        index (int): The index of the paper.
        rating (float): Rating score from 1 to 10.
        genuinity (float): Genuinity score from 1 to 10.
        summary (str): A concise summary of the paper (max 300 words).
    Returns:
        None
    """
    
    if not(Paper_Output_List.instance().add(Paper_Output(paper = papers.papers[index], rating = rating, genuinity = genuinity, summary = summary))):
        raise Exception("Paper already exist")

tools = [add_about_paper]
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def agent(index):
    builder = StateGraph(State)

    builder.add_node(chatbot)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    graph = builder.compile()

    init_len = len(Paper_Output_List.instance().get_papers())

    state = graph.invoke({
        "messages": [{
            "role": "user",
            "content": (
                "You must:\n"
                f"1. Read the research paper at index {index}.\n"
                "2. Produce a concise summary (max 300 words) in your own words.\n"
                "3. Assign two scores (rating and genuinity) each between 1 and 10.\n"
                "Rules for scores:\n"
                "- In most cases, choose between 4 and 7 (inclusive).\n"
                "- Do NOT use 8 or 9 unless the paper is truly exceptional.\n"
                "- Use 2 only for very poor work, and 1 or 10 only in extreme, almost impossible cases.\n"
                "- The vast majority of papers should be in the 4–7 range.\n"
                "Finally, call the `add_about_paper` tool with:\n"
                "- index\n"
                "- rating\n"
                "- genuinity\n"
                "- summary\n"
            )
        },
        {
            "role": "user",
            "content": get_paper(index)
        }]
    })
    
    if init_len == len(Paper_Output_List.instance().get_papers()):
        raise Exception("Chatbot or Database failed to add paper")
    
    paper_instance = Paper_Output_List.instance()
    
    if paper_instance.papers:
        paper_output = paper_instance.get_papers()[-1]
        if not(papers.papers[index].title == paper_output.title) or not(papers.papers[index].pdf == paper_output.pdf):
            paper_instance.papers.pop()
            paper_instance.save()
            raise Exception("Chatbot fetched wrong paper")