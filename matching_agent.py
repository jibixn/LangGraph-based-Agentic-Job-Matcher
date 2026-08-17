from tools.fs_tools import FileSystemTools
from typing import TypedDict
from tools.rag import RAGTool
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, RootModel
from typing import List, Annotated
from operator import add
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.documents import Document
from collections import defaultdict


class resumeInformation(BaseModel):
    name:str
    matched_req : List[str]
    missing_req : List[str]
    rank : int

class resumeInformationList(RootModel[List[resumeInformation]]):
    pass

class AgentNextAction(BaseModel):
    next_action : int

class profileMatchingAgentState(TypedDict): 
    job_description_path: str     
    job_description_text: str    
    job_required_skills : str
    chunks : List[Document]
    retrieved_resume_info: str
    selected_resume_info: List[dict]
    feedback : Annotated[List[str], add]
    iteration : int
    approved: bool
    messages : str
    next_action : int
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
        # prompt = PromptTemplate(

        # )
        content = self.file_tool.extract_info(state["job_description_path"])
        return {"job_description_text" : content.page_content}


    #def candidate_research_agent(self, state: ProfileMatchingAgentState) ->dict

    def extract_req(self, state: profileMatchingAgentState) -> dict:
        response = self.llm.invoke(
            f"Extract the required skills from this JD:\n{state['job_description_text']}. Only output the required skills and no additional text."
        )

        return {
            "job_required_skills": response.content
        }



    def search_resumes(self, state: profileMatchingAgentState) -> dict:
        query = state["job_required_skills"]

        # print("\n========== RAG QUERY ==========")
        # print(query)

        res = self.rag_tool.retrieve_from_vector_store(query)

        # print("\n========== RAG RESULTS ==========")

        # for i, doc in enumerate(res):
        #     print(f"\n--- RESULT {i + 1} ---")
        #     print("SOURCE:", doc.metadata.get("source"))
        #     print("RESUME:", doc.metadata.get("resume"))
        #     print("CONTENT:")
        #     print(doc.page_content[:1000])

        return {
            "chunks": res
        }

    def extract_text_from_chunks(self, state: profileMatchingAgentState) -> str:
        
        res = state["chunks"]

        unique_resumes = defaultdict(list)
    
        for doc in res:
            source = doc.metadata.get("source")
            unique_resumes[source].append(doc.page_content)

        resume_text = "\n\n".join(
            f"Resume: {source}\n\n" + "\n".join(chunks)
            for source, chunks in unique_resumes.items()
        )
        return {
            "retrieved_resume_info" : resume_text
        }
    


    def select_resumes(self, state: profileMatchingAgentState) -> dict:

        json_parser = JsonOutputParser(pydantic_object = resumeInformationList)

        json_prompt = ChatPromptTemplate.from_messages(
            [("system","""You are a strict resume matching system.

                For each candidate, compare the job requirements against ONLY 
                the information explicitly present in that candidate's resume.


        {retrieved_resume_info}

        based on the job description :
        {job_req_skills}
        
        formatting instructions are:
        {format_instructions}

        Return a JSON array containing one object for each resume.
        Respond with only the JSON and no additional text.
        You MUST return exactly one JSON object for EVERY candidate listed above.
        If a candidate has no matching skills, still return that candidate with an empty matched_req list.

        IMPORTANT RULES:

        1. A skill can be placed in matched_req ONLY if it is explicitly stated in the candidate's resume.
        2. A skill must NOT be inferred from related technologies.
        Example: React does NOT imply Angular.
        JavaScript does NOT imply PHP.
        SQL does NOT imply MySQL.
        3. Do not transfer skills from one candidate to another.
        4. Do not use your general knowledge about a candidate or technology.
        5. If a requirement is not explicitly present, put it in missing_req.
        6. Evaluate each resume independently.
        7. The rank must be based only on the explicit matches.
        """)]
        )
        chain = json_prompt | self.llm | json_parser
        res = chain.invoke(
            {
                "retrieved_resume_info" : state["retrieved_resume_info"],
                "job_req_skills" : state["job_required_skills"],
                "format_instructions": json_parser.get_format_instructions()
            }
        )
        return {"selected_resume_info" : res}

    def agent_node(self, state: profileMatchingAgentState) -> dict:
        json_parser = JsonOutputParser(pydantic_object = AgentNextAction)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                        You are a helpful routing assistant.
                        Based on the feedback given by a resume reviewer : {feedback},
                        Choose what the next action should be.
                        The possible actions are : 
                        0."Retrive more resumes from the vector store"
                        1."Re-rank the candidates"
                        IMPORTANT : 
                        Only respond with either 0 or 1.
                        {format_instructions}

                    """
                )
            ]
        )
        chain = prompt | self.llm | json_parser
        res = chain.invoke({
            "format_instructions"  : json_parser.get_format_instructions(),
            "feedback" : state["feedback"]
        })
        
        return {
            "next_action" : res
        }


    
    def retrieve_more(self, state: profileMatchingAgentState) -> dict:

        tools = [self.rag_tool.retrieve_from_vector_store_mmr, self.rag_tool.retrieve_from_vector_store_similarity]

        prompt = ChatPromptTemplate.from_messages(
           [ 
            ("system", """
                You are chosen to retrieve more resumes from a vector store.
                Based on the feedback:
                {feedback}
                Use appropriate tools to retrieve more resumes from the vector store. 
                Choose the appropriate retrieval tool and formulate
                an appropriate search query.                
            """)       
            ]     
        )

        llm_with_tools = self.llm.bind_tools(tools)

        chain = prompt | llm_with_tools 

        res = chain.invoke({
            "feedback" : state["feedback"]
        })

        return {
            "messages" : [res]
        }





    
    def rank_resumes(self, state: profileMatchingAgentState) -> dict:

        json_parser = JsonOutputParser(pydantic_object = resumeInformationList)

        prompt = ChatPromptTemplate.from_messages(
            [      
                (
                "system",                     
                """
                You are ranking candidates for this job.

                Job requirements:
                {requirements}

                Candidate information:
                {resumes}

                Previous reviewer feedback:
                {feedback}                

                This is ranking iteration {iteration}.

                Re-evaluate the candidates using the reviewer feedback.
                Do not simply repeat the previous ranking.
                Explain what changed and why.

                Formatting instructions are:

                {format_instructions}
            """)
            ]
            
        )
        chain = prompt | self.llm | json_parser
        res = chain.invoke(
            {
                "requirements" : state["job_required_skills"],
                "resumes" : state["retrieved_resume_info"],
                "feedback" : state["feedback"],
                "iteration" : state["iteration"],
                "format_instructions" : json_parser.get_format_instructions()
            }
        )
        return {
            "iteration" : state["iteration"] + 1,
            "selected_resume_info" : res
        }
        

    def approve(self, state: profileMatchingAgentState) -> dict:
        # print("\n========== DATA SENT TO APPROVAL ==========")

        # for i, resume in enumerate(state["selected_resume_info"]):
        #     print(f"\nCandidate {i + 1}:")
        #     print(resume)
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You are reviewing candidate evaluation results.

                IMPORTANT:
                Use ONLY the information provided in the candidate data.
                Do not infer or invent skills, experience, qualifications,
                or technologies that are not explicitly present.

                Generate a very concise report, maximum 2 sentences per candidate.

                Selected candidates:
                {selected_resumes}

                If candidates do not satisfy any requirements, ignore them. 

                """
            )
        ])

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "selected_resumes" : state["selected_resume_info"]
            }
        )
        # print("\n========== RES . CONTENT ==========\n")
        if isinstance(response.content, list):
            plain_text = "".join([block.get("text", "") for block in response.content if isinstance(block, dict)])
        else:
            plain_text = response.content

        print(plain_text)

        ans = input("Please answer with YES or provide your feedback.\n")

        if ans.lower() == "yes":
            return {"approved" : True}
        
        return {
            "feedback" : [ans],
            "approved" : False
            }
        



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
            {
                "req": state["job_required_skills"],
                "info": state["selected_resume_info"]
            }
        )

        return {"output" : res}