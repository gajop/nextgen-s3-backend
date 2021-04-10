#!/bin/python

import os
from pathlib import Path
import json

from helpers import shell, maybe_make_archive, get_version_number, get_spring_name, get_spring_version, get_commit_history
from repos import repos
from generate import make_diff, generate
from versions import make_connection, create_tables, insert_versions

REPO_DIR = 'repos/'

def run_clone(repo):
	repo_name = repo['name']
	repo_path = os.path.join(REPO_DIR, repo_name)
	channel = 'main'
	platform = 'any'

	clone(repo['url'], repo_path)

	version_number = get_version_number(repo_path)

	baseUrl = f"{repo_name}/{channel}/{platform}"
	diff_path = f"pkg/{baseUrl}/patch/0-{version_number}"
	if os.path.exists(diff_path):
		return False

	archive, _ = maybe_make_archive(repo_path, 'output')
	make_diff("/dev/null", archive, diff_path, 0, version_number, repo_name)

	package_info = repo
	update_package_info(package_info, f'pkg/{repo_name}/package-info.json')

	update_latest_json(f'pkg/{repo_name}/{channel}/{platform}/latest.json', os.path.basename(archive), version_number)

	# TODO: don't rely on git for old versions, use our system
	history = get_commit_history(repo_path)
	if len(history) <= 1:
		new_sha = history[-1]
		old_sha = history[-2]
		generate(repo_name, repo_path, baseUrl, version_number - 1, version_number, old_sha, new_sha)

	con = make_connection()
	create_tables(con)
	spring_name = get_spring_name(repo_path).strip()
	spring_version = get_spring_version(repo_path)
	insert_versions(con, [(
		f"{spring_name} {spring_version}",
		f"{repo_name}@{channel}:{version_number}"
	)])

	if os.path.exists(archive):
		os.remove(archive)

	return True

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

