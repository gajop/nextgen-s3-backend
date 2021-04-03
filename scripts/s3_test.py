import os
import boto3

from dotenv import load_dotenv

load_dotenv()

session = boto3.session.Session()
client = session.client('s3',
						region_name=os.getenv('SPACES_REGION_NAME'),
						endpoint_url=os.getenv('SPACES_ENDPOINT_URL'),
						aws_access_key_id=os.getenv('SPACES_KEY'),
						aws_secret_access_key=os.getenv('SPACES_SECRET'))

response = client.list_buckets()
for space in response['Buckets']:
	print(space['Name'])

response = client.list_objects(Bucket=os.getenv('SPACES_BUCKET'), Prefix='maps/')
# response = client.list_objects_v2(Bucket=os.getenv('SPACES_BUCKET'), Prefix='maps/')
for obj in response['Contents']:
	print(obj['Key'])