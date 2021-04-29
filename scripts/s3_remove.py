import heapq

from s3_common import make_client
from config import *
from repos import repos

def get_existing_full_patches(client, repo_name, channel, platform):
	prefix = f'pkg/{repo_name}/{channel}/{platform}/patch/0-'
	response = client.list_objects(Bucket=SPACES_BUCKET, Prefix=prefix)
	if 'Contents' not in response:
		return []
	return [obj['Key'] for obj in response['Contents']]

def group_into_versions(files):
	file_versions = {}
	for f in files:
		version = f.split('0-')
		version = version[len(version) - 1]
		if "." in version:
			version = version.split(".")[0]
		version = int(version)
		if version not in file_versions:
			file_versions[version] = []
		file_versions[version] = f
	return file_versions

def get_files_to_delete(file_versions):
	largest_keys = heapq.nlargest(2, file_versions.keys())
	return [files for version, files in file_versions.items() if version not in largest_keys]

def delete_files(client, files):
	delete_objects = []
	for f in files:
		delete_objects.append({'Key': f})
	response = client.delete_objects(Bucket=SPACES_BUCKET, Delete={
		'Objects': delete_objects
	})
	print(response)

def run_remove(repo_name, channel, platform):
	client = make_client()
	existing = get_existing_full_patches(client, repo_name, channel, platform)
	file_versions = group_into_versions(existing)
	files_to_delete = get_files_to_delete(file_versions)

	if len(files_to_delete) != 0:
		print(f"Deleting old files: {files_to_delete}")
		delete_files(client, files_to_delete)

def run_remove_repo(repo):
	for channel, platforms in repo["channels"].items():
		for platform in platforms:
			run_remove(repo['name'], channel, platform)

def remove_all():
	for repo in repos:
		run_remove_repo(repo)

if __name__ == "__main__":
	remove_all()