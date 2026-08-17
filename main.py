from init_rag import RAGInitializer
from matching_agent import profileMatchingAgent, profileMatchingAgentState
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_mistralai.chat_models import ChatMistralAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from tools.rag import RAGTool



def main():    
    folder = "resources/resumes"    

    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")    

    load_dotenv()

    llm = ChatOllama(
        model="qwen3:1.7b",
        temperature=1,
        max_tokens=None            
    )

    
    
    rag_obj = RAGInitializer(embedding_model)
    _,_,_ = rag_obj.initialize_components()

    print("RAG Initialized")

    # rag_obj.add_to_vector_store(folder) #Only do this once or when knowledge base is to be updated.

    print("Resumes added to Vector Store")

    agent = profileMatchingAgent(rag_obj, embedding_model, llm)
    rag_tool = RAGTool(rag_obj)

    def check_approval(state : profileMatchingAgentState):
        """ route based on approval status"""
        if state.get("approved", False):
            return "accept"
        return "reject"

    def check_next_action(state : profileMatchingAgentState):
        """ route based on next action"""
        if state.get("next_action", 0) == 1:
            return "rerank"
        return "retrieve"


    tools = [
        rag_tool.retrieve_from_vector_store_mmr,
        rag_tool.retrieve_from_vector_store_similarity
    ]

    tool_node = ToolNode(tools)

    graph = StateGraph(profileMatchingAgentState)



    graph.add_node("parse_job_desc", agent.parse_JD)
    graph.add_node("extract_requirements", agent.extract_req)
    graph.add_node("search_resumes", agent.search_resumes)
    graph.add_node("extract_chunks", agent.extract_text_from_chunks)
    graph.add_node("select_resumes", agent.select_resumes)
    graph.add_node("retrieve_more", agent.retrieve_more)
    graph.add_node("agent_node", agent.agent_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("rank_resumes", agent.rank_resumes)
    graph.add_node("ask_approval", agent.approve)
    graph.add_node("output", agent.output)

    graph.add_edge(START, "parse_job_desc")
    graph.add_edge("parse_job_desc", "extract_requirements")
    graph.add_edge("extract_requirements", "search_resumes")
    graph.add_edge("search_resumes", "extract_chunks")
    graph.add_edge("extract_chunks", "select_resumes")
    graph.add_edge("select_resumes", "ask_approval")
    graph.add_conditional_edges(
        "ask_approval",
        check_approval,
        {
            "accept" : "output", "reject" : "agent_node"
        }
    )
    graph.add_conditional_edges(
        "agent_node",
        check_next_action,
        {
            "rerank" : "rank_resumes", "retrieve" : "retrieve_more"
        }
    )
    graph.add_edge("rank_resumes", "ask_approval")
    graph.add_edge("retrieve_more", "tool_node")
    graph.add_edge("tool_node", "extract_chunks")    

    graph.add_edge("output", END)

    print("Graph initialized succesfully")

    memory = InMemorySaver()

    application = graph.compile(
        checkpointer = memory,
        # interrupt_after = ["select_resumes", "rank_resumes"]
    )
    config = {
    "configurable": {
        "thread_id": "profile_matching_1"
    }
}
    result = application.invoke({
        "job_description_path": "resources/SDE Job Description.pdf",
        "job_description_text": "",
        "job_required_skills": "",
        "chunks" : [],
        "retrieved_resume_info": [],
        "selected_resume_info": [],
        "feedback" : [],
        "iteration" : 0,
        "approved" : False,
        "messages" : "",
        "next_action" : "",
        "output": ""
    }, config)

    # print("\n========== GRAPH RESULT ==========")
    # print(result)

    print("\n========== OUTPUT ==========")
    print(result.get("output"))

    # print("\n========== ITERATION ==========")
    # print(result.get("iteration"))

    # print("\n========== APPROVED ==========")
    # print(result.get("approved"))

    # print("\n========== SELECTED RESUMES ==========")
    # print(result.get("selected_resume_info"))


if __name__ == "__main__":
    main()






