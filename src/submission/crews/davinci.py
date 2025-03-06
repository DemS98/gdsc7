from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.static.submission import Submission
from src.static.util import PROJECT_ROOT
import src.submission.tools.database as db_tools
import src.submission.tools.plot as plot_tools
import src.submission.tools.external as ext_tools


@CrewBase
class DaVinciCrew(Submission):
    """Data Analysis Crew for the GDSC project."""
    # Load the files from the config directory
    agents_config = PROJECT_ROOT / 'submission' / 'config' / 'davinci' / 'agents.yaml'
    tasks_config = PROJECT_ROOT / 'submission' / 'config' / 'davinci' / 'tasks.yaml'

    def __init__(self, llm):
        self.llm = llm

    def run(self, prompt: str) -> str:
        return self.crew().kickoff(inputs={'user_question': prompt}).raw

    @agent
    def prompt_analyzer(self) -> Agent:
        a = Agent(
            config=self.agents_config['prompt_analyzer'],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )
        return a

    @agent
    def query_creator(self) -> Agent:
        a = Agent(
            config=self.agents_config['query_creator'],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )
        return a
    
    @agent
    def data_searcher(self) -> Agent:
        a = Agent(
            config=self.agents_config['data_searcher'],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )
        return a
    
    @agent
    def data_visualizer(self) -> Agent:
        a = Agent(
            config=self.agents_config['data_visualizer'],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )
        return a
       
    @agent
    def lead_data_analyst(self) -> Agent:
        a = Agent(
            config=self.agents_config['lead_data_analyst'],
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )
        return a
    
    @task
    def analyze_prompt_task(self) -> Task:
        t = Task(
            config=self.tasks_config['analyze_prompt_task'],
            tools= [
                db_tools.get_schema_of_given_table,
                db_tools.get_question_types,
                db_tools.get_questions,
                db_tools.get_answers,
                db_tools.get_benchmark_scores,
                db_tools.get_score_metrics,
                db_tools.get_countries
            ],
        )
        return t

    @task
    def create_query_task(self) -> Task:
        t = Task(
            config=self.tasks_config['create_query_task'],
            context=[self.analyze_prompt_task()],
            tools=[
                db_tools.query_database
            ]
        )
        return t
    
    @task
    def search_external_task(self) -> Task:
        t = Task(
            config=self.tasks_config['search_external_task'],
            context=[self.analyze_prompt_task(), self.create_query_task()],
            tools=[
                ext_tools.get_indicators_data,
                ext_tools.get_previous_pirls_scores,
                db_tools.get_countries
            ]
        )
        return t
    
    @task
    def create_plots_task(self) -> Task:
        t = Task(
            config=self.tasks_config['create_plots_task'],
            context=[self.create_query_task(), self.search_external_task()],
            tools=[
                plot_tools.generate_plot
            ]
        )
        return t

    @task
    def answer_question_task(self) -> Task:
        t = Task(
            context=[self.create_query_task(), self.search_external_task(), self.create_plots_task()],
            config=self.tasks_config['answer_question_task'],
        )
        return t

    @crew
    def crew(self) -> Crew:
        """Creates the data analyst crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_iter=5,
            cache=True
        )
