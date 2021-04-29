import os
import sys
from pathlib import Path

from helpers import replace_with_empty
from config import *
from s3_common import make_client

def upload_dir(dir):
	client = make_client()
	sync_dir(client, dir)

def get_upload_list(name, existing_objects):
	pkg_folder = f'pkg/{name}'
	patches = []
	patch_jsons = []
	package_jsons = []
	for root, dir, files in os.walk(pkg_folder):
		for file in files:
			absPath = os.path.join(root, file)
			# TODO: make a better algorithm to figure out what to upload and when
			if Path(absPath).stat().st_size == 0:
				continue

			if root.endswith('patch'):
				if file.endswith('.json'):
					patch_jsons.append(absPath)
				else:
					patches.append(absPath)
			else:
				package_jsons.append(absPath)

	bef_patches_len = len(patches)
	bef_patch_jsons_len = len(patch_jsons)

	patches = [o for o in patches if o not in existing_objects]
	patch_jsons = [o for o in patch_jsons if o not in existing_objects]

	print(f"Uploading {len(patches)} ({bef_patches_len - len(patches)} omitted) patches, " +
		f"{len(patch_jsons)} ({bef_patch_jsons_len - len(patch_jsons)} omitted) patch jsons, " +
		f"and {len(package_jsons)} package jsons")

	return {
		'patches': patches,
		'patch_jsons': patch_jsons,
		'package_jsons': package_jsons
	}

def upload_files(client, repo_name, files, is_dry):
	file_categories = ['patches', 'patch_jsons', 'package_jsons']
	total_uploads = 0
	for cat in file_categories:
		total_uploads += len(files[cat])
		for file_name in files[cat]:
			if not file_name.startswith(f'pkg/{repo_name}'):
				print(f"Invalid file: {file_name}. Won't upload")
				return

	if is_dry:
		print("No upload (dry run)")
	else:
		print("Starting upload")
	upload_number = 1
	for cat in file_categories:
		ExtraArgs = { 'ACL': 'public-read' }
		if cat in ['patches', 'patch_jsons']:
			ExtraArgs['CacheControl'] = 'public,max-age=604800,immutable'
		else:
			ExtraArgs['CacheControl'] = 'no-store, max-age=0'

		for file_name in files[cat]:
			print(f"Uploading {upload_number}/{total_uploads} {file_name}...")
			if not is_dry:
				client.upload_file(file_name, SPACES_BUCKET, file_name, ExtraArgs=ExtraArgs)
			upload_number += 1

def get_existing_objects(client, repo_name):
	response = client.list_objects(Bucket=SPACES_BUCKET, Prefix=f'pkg/{repo_name}')
	if 'Contents' not in response:
		return []
	return [obj['Key'] for obj in response['Contents']]

def run_upload(repo_name, is_dry):
	client = make_client()
	existing_objects = get_existing_objects(client, repo_name)
	files = get_upload_list(repo_name, existing_objects)
	upload_files(client, repo_name, files, is_dry)

def run():
	if len(sys.argv) < 2:
		print('missing repo name')
		return
	run_upload(sys.argv[1], False)

if __name__ == '__main__':
	run()