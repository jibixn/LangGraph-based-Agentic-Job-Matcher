from tools.fs_tools import FileSystemTools
from typing import TypedDict
from tools.rag import RAGTool
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, RootModel
from typing import List, Annotated
from operator import add
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser



class resumeInformation(BaseModel):
    name:str
    matched_req : List[str]
    missing_req : List[str]
    rank : int

class resumeInformationList(RootModel[List[resumeInformation]]):
    pass


class profileMatchingAgentState(TypedDict): 
    job_description_path: str     
    job_description_text: str    
    job_required_skills : str
    retrieved_resume_info: str
    selected_resume_info: Annotated[List[dict], add]
    # approved: bool
    output : str
    

class profileMatchingAgent:

    def __init__(self, rag_initializer, embedding_model, llm):    

        self.embedding_model = embedding_model
        self.llm = llm
        self.file_tool = FileSystemTools()
        self.rag_tool = RAGTool(rag_initializer)

    # def start_node(self, state: profileMatchingAgentState) -> dict:
    #     '''Recieves the Query'''
    #     return {}

    def parse_JD(self, state: profileMatchingAgentState) -> dict:

        content = self.file_tool.extract_info(state["job_description_path"])
        return {"job_description_text" : content}


    #def candidate_research_agent(self, state: ProfileMatchingAgentState) ->dict

    def extract_req(self, state: profileMatchingAgentState) -> dict:
        response = self.llm.invoke(
            f"Extract the required skills from this JD:\n{state['job_description_text']}"
        )

        return {
            "job_required_skills": response.content
        }
    def search_resumes(self, state: profileMatchingAgentState) -> dict:
        query = state["job_required_skills"]
        res = self.rag_tool.retrieve_from_vector_store(query)
        return {"retrieved_resume_info" : res}

    def rank_resumes(self, state: profileMatchingAgentState) -> dict:
        json_parser = JsonOutputParser(pydantic_object = resumeInformationList)
        json_prompt = PromptTemplate(
            template="""Extract the required information from these resumes:

        {retrieved_resume_info}

        {format_instructions}

        Return a JSON array containing one object for each resume.
        Respond with only the JSON and no additional text.""",

            input_variables=["retrieved_resume_info"],

            partial_variables={
                "format_instructions": json_parser.get_format_instructions()
            }
        )
        chain = json_prompt | self.llm | json_parser
        res = chain.invoke(
            {"retrieved_resume_info" : state["retrieved_resume_info"]}
        )
        return {"selected_resume_info" : res}

    # def approved(self, state: profileMatchingAgentState) -> dict:



    def output(self, state: profileMatchingAgentState) -> dict:
        str_parser = StrOutputParser()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful resume reviewing assistant who reviews the job requirements, matches it against resume information and generates reports about the candidates."),
            ("human", """

                Job Requirements : {req},
                Information about the selected resumes : {info}
                Generate reports about the top 3 candidates and rank them according to their ranks.

            """)
            ]
        )        

        chain = prompt | self.llm | str_parser
        res = chain.invoke(
            {"req": state["job_required_skills"],
            "info": state["retrieved_resume_info"]}
        )

        return {"output" : res}