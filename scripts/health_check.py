from tqdm import tqdm

from helpers import shell, maybe_make_archive, get_version_number, get_commit_history, checkout
from helpers import set_shells_silent, get_spring_version_number
from repos import repos
from config import *

import json

byar_chobby = json.load(open('./out.json', 'r'))

REPO_DIR = 'repos/'

# TODO:
# Health check:
# Version -> Archive version (i.e. rapid version)
# All versions are unique
# Version <-> Archive version bijective mapping
# Version goes from 0 to X, no missing element
# All rapid versions are present

def run_healthcheck(repo):
	set_shells_silent(True)

	repo_name = repo['name']
	repo_path = os.path.join(REPO_DIR, repo_name)

	history = get_commit_history(repo_path)
	history = history[-(HISTORY_GENERATION_SIZE + 1):]

	newest_version = get_version_number(repo_name)
	# Assuming linear history
	versions = [newest_version - i for i, sha in enumerate(history)]
	versions.reverse()

	actual_versions = []

	print(byar_chobby)
	if repo_name == "beyond-all-reason/BYAR-Chobby":
		for i, version in enumerate(versions):
			sha = history[i]
			checkout(repo_path, sha)
			archive_number = str(get_spring_version_number(repo_path))
			print(version, archive_number)
			if archive_number not in byar_chobby:
				print(f"Version not found: {archive_number}")
			# print(byar_chobby[str(version)], sha)
	return

	print(f'Checking {repo_path}...')
	for i, new_sha in enumerate(tqdm(history)):
		new_ver = versions[i]

		try:
			checkout(repo_path, new_sha)
		except Exception as e:
			print(e)
			actual_versions.append(-1)
		version_number = get_version_number(repo_name)
		actual_versions.append(version_number)

	if actual_versions != versions:
		print("ERROR: Actual and expected versions are different!")
		if len(actual_versions) != len(versions):
			print(f"Length is different: {len(actual_versions)} != {len(versions)}")
		for i in range(min(len(actual_versions), len(versions))):
			if actual_versions[i] != versions[i]:
				print(f"{i}: {actual_versions[i]} (actual) != {versions[i]} (expected)")
	else:
		print("OK!")

	set_shells_silent(False)

def run_all_healthchecks():
	for repo in repos:
		run_healthcheck(repo)

if __name__ == "__main__":
	run_all_healthchecks()