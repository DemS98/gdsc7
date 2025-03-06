import os
import boto3
from botocore.exceptions import ClientError

from datetime import datetime as date, timezone

from langchain_core.tools import tool

from src.static.util import S3_BUCKET_NAME

S3_BUCKET_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com"

def save_to_s3(file_path: str) -> str | None:
    s3_client = boto3.client('s3')

    now = date.now(timezone.utc)

    key = f"{now.year}/{now.month}/{now.day}/{now.hour}/{os.path.basename(file_path)}"

    try:
        s3_client.upload_file(file_path, S3_BUCKET, key)
        return f"{S3_BUCKET_BASE_URL}/{key}"
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return None

@tool("generate_plot")
def generate_plot(matplotlib_code: str) -> str:
    """
    Function that executes the given matplotlib code for generating a plot and returns the URL to the plot file.

    Args:
        matplotlib_code (str): string containing the Python matplotlib code to execute for generating the plot

    Returns:
        str: the generated plot image URL or "ERROR" if there was an error generating the plot
    """
    
    globs = {}

    try:
        exec(matplotlib_code, globs)

        if "FILENAME" not in globs:
            return "ERROR"
        
        file_path = globs["FILENAME"]
        
        return save_to_s3(file_path) or "ERROR"
    finally:
        file_path = globs.get("FILENAME", None)

        if file_path:
            os.remove(file_path)