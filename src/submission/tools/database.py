from collections import defaultdict
import json
from langchain_core.tools import tool
from sqlalchemy import CursorResult, text
from src.static.util import ENGINE
from typing import Literal
import re


def execute_query(query: str) -> CursorResult:
    """
    Function that really executes a query on the database

    Args:
        query str to be executed

    Returns:
        CursorResult: the results of the query or raise and exception
    """

    record_limiters = ['count', 'where', 'limit', 'distinct', 'having', 'group by']

    with ENGINE.connect() as connection:
        try:
            lq = query.strip().lower()
            if not any(word in lq for word in record_limiters):
                print("WARNING! Query you are performing has no limitation!\n" + 
                      "This can cause the kernel to crash in case of large output.")

            res = connection.execute(text(query))

            return res
        except Exception as e:
            print(f'Wrong query, encountered exception {e}.')
            raise e


@tool('query_database')
def query_database(query: str) -> str:
    """Query the PIRLS postgres database and return the results as a string.

    Args:
        query (str): The SQL query to execute.

    Returns:
        str: The results of the query as a string, where each row is separated by a newline.

    Raises:
        Exception: If the query is invalid or encounters an exception during execution.
    """
    res = execute_query(query)
    ret = '\n'.join(", ".join(map(str, result)) for result in res)
    return f'Query: {query}\nResult:\n{ret}'


@tool('get_schema_of_given_table')
def get_schema_of_given_table(
    table_name: str
) -> str:
    """
    Retrieves the schema information for a given table from the database.

    Args:
        table_name (str): The name of the table for which to retrieve the schema information.

    Returns:
        str: A string containing the schema information, with each column on a new line in the format:
             (Column: column_name, Data Type: data_type)
             If an error occurs during execution, it returns an error message instead.
    """

    query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = LOWER('{table_name}')"

    res = execute_query(query)

    return '\n'.join(map(lambda value: f'(Column: {value[0]}, Data Type: {value[1]})', res))


@tool('get_question_types')
def get_question_types(
    table_name: Literal['studentquestionnaireentries', 'curriculumquestionnaireentries', 'homequestionnaireentries', 'teacherquestionnaireentries', 'schoolquestionnaireentries'],
) -> str:
    """
    Retrieve questions types from the given table.

    Args:
        table_name (str): The name of the table to query.

    Returns:
        str: A string containing the values, each formatted as "(Type: <type>)\n".
             If an error occurs during query execution, it returns an error message.
    """
    
    query = f'SELECT DISTINCT type FROM {table_name}'

    res = execute_query(query)

    # Teacher questionnaire types have these chars that need to be handled
    carriage_return=("\r\n","\\r\\n")

    return '\n'.join(map(lambda value: f'(Type: {value[0].replace(*carriage_return)})', res))


@tool('get_questions')
def get_questions(
    table_name: Literal['studentquestionnaireentries', 'curriculumquestionnaireentries', 'homequestionnaireentries', 'teacherquestionnaireentries', 'schoolquestionnaireentries'],
    types: list[str] = []
) -> str:
    """
    Retrieve questions from the given table, filtering by 'types'.
    No filtering is applied if 'types' is an empty list.

    Args:
        table_name (str): The name of the table to query
        question_type (list[str]): The question types

    Returns:
        str: A string containing the values, each formatted as "(Code: <code>, Question: <question>)\n".
             If an error occurs during query execution, it returns an error message.
    """

    # Teacher questionnaire types have these chars that need to be handled
    carriage_return=("\\r\\n","\r\n")
    singleton_tuple=(",)",")")

    where_clause = f"WHERE type IN {str(tuple(types)).replace(*singleton_tuple).replace(*carriage_return)}" if types else ""

    query = f'SELECT code, question FROM {table_name} {where_clause}'

    res = execute_query(query)

    return '\n'.join(map(lambda value: f'(Code: {value[0]}, Question: {value[1]})', res))


@tool('get_answers')
def get_answers(
    table_name: Literal['studentquestionnaireanswers', 'curriculumquestionnaireanswers', 'homequestionnaireanswers', 'teacherquestionnaireanswers', 'schoolquestionnaireanswers'],
    codes: list[str]
) -> str:
    """
    Retrieve answers to questions relative to 'codes' from the given table.

    Args:
        table_name (str): The name of the table to query
        codes (list[str]): The question codes

    Returns:
        str: A JSON object with the answers for each provided question, in the format
        {
            "<code>": [
                "<answer_1>",
                "<answer_2>",
                ...
            ],
            ...
        }
        If an error occurs during query execution, it returns an error message.
    """

    singleton_tuple=(",)",")")
    
    query = f"SELECT DISTINCT code, answer FROM {table_name} WHERE code IN {str(tuple(codes)).replace(*singleton_tuple)}"

    res = execute_query(query)
    qa = defaultdict(list)

    for code, answer in res:
        qa[code].append(answer)

    return json.dumps(qa, indent=2, ensure_ascii=False)


@tool('get_benchmark_scores')
def get_benchmark_scores() -> str:
    """
    Retrieve benchmarks with relative score to reach them.

    Returns:
        str: A string containing the values, each formatted as "(Name: <name>, Score: <score>)\n".
             If an error occurs during query execution, it returns an error message.
    """
    
    query = "SELECT name, score FROM benchmarks"

    res = execute_query(query)
    
    return '\n'.join(map(lambda value: f'(Name: {value[0]}, Score: {value[1]})', res))

@tool('get_score_metrics')
def get_score_metrics() -> str:
    """
    Retrieve score metrics with relative code.

    Returns:
        str: A string containing the values, each formatted as "(Name: <metric>, Code: <code>)\n".
             If an error occurs during query execution, it returns an error message.
    """
    
    query = "SELECT name, code FROM studentscoreentries"

    res = execute_query(query)  
    
    return '\n'.join(map(lambda value: f'(Name: {value[0]}, Code: {value[1]})', res))

@tool('get_countries')
def get_countries() -> str:
    """
    Retrieve countries with relative code and id.

    Returns:
        str: A string containing the values, each formatted as "(Name: <country>, Code: <code>, Country_Id: <id>)\n".
             If an error occurs during query execution, it returns an error message.
    """
    
    query = "SELECT name, code, country_id FROM countries"

    res = execute_query(query)
    
    return '\n'.join(map(lambda value: f'(Name: {value[0]}, Code: {value[1]}, Country_Id: {value[2]})', res))

