import time
#from IPython.display import display, clear_output

#import jsonlines
import boto3
from datetime import datetime

import pandas as pd
import json
#import numpy as np

import math
#from numpy.linalg import norm
import subprocess
from pyathena import connect
    
target_s3_bucket             = "guided-pathways-demo-us-east-1-339712923430"    # The name of the bucket where intermediate and final results should be stored
raw_data_db                  = "gp_raw_data"  # The name of the Glue Data Catalog that contains the raw input data
min_degree_count             = 25
model_build_date             = '2024-05-09'
vector_size                  = 2000


log_level         = "verbose" # | "verbose" | errors

## S3 buckets & prefixes
s3_output_path    = f"s3://{target_s3_bucket}/temp_athena_output"

#model_s3_loc      = "model_output/college_code={}/{}".format(college_code.lower(),datetime.now().strftime('%Y-%m-%d'))
model_s3_loc      = f"/model/model_build_{model_build_date}"
s3_model_path     = f"s3://{target_s3_bucket}{model_s3_loc}"
s3_model_tables_path = f"s3://{target_s3_bucket}/model/tables/"

## Glue data catalog databases
inference_db      = "gp_infer"
model_build_db    = "gp_build" 

inference_s3_loc  = f"s3://{target_s3_bucket}/inference/"
    
def execute_athena_query(query, database, s3_output_path):

    print("LOG | Opening connection to Athena")
    connection = connect(
        s3_staging_dir=s3_output_path,
        region_name=region_to_use,
        schema_name=database
    )
    cursor = connection.cursor()
    if (log_level == "verbose") :
        print("LOG | Executing query\n    | {query}".format(query = query.strip().replace("\n", "\n    |  ")))
    cursor.execute(query)
    cursor.close()
    connection.close()

    if (log_level == "verbose") :
        print("    |")
    print("LOG | Query executed successfully.")


def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']

    
def lambda_handler(event, context):
    print("event: ", event)
    
    headers = event.get('headers', {})
    my_session    = boto3.session.Session()
    region_to_use = my_session.region_name
    print(my_session.region_name)
    conn = connect(s3_staging_dir=s3_output_path, region_name=region_to_use)

    try:
        api = event['apiPath']
        print(f"API = {api}")
        curr_student_id = get_named_parameter(event, 'student_id')
        print(f"Student_id = {curr_student_id}")
        view = 'recommended_courses' #get_named_parameter(event, 'course_type')
        college_code = 'CC'
        query = f"""
            select 
                college_id, 
                program, 
                substr(course_id,1,4) || ' ' || substr(course_id,5,4) as course_id, 
                course_subject, 
                course_subject_desc, 
                course_name 
            from gp_api_materialized.recommended_courses 
            where student_id = {curr_student_id}
        """

    except:
        view = headers.get('view')
        college_code = headers.get('college_code')  # Get the college code from headers
        curr_student_id = int(headers.get('curr_student_id'))
        query = f"""SELECT * FROM gp_api.{view} WHERE student_id ={curr_student_id} and college_id = '{college_code}'"""

    print(college_code)
    print(curr_student_id)
    
    cohort_data = pd.read_sql(query, conn)
    cohort_data = pd.DataFrame(cohort_data)
    # Convert DataFrame to a list of dictionaries
    cohort_data = cohort_data.to_dict(orient='records')
        
    print("Data", cohort_data)
    print(json.dumps(cohort_data))

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,view,college_code,curr_student_id',
            'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT,ANY'
        },
        'body': json.dumps(cohort_data)
    }

