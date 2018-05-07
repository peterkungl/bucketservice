import base64
import logging
import re

from flask import json
from github import Github
from jira import JIRA

import constants
import envvariables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskRest")
handler = logging.FileHandler(filename='log.txt')
handler.setLevel(logging.INFO)
logger.addHandler(handler)
props = json.load(open("properties.json", 'r'))

jira = JIRA(envvariables.jiraUrl, basic_auth=(envvariables.jirauser, base64.b64decode(envvariables.jirapw).decode('utf-8')))
g = Github(envvariables.github)
org = g.get_organization(props["org"])
repo = org.get_repo(props["repo"])


def bucket(pr_number, bucket):
	bucket = "Bucket-" + str(bucket).capitalize()
	pr = repo.get_pull(pr_number)
	pr_body = str(pr.body)
	bpr_numbers = set(re.findall("BPR-(\d+)", pr_body))

	for bprKey in bpr_numbers:
		issue = jira.issue("BPR-" + bprKey)
		try:
			if issue.fields.status.name == "In Review":
				jira.transition_issue(issue, 101)
				add_new_value_multiselect_customfield(bucket, 'customfield_19930', issue)
				logger.info("PR has been bucketed and moved to regression testing: PR-" + str(pr.number) + " in " + bucket)
		except Exception as e:
			logger.error(e)


def add_new_value_multiselect_customfield(value, field, issue):
	data = []
	for element in issue.fields.customfield_19930:
		if element.value not in ['None', 'Bucket-A', 'Bucket-B']:
			data.append(element.value)

	if value in data:
		return

	data.append(value)
	list = []
	for d in data:
		dict = {'value': d}
		list.append(dict)
	issue.update(fields={field: list})


def administrative_issue(pr_number):
	pr = repo.get_pull(pr_number)
	pr_body = str(pr.body)
	bpr_numbers = set(re.findall("BPR-(\d+)", pr_body))

	for bprKey in bpr_numbers:
		issue = jira.issue("BPR-" + bprKey)
		try:
			add_new_value_multiselect_customfield(constants.JIRA_ADMINISTRATIVE_ISSUE, constants.JIRA_REVIEW_RESULT_FIELD, issue)
			logger.info("Administrative issue was added to %s", issue)
		except Exception as e:
			logger.error(e)


def close(pr_number):
	pr = repo.get_pull(pr_number)
	pr_body = str(pr.body)
	bpr_numbers = set(re.findall("BPR-(\d+)", pr_body))

	for bprKey in bpr_numbers:
		issue = jira.issue("BPR-" + bprKey)

		if issue.fields.status.name == "In Review":
			jira.transition_issue(issue, 141)
			logger.info(bprKey + "Has been closed")
			jira.transition_issue(issue, 81)
			logger.info(bprKey + "Has been reopened")
			jira.transition_issue(issue, 21)
			logger.info(bprKey + "Has been transitioned to 'Original Fix Committed'")
	if pr.state == 'open':
		pr.create_issue_comment("ci:close")
		logger.info(pr.number + "has been closed.")
