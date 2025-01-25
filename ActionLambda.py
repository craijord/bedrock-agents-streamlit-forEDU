import json
import pandas as pd


import boto3
import os




def lambda_handler(event, context):
    print(event)

    # Mock data for demonstration purposes
    bottom3_concern = [
        {
            "college_id": "CC",
            "student_id": 128412,
            "first_name": "Wynter-Violet",
            "last_name": "Lalumia",
            "email_address": "Wynter-Violet.Lalumia_811@example.com",
            "phone_number": "555-XXX-XXXX",
            "declared_program": "CCPARAAS",
            "declared_degree": "AS",
            "declared_major": "Paralegal Studies",
            "major_name": "Paralegal Studies",
            "student_class": "First year",
            "graduate_year": 2026,
            "current_gpa": 3.12,
            "credits_earned": 12,
            "curr_alignment_score": 39,
            "next_alignment_score": 41,
            "poss_alignment_score": 80
        },
        {
            "college_id": "CC",
            "student_id": 129398,
            "first_name": "Jasmin",
            "last_name": "Wilby",
            "email_address": "Jasmin.Wilby_975@example.com",
            "phone_number": "555-XXX-XXXX",
            "declared_program": "CGWLDTAS",
            "declared_degree": "AS",
            "declared_major": "Welding Tech",
            "major_name": "Welding Tech",
            "student_class": "Second year",
            "graduate_year": 2025,
            "current_gpa": 3.66,
            "credits_earned": 54,
            "curr_alignment_score": 61,
            "next_alignment_score": 63,
            "poss_alignment_score": 81
        },
        {
            "college_id": "CC",
            "student_id": 132811,
            "first_name": "Irvine",
            "last_name": "Boneparte",
            "email_address": "Irvine.Boneparte_363@example.com",
            "phone_number": "555-XXX-XXXX",
            "declared_program": "CGVNRSAS",
            "declared_degree": "AS",
            "declared_major": "Vocational Nursing",
            "major_name": "Vocational Nursing",
            "student_class": "First year",
            "graduate_year": 2026,
            "current_gpa": 3.11,
            "credits_earned": 21,
            "curr_alignment_score": 31,
            "next_alignment_score": 33,
            "poss_alignment_score": 58
        }
        ]


    def get_named_parameter(event, name):
        return next(item for item in event['parameters'] if item['name'] == name)['value']

    def get_named_property(event, name):
        return next(item for item in event['requestBody']['content']['application/json']['properties'] if item['name'] == name)['value']

    def getPriorityStudents(event):
        return bottom3_concern
    
    def getStudentProfile(event, student_id):
        for student in bottom3_concern:
            if student['student_id'] == int(student_id):
                return student

        return "No student found with the given ID." + student_id

    def getCourseList(event, context):
        # Initialize Lambda client
        lambda_client = boto3.client('lambda')
        
        try:
            # Call the getCourseList Lambda function
            response = lambda_client.invoke(
                FunctionName='getCourseList',
                InvocationType='RequestResponse',  # Synchronous invocation
                Payload=json.dumps(event)  # Pass through the original event
            )
            
            # Read and parse the response payload
            response_payload = json.loads(response['Payload'].read())
            
            return response_payload
            
        except Exception as e:
            print("FAILED IN SECOND INVOKE")
            print(e)
            e
    
      
    result = ''
    response_code = 200
    action_group = event['actionGroup']
    api_path = event['apiPath']
    
    print("api_path: ", api_path )
    
    if api_path == '/bottom3':
        result = getPriorityStudents(event)
    elif api_path == '/student':
        student_id = get_named_parameter(event, 'student_id')
        result = getStudentProfile(event, student_id)
    elif api_path == '/recommended_courses':
        result = getCourseList(event, context)
    else:
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"
        
    response_body = {
        'application/json': {
            'body': result
        }
    }
        
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': response_code,
        'responseBody': response_body
    }

    api_response = {'messageVersion': '1.0', 'response': action_response}
    return api_response

