import sys
import time
import traceback

from update_repos import run_clone
from repos import repos
from generate import run_generate
from s3_upload import run_upload
from versions import run_versions
from config import *
from helpers import replace_with_empty

SLEEP_SECONDS = 60

def run(is_dry):
	while True:
		for repo in repos:
			try:
				repo_name = repo['name']
				first_run = not os.path.exists(f'pkg/{repo_name}')
				has_clone_updates = run_clone(repo)
				if first_run:
					run_generate(repo)
					run_versions(repo)
				if has_clone_updates:
					run_upload(repo_name, is_dry)
				if REMOVE_ON_UPLOAD and not is_dry:
					remove_pkg_on_upload(repo_name)
			except Exception:
				traceback.print_exc()
				continue
		print(f"Sleeping for {SLEEP_SECONDS} seconds...")
		time.sleep(SLEEP_SECONDS)

def remove_pkg_on_upload(repo_name):
	all_files = []
	pkg_folder = f'pkg/{repo_name}'
	for root, dir, files in os.walk(pkg_folder):
		for file in files:
			absPath = os.path.join(root, file)
			if root.endswith('patch'):
				if file.endswith('.json'):
					all_files.append(absPath)
				else:
					all_files.append(absPath)
			else:
				all_files.append(absPath)

	for file in all_files:
		replace_with_empty(file)

if __name__ == "__main__":
	is_dry = False
	if len(sys.argv) > 1:
		is_dry = sys.argv[1] == "dry"
	run(is_dry)