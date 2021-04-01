#!/bin/python

import os
import shutil

from helpers import shell, maybe_make_archive, get_version_number, get_commit_history, checkout
from repos import repos

def run_butler_apply():
	for repo in repos:
		repo_name = repo['name']
		repo_path = os.path.join(REPO_DIR, repo_name)

		history = get_commit_history(repo_path)
		newest_version = get_version_number(repo_path)
		# Assuming linear history
		versions = [newest_version - i for i, sha in enumerate(history)]
		versions.reverse()
		ver2sha = dict(zip(versions, history))

		up_patches = f'patch/{repo_name}/up'
		patches = os.listdir(up_patches)
		make_first = True
		for patch in sorted(patches):
			if patch.endswith('.sig'):
				continue
			parts = patch.split('-')
			first = int(parts[0])
			second = int(parts[1])

			if make_first:
				sha_first = ver2sha[first]
				checkout(repo_path, sha_first)
				archive, _ = maybe_make_archive(repo_path, 'archives')
				make_first = False

			shell(['./butler', 'apply', '--staging-dir=tmp', f'{up_patches}/{patch}', './archives'])
			shutil.rmtree('./tmp')

if __name__ == '__main__':
	run_butler_apply()


