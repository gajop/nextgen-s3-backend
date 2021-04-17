#!/bin/python

import os
from pathlib import Path
import json

from helpers import shell, maybe_make_archive_from_git, get_version_number, get_spring_name, get_spring_version
from helpers import get_git_hash
from repos import repos
from generate import make_diff, generate
from versions import make_connection, create_tables, insert_versions

REPO_DIR = 'repos/'

def run_clone(repo):
	repo_name = repo['name']
	repo_path = os.path.join(REPO_DIR, repo_name)
	channel = 'main'
	platform = 'any'

	old_hash = None
	if os.path.exists(repo_path):
		old_hash = get_git_hash(repo_path)
	clone(repo['url'], repo_path)
	new_hash = get_git_hash(repo_path)

	old_version_number = get_version_number(repo_name, channel, platform)
	new_version_number = old_version_number + 1

	if old_hash == new_hash and old_version_number != 0:
		return False

	spring_name = get_spring_name(repo_path).strip()
	spring_version = get_spring_version(repo_path)

	baseUrl = f"pkg/{repo_name}/{channel}/{platform}"
	diff_path = f"{baseUrl}/patch/0-{new_version_number}"
	if os.path.exists(diff_path):
		return False

	archive, _ = maybe_make_archive_from_git(repo_path, 'output')
	archive_name = os.path.basename(archive)
	make_diff("/dev/null", archive, diff_path, 0, new_version_number, archive_name)

	package_info = repo
	write_json_to_file(f'pkg/{repo_name}/package-info.json', package_info)

	write_json_to_file(f'pkg/{repo_name}/{channel}/{platform}/latest.json',
		{
			'version': new_version_number,
			'name': archive_name
		}
	)

	if old_version_number != 0:
		generate(baseUrl, old_version_number, new_version_number)

	con = make_connection()
	create_tables(con)
	insert_versions(con, [(
		f"{spring_name} {spring_version}",
		f"{repo_name}@{channel}:{new_version_number}"
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

def write_json_to_file(file, obj):
	with open(file, 'w') as outfile:
		json.dump(obj, outfile, sort_keys=True, indent=2)

if __name__ == '__main__':
	for repo in repos:
		run_clone(repo)

