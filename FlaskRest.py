import time

import pytz
from flask import Flask
import logging
from datetime import datetime
from sendToRegression import bucket, administrative_issue, close
import commands
from flask import json
from github import Github

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskRest")
handler = logging.FileHandler(filename='log.txt')
handler.setLevel(logging.INFO)
logger.addHandler(handler)
env = json.load(open("wedeploy.json", 'r'))["env"]
props = json.load(open("properties.json", 'r'))
app = Flask(__name__)


def run():
	while True:
		logging.info('Polling started: %s', datetime.now(pytz.timezone('Europe/Paris')))

		githubtoken = env["github"]
		g = Github(githubtoken)
		org = g.get_organization(props["org"])
		repo = org.get_repo(props["repo"])
		prs = repo.get_pulls("open")
		for pr in prs:
			if check_for_labels(pr):
				comments = pr.get_issue_comments()
				for comment in comments:
					if comment.body[0:4] == "cihu":
						handle_command(comment, pr)
		time.sleep(props["schedule"])


def check_for_labels(pr):
	for label in pr.raw_data["labels"]:
		if label["name"] in {"bucket-a", "bucket-b", "gauntlet"}:
			return False
	return True


def handle_command(comment, pr):
	allowed_senders = props["allowedSender"]
	if comment.user.login in allowed_senders:
		params = str(comment.body).split(":")
		if params[1] == commands.BUCKETING_COMMAND:
			bucket(pr.number, params[2])
		elif params[1] == "review":
			if params[2] == commands.ADMINISTRATIVE_ISSUE_COMMAND:
				administrative_issue(pr.number)
		elif params[1] == "close":
			close(pr.number)


if __name__ == '__main__':
	run()
