#!/bin/python

import os

from helpers import get_version_number, get_commit_history
from helpers import checkout, get_spring_version, get_spring_name
from repos import repos
from config import *

import sqlite3

REPO_DIR = 'repos/'

def make_connection():
	return sqlite3.connect('nextgen.db')

def run_versions(repo):
	con = make_connection()
	create_tables(con)

	repo_name = repo['name']
	repo_path = os.path.join(REPO_DIR, repo_name)

	history = get_commit_history(repo_path)
	history = history[-HISTORY_GENERATION_SIZE:]
	newest_version = get_version_number(repo_path)
	# Assuming linear history
	versions = [newest_version - i for i, sha in enumerate(history)]
	versions.reverse()
	channel = 'main'

	full_names = []

	version_entries = []
	version_entries.append((
		f"{repo['rapid']}:test",
		f"{repo_name}@{channel}"
	))
	for i, new_sha in enumerate(history):
		new_ver = versions[i]
		if i == 0:
			continue

		checkout(repo_path, new_sha)
		name = get_spring_name(repo_path).strip()
		spring_version = get_spring_version(repo_path)
		version_number = get_version_number(repo_path)
		print(newest_version, version_number)
		if version_number != newest_version:
			version_entries.append((
				f"{name} {spring_version}",
				f"{repo_name}@{channel}:{version_number}"
			))
	print(version_entries)

	insert_versions(con, version_entries)

def create_tables(con):
	cur = con.cursor()
	cur.execute('''CREATE TABLE IF NOT EXISTS versions(
		springName TEXT NOT NULL UNIQUE,
		nextgenName TEXT NOT NULL UNIQUE
	)''')
	con.commit()

def insert_versions(con, versions):
	cur = con.cursor()
	for version in versions:
		cur.execute("INSERT INTO versions VALUES (?, ?)", version)
	con.commit()

def select_all(con):
	cur = con.cursor()
	cur.execute("SELECT * FROM versions")
	rows = cur.fetchall()
	for row in rows:
		print(row)
	print(rows)

if __name__ == '__main__':
	for repo in repos:
		run_versions(repo)

	select_all()