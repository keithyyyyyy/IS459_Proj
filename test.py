import boto3
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
access_key_id = os.getenv("ACCESS_KEY_ID")
secret_access_key = os.getenv("SECRET_ACCESS_KEY")

bucket_name = 'is459-t3-job-transformed-data'
google_object_key = "google_transformed"
nodeflair_object_key = 'nodeflair_transformed/jobs.csv'
nodeflair_file_name = "jobs.csv"

s3 = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

# print(s3.get_object(Bucket=bucket_name, Key=nodeflair_object_key)['Body'].read().decode('utf-8'))

# with open(data, "r") as file1:
#     read_content = file1.read()
#     print(read_content)


jobs_df = pd.read_csv(s3.get_object(Bucket=bucket_name, Key=nodeflair_object_key)['Body'])
print(jobs_df.sample(10))