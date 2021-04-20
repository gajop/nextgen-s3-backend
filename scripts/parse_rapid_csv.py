# %%
import csv

shas = []
versions = []
with open('../byar-chobby.csv') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for row in reader:
		sha = row[0].split(':')
		sha = sha[len(sha) - 1]
		version = row[3].split('-')
		version = version[len(version) - 2]
		try:
			version = int(version)
		except Exception:
			continue

		versions.append(version)
		shas.append(sha)

#print(shas)
mapped = dict(zip(versions, shas))
zipped = list(zip(versions, shas))
print(mapped)

# %%
import json

json.dump(mapped, open('out.json', 'w'))