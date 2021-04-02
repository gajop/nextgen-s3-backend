import sys

from update_repos import run_clone
from repos import repos
from generate import run_generate
from s3_upload import run_upload
import time

SLEEP_SECONDS = 60

def run(is_dry):
	while True:
		for repo in repos:
			has_clone_updates = run_clone(repo)
			has_generate_updates = run_generate(repo)
			if has_clone_updates or has_generate_updates:
				run_upload(repo['name'], is_dry)
		print(f"Sleeping for {SLEEP_SECONDS} seconds...")
		time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
	is_dry = False
	if len(sys.argv) > 1:
		is_dry = sys.argv[1] == "dry"
	run(is_dry)