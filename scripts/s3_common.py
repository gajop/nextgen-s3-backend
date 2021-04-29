import boto3

from config import *

def make_client():
	session = boto3.session.Session()
	client = session.client('s3',
							region_name=SPACES_REGION_NAME,
							endpoint_url=SPACES_ENDPOINT_URL,
							aws_access_key_id=SPACES_KEY,
							aws_secret_access_key=SPACES_SECRET)

	return client