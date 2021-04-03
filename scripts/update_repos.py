#!/bin/python

import os
from pathlib import Path
import json

from helpers import shell, maybe_make_archive, get_version_number
from repos import repos
from generate import make_diff

REPO_DIR = 'repos/'

def run_clone(repo):
	repo_name = repo['name']
	repo_path = os.path.join(REPO_DIR, repo_name)
	channel = 'main'
	platform = 'any'

	clone(repo['url'], repo_path)

	version = get_version_number(repo_path)

	baseUrl = f"{repo_name}/{channel}/{platform}"
	archive, is_new_archive = maybe_make_archive(repo_path, 'output')
	diff_path = f"pkg/{baseUrl}/patch/0-{version}"
	if not os.path.exists(diff_path):
		make_diff("/dev/null", archive, diff_path, 0, version, repo_name)

	package_info = repo
	update_package_info(package_info, f'pkg/{repo_name}/package-info.json')

	update_latest_json(f'pkg/{repo_name}/{channel}/{platform}/latest.json', os.path.basename(archive), version)

	# if os.path.exists(archive):
	# 	os.remove(archive)

	return is_new_archive

def clone(git_url, clone_path):
	if os.path.exists(clone_path):
		pull_existing(clone_path)
	else:
		clone_new(git_url, clone_path)
	update_submodules(clone_path)

def pull_existing(clone_path):
	shell(['git', 'checkout', 'master'], cwd=clone_path)
	shell(['git', 'pull', '--rebase'], cwd=clone_path)

def clone_new(git_url, clone_path):
	Path(clone_path).mkdir(parents=True, exist_ok=True)
	shell(['git', 'init'], cwd=clone_path)
	shell(['git', 'remote', 'add', '-f', 'origin', git_url], cwd=clone_path)
	shell(['git', 'checkout', 'master'], cwd=clone_path)

def update_submodules(clone_path):
	shell(['git', 'submodule', 'init'], cwd=clone_path)
	shell(['git', 'submodule', 'update'], cwd=clone_path)

def update_package_info(package_info, dest):
	with open(dest, 'w') as outfile:
		json.dump(package_info, outfile, sort_keys=True, indent=2)

def update_latest_json(dest, name, version):
	with open(dest, 'w') as outfile:
		json.dump({
			'version': version,
			'name': name
		}, outfile, sort_keys=True, indent=2)

if __name__ == '__main__':
	for repo in repos:
		run_clone(repo)

