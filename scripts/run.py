import sys

from update_repos import run_clone
from repos import repos
from generate import run_generate
from s3_upload import run_upload

def run(is_dry):
	for repo in repos:
		#if run_clone(repo) or run_generate(repo):
		run_upload(repo['name'], is_dry)

if __name__ == "__main__":
	is_dry = False
	if len(sys.argv) > 1:
		is_dry = sys.argv[1] == "dry"
	run(is_dry)