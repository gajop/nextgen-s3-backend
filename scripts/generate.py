#!/bin/python

import os
from pathlib import Path
import fileinput
import json


from helpers import shell, maybe_make_archive_from_pkg, get_version_number, get_commit_history, checkout
from repos import repos
from config import *

REPO_DIR = 'repos/'

def run_generate(repo):
	repo_name = repo['name']
	repo_path = os.path.join(REPO_DIR, repo_name)

	history = get_commit_history(repo_path)
	history = history[-HISTORY_GENERATION_SIZE:]
	newest_version = get_version_number(repo_name)
	# Assuming linear history
	versions = [newest_version - i for i, sha in enumerate(history)]
	versions.reverse()
	channel = 'main'
	platform = 'any'

	baseUrl = f"pkg/{repo_name}/{channel}/{platform}"
	generated_one = False
	for i, new_sha in enumerate(history):
		new_ver = versions[i]
		if i == 0:
			continue

		old_ver = versions[i - 1]
		old_sha = history[i - 1]

		was_generated = generate(repo_name, repo_path, baseUrl, old_ver, new_ver, old_sha, new_sha)
		if was_generated:
			generated_one = True

	for file in os.listdir('output'):
		os.remove(os.path.join('output', file))

	return generated_one

def generate(baseUrl, old_version_number, new_version_number):
	up_diff = f'{baseUrl}/patch/{old_version_number}-{new_version_number}'
	down_diff = f'{baseUrl}/patch/{new_version_number}-{old_version_number}'
	if os.path.exists(up_diff) and os.path.exists(down_diff):
		return False

	archive, _ = maybe_make_archive_from_pkg(baseUrl, new_version_number, 'output')
	old_archive, _ = maybe_make_archive_from_pkg(baseUrl, old_version_number, 'output')

	new_name = os.path.basename(archive)
	old_name = os.path.basename(old_archive)

	make_diff(old_archive, archive, up_diff, old_version_number, new_version_number, new_name)
	make_diff(archive, old_archive, down_diff, new_version_number, old_version_number, old_name)
	os.remove(old_archive)

	return True

def make_diff(old_archive, new_archive, diff_path, old_version, new_version, name):
	Path(diff_path).parent.mkdir(parents=True, exist_ok=True)
	shell(['./butler', 'diff', old_archive, new_archive, diff_path])

	patch_json = {
		'name': name,
		'size': Path(diff_path).stat().st_size,
		'sig_size': Path(diff_path + ".sig").stat().st_size,
	}
	patch_json_path = f'{Path(diff_path).parent}/{old_version}-{new_version}.json'

	with open(patch_json_path, 'w') as outfile:
		json.dump(patch_json, outfile)

	make_version_info(diff_path, new_version, name)

def make_version_info(diff_path, new_version, name):
	Path(diff_path).parent.mkdir(parents=True, exist_ok=True)

	version_json = {
		'name': name
	}
	version_json_path = f'{Path(diff_path).parent}/{new_version}.json'

	with open(version_json_path, 'w') as outfile:
		json.dump(version_json, outfile)

if __name__ == '__main__':
	for repo in repos:
		run_generate(repo)

