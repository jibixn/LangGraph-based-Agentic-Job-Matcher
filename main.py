from init_rag import RAGInitializer
from matching_agent import profileMatchingAgent, profileMatchingAgentState
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv



def main():    
    folder = "resources/resumes"    

    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")    

    load_dotenv()

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=1,
        max_tokens=None,
        reasoning_effort="medium",        
    )
    
    rag_obj = RAGInitializer(embedding_model)
    _,_,_ = rag_obj.initialize_components()

    print("RAG Initialized")

    # rag_obj.add_to_vector_store(folder) #Only do this once.

    print("Resumes added to Vector Store")

    agent = profileMatchingAgent(rag_obj, embedding_model, llm)

    graph = StateGraph(profileMatchingAgentState)

    graph.add_node("parse_job_desc", agent.parse_JD)
    graph.add_node("extract_requirements", agent.extract_req)
    graph.add_node("search_resumes", agent.search_resumes)
    graph.add_node("rank_resumes", agent.rank_resumes)
    graph.add_node("output", agent.output)

    graph.add_edge(START, "parse_job_desc")
    graph.add_edge("parse_job_desc", "extract_requirements")
    graph.add_edge("extract_requirements", "search_resumes")
    graph.add_edge("search_resumes", "rank_resumes")
    graph.add_edge("rank_resumes", "output")
    graph.add_edge("output", END)

    print("Graph initialized succesfully")

    memory = InMemorySaver()

    application = graph.compile(
        checkpointer = memory
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
        "retrieved_resume_info": [],
        "selected_resume_info": [],
        "output": ""
    }, config)

    print(result["output"])


if __name__ == "__main__":
    main()






