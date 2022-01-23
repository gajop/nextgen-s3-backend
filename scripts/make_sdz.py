#!/bin/python

import os
from pathlib import Path
import json
import argparse

from helpers import shell, maybe_make_archive_from_git

# dest is where you want to keep your games (you may want to clean this periodically)
# rapid is the rapid file location (e.g. ~/.spring/rapid/repos.springrts.com/byar/versions.gz)
def clone_and_make_sdz(repo, repo_path, output, force):
	clone(repo, repo_path)
	maybe_make_archive_from_git(repo_path, output, force)

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
	parser = argparse.ArgumentParser(description='Make Spring .sdz archive from Git repository.')
	parser.add_argument('--repo', help='Git repository', required=True)
	parser.add_argument('--clone-path', help='Local clone folder', required=True)
	parser.add_argument('--output', help='Output folder', required=True)
	parser.add_argument('--force', help='Force folder generation', required=False, default=False, action='store_true')
	args = parser.parse_args()

	clone_and_make_sdz(args.repo, args.clone_path, args.output, args.force)

