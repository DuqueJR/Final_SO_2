import boto3
from config import AWS_BUCKET

s3 = boto3.client("s3")
BUCKET = AWS_BUCKET