import sys
from jira import JIRA
import base64
import collections
from github import Github
import re

'''
Before use, please change the basic auth arguments to you own Jira username, and password in base64 encoded form.

'''


def bucket(prNumber):

    g = Github("")
    jira = JIRA('https://issues.liferay.com/',basic_auth=('peter.kungl', base64.b64decode('').decode('utf-8')))

    org = g.get_organization("liferay")
    repo = org.get_repo("liferay-portal-ee")

    pr = repo.get_pull(prNumber)

    prBody = str(pr.body)

    bprNumbers = set(re.findall("BPR-(\d+)",prBody))

    for bprKey in bprNumbers:
        issue = jira.issue("BPR-" + bprKey)
        try:
            issue.update(fields={'customfield_19930':[{'value':'Bucket-A'}]})
            jira.transition_issue(issue,101)

        except:
            return "Something went wrong!"

        return ("Issue has been bucketed and moved to regression testing: "
                 "BPR-" + bprKey)




