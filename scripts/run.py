import sys
import time
import traceback

from update_repos import run_clone
from repos import repos
from s3_upload import run_upload
from s3_remove import run_remove_repo
from config import *
from helpers import replace_with_empty

SLEEP_SECONDS = 60
SLEEP_SECONDS_BETWEEN_REPO = 5

def run(is_dry):
	should_upload_to_s3 = SPACES_ENDPOINT_URL is not None and SPACES_ENDPOINT_URL != ''
	while True:
		for repo in repos:
			try:
				repo_name = repo['name']
				first_run = not os.path.exists(f'pkg/{repo_name}')
				has_clone_updates = run_clone(repo)
				if should_upload_to_s3:
					if has_clone_updates:
						run_upload(repo_name, is_dry)
					if REMOVE_ON_UPLOAD and not is_dry:
						remove_pkg_on_upload(repo_name)
					run_remove_repo(repo)
				time.sleep(SLEEP_SECONDS_BETWEEN_REPO)
			except Exception:
				traceback.print_exc()
				continue
		print(f"Sleeping for {SLEEP_SECONDS} seconds...")
		time.sleep(SLEEP_SECONDS)

def remove_pkg_on_upload(repo_name):
	all_files = []
	pkg_folder = f'pkg/{repo_name}'
	for root, dir, files in os.walk(pkg_folder):
		newest_version_number = 0
		full_patches = []
		version_jsons = []
		for file in files:
			abs_path = os.path.join(root, file)
			if root.endswith('patch'):
				if file.startswith('0-'):
					full_patches.append(abs_path)
					if file.endswith('.json'):
						version_number = file.split('-')[1].split('.json')[0]
						version_number = int(version_number)
						if newest_version_number < version_number:
							newest_version_number = version_number
				elif file.endswith('.json'):
					version_jsons.append(abs_path)
				else:
					all_files.append(abs_path)
			elif file != 'latest.json':
				all_files.append(abs_path)

		all_files += [f for f in full_patches if not os.path.basename(f).startswith(f'0-{newest_version_number}')]
		version_jsons += [f for f in version_jsons if not os.path.basename(f) != '{newest_version_number}.json']



	for file in all_files:
		replace_with_empty(file)

if __name__ == "__main__":
	is_dry = False
	if len(sys.argv) > 1:
		is_dry = sys.argv[1] == "dry"
	run(is_dry)