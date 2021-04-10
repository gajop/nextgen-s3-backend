import subprocess
from subprocess import PIPE
import os
import sys
from pathlib import Path
import shutil
import tempfile
import fileinput

shell_printing_silenced = False

def set_shells_silent(silent):
	global shell_printing_silenced
	shell_printing_silenced = silent

def shell(cmds, **kwargs):
	cmd = ' '.join(cmds)
	if 'cwd' in kwargs:
		cmd = kwargs['cwd'] + '$ ' + cmd
	if not shell_printing_silenced:
		print(cmd)
	# result = subprocess.run(cmds, capture_output=True, text=True, **kwargs)
	result = subprocess.run(cmds, stdout=PIPE, stderr=PIPE, universal_newlines=True, **kwargs)
	if result.returncode != 0:
		raise Exception(f'Command failed: {result.stderr} {result.stdout}')
	if result.stderr.strip() != '' and not shell_printing_silenced:
		print(f'Error output: {result.stderr}')
	return result.stdout.strip()

def maybe_make_archive(clone_path, dest_dir):
	version = get_version(clone_path)
	name = get_name(clone_path).strip()
	dest = f'{dest_dir}/{name} {version}.sdz'
	if os.path.exists(dest):
		return dest, False
	make_archive(clone_path, version, dest)
	return dest, True

def make_archive(repo_path, version, dest):
	with tempfile.TemporaryDirectory() as tmpdir:
		tmp_dest = f'{tmpdir}/dest'
		shutil.copytree(repo_path, tmp_dest)
		shutil.rmtree(f'{tmp_dest}/.git')
		for i, line in enumerate(fileinput.input(f'{tmp_dest}/modinfo.lua', inplace=1)):
			if 'version' in line and '$VERSION' in line:
				sys.stdout.write(line.replace('$VERSION', version))
			else:
				sys.stdout.write(line)
		print(f'Zipping {dest}...')
		shutil.make_archive(dest, 'zip', tmp_dest)
		Path(dest).parent.mkdir(parents=True, exist_ok=True)
		shutil.move(dest + '.zip', dest)

def get_version(repo_path):
	commit_msg = shell(['git', 'log', '-1', '--pretty=%B'], cwd=repo_path)

	if commit_msg.startswith('VERSION{'):
		version = commit_msg.split('VERSION{')[1]
		if '}' in version.endswith():
			version = version.split('}')[0]
			return version

	version_number = get_version_number(repo_path)
	sha = shell(['git', 'rev-parse', '--short', 'HEAD'], cwd=repo_path)
	return f'test-{version_number}-{sha}'

def get_version_number(repo_path):
	return int(shell(['git', 'rev-list', 'HEAD', '--count'], cwd=repo_path))

def get_commit_history(repo_path):
	shell(['git', 'checkout', 'master'], cwd=repo_path)
	return shell(['git', 'log', '--reverse', '--pretty=%H'], cwd=repo_path).split()

def checkout(repo_path, commit_sha):
	shell(['git', 'checkout', '-f', commit_sha], cwd=repo_path)
	shell(['git', 'submodule', 'deinit', '--force', '--all'], cwd=repo_path)
	shell(['git', 'submodule', 'init'], cwd=repo_path)
	shell(['git', 'submodule', 'update'], cwd=repo_path)

def get_name(repo_path):
	return shell(['lua', f'{Path(__file__).parent}/load.lua', f'{repo_path}/modinfo.lua', 'name'])

def replace_with_empty(file):
	os.remove(file)
	touch(file)

def touch(path):
	basedir = os.path.dirname(path)
	if not os.path.exists(basedir):
		os.makedirs(basedir)
	with open(path, 'a'):
		os.utime(path, None)