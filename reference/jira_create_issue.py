from jira import JIRA
import jira.client
import datetime
import re

def issue_create():
    import jira.client
    options = {'server': 'http://vlm.lge.com/issue'}
    jira = jira.client.JIRA(options, basic_auth = ('username', 'password')) # Noted!! you need change your username and password

    jira_label = 'tiger-auto-test'# you are make sure label valid
    jira_title = 'set title'
    jira_issuetype = 'Task' #you can change to "Sub-task"
    jira_description = 'set description'
    jira_component  = 'tiger-desktop' # you are make sure component valid
    jira_priority = 'P2'
    jira_reporter = 'auto-tiger'
    jira_assignee = 'auto-tiger'
    jira_watcher = 'auto-tiger'
    jira_attachment = 'path file'
    jira_duedate = str(datetime.datetime.now() + datetime.timedelta(days = 5)).split()[0]
    

    jira_task_dict = {
        'project' : { 'key': 'TIGER' },
        'issuetype' : { 'name' : jira_issuetype },
        'summary' : jira_title,
        'description' : jira_description,
        'duedate': jira_duedate,
        'priority': { 'name' : jira_priority},
        'components': [{"name": jira_component}],
        'reporter': {'name': jira_reporter},
        'assignee': {'name': jira_assignee}
        }

    issue = jira.create_issue(fields=jira_task_dict)
    print('Jira issue id: ', issue)

    issue.fields.labels.append(jira_label)
    issue.update(fields={"labels": issue.fields.labels})
    jira.add_watcher(issue, jira_watcher)
    #add attachments file
    # jira.add_attachment(issue=issue, attachment = jira_attachment)


if (__name__ == "__main__"):
    print("the simple example to make jira ticket with python")
    issue_create()