from jira import JIRA
import jira.client
import datetime
import re
import argparse

def issue_create(
                 jira_assignee
                 , auth_name = 'USER' 
                 , auth_passwd = 'PASSWORD'
                 , jira_project = 'TIGER'
                 , jira_label = 'test'      # multiple with ,
                 , jira_title = 'test : 테스트'
                 , jira_issuetype = 'Task'
                 , jira_description = 'test : 테스트'
                 , jira_component = 'CMU'
                 , jira_priority = 'P2'
                 , jira_reporter = ''
                 , jira_watcher = ''            # multiple with ,
                 , jira_attachment = ''         # multiple with ,
                 , jira_remaindate = 5
):
    """ 
    This funciton is issue create function.
    each issue has only one owner (assignee)
    """
    import jira.client

    if not jira_assignee:
        print("ERROR : you should set assignee")
        quit()
    if not jira_reporter:
        jira_reporter = auth_name
    if not jira_project:
        jira_project = 'TIGER'
    if not jira_issuetype:
        jira_issuetype = 'Task'
    if not jira_component:
        jira_component = 'CMU'
    if not jira_priority:
        jira_priority = 'P2'
    if jira_remaindate < 1:
        jira_remaindate = 1
    jira_duedate = str(datetime.datetime.now() + datetime.timedelta(days = jira_remaindate)).split()[0]
    
    print("Make Issue Ticket")
    print("\tauth_name : {}" , auth_name)
    print("\tauth_passwd : {}" , auth_passwd)
    print("\tjira_project : {}" , jira_project)
    print("\tjira_label : {}" , jira_label)
    print("\tjira_title : {}" , jira_title)
    print("\tjira_issuetype : {}" , jira_issuetype)
    print("\tjira_description : {}" , jira_description)
    print("\tjira_component : {}" , jira_component)
    print("\tjira_priority : {}" , jira_priority)
    print("\tjira_reporter : {}" , jira_reporter)
    print("\tjira_assignee : {}" , jira_assignee)
    print("\tjira_watcher : {}" , jira_watcher)
    print("\tjira_attachment : {}" , jira_attachment)
    print("\tjira_remaindate : {}" , jira_remaindate)
    print("\t\tjira_duedate : {}" , jira_duedate)

    return 

    options = {'server': 'http://vlm.lge.com/issue'}
    jira = jira.client.JIRA(options, basic_auth = (auth_name, auth_passwd)) # Noted!! you need change your username and password

    # label , title , issuetype , component , watcher ,  attachment  , duedate
    # auth_user , auth_password
    # project , assignee , desc
    jira_task_dict = {
        'project' : { 'key': jira_project },
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
    # print("{} to the power {} equals {}".format(args.x, args.y, answer)

    labels = jira_label.split(',')
    for label in labels:
        issue.fields.labels.append(label)
    issue.update(fields={"labels": issue.fields.labels})
    watchers = jira_watcher.split(',')
    for watcher in watchers:
        jira.add_watcher(issue, watcher)
    #add attachments file
    attachs = jira_attachment.split(',')
    for attach in attachs:
        jira.add_attachment(issue=issue, attachment = attach)


if (__name__ == "__main__"):

    parser = argparse.ArgumentParser(
        prog='create_jira_issue.py',
        description=
        'Create Jira Issue in VLM'
    )
    # group = parser.add_mutually_exclusive_group()
    #group.add_argument("-v", "--verbose", action="store_true")
    #group.add_argument("-q", "--quiet", action="store_true")

    parser.add_argument(
        '--authname',
        metavar="<id>",
        type=str,
        help='jira id')

    parser.add_argument(
        '--authpasswd',
        metavar="<passwd>",
        type=str,
        help='jira passwd')

    parser.add_argument( '--project', metavar="<str>", type=str, help='Project Name -  default) TIGER')
    parser.add_argument( '--label', metavar="<str>", type=str, help='multiple labels with \',\'')
    parser.add_argument( '--title', metavar="<str>", type=str, help='title or summary')
    parser.add_argument( '--issuetype', metavar="<str>", type=str, choices=['Task', 'Story'] , help='issue type (Task,Story) - default) Task')

    parser.add_argument(
        '--desc',
        metavar="<str>",
        type=str,
        help='description')

    parser.add_argument( '--component', metavar="<str>", type=str, help='component - default) CMU')
    parser.add_argument( '--priority', metavar="<str>", type=str, choices=['P0', 'P1', 'P2', 'P3'] , help='priority - default) P2')
    parser.add_argument( '--reporter', metavar="<str>", type=str, help='reporter - default) creator (authname)')

    parser.add_argument(
        '--assignee',
        metavar="<str>",
        type=str,
        help='whom do you send to?  (multiple with \',\')')

    parser.add_argument( '--watcher', metavar="<str>", type=str, help='watcher - default) creater , assignee')
    parser.add_argument( '--attachment', metavar="<str>", type=str, help='attachment - ex) ./data.txt')
    parser.add_argument( '--remaindate', metavar="<int>", type=str, help='due date after remaindate dayes')

    args = parser.parse_args()

    if not args.assignee:
        print("ERROR : you should set assignee")
        quit()

    print("the simple example to make jira ticket with python")
    #print(args.project)
    #print(args.desc)
    #print(args.assignee)

    #args.wathcer.translate({ord(c): None for c in string.whitespace})           # remove all whitespace

    assignees = args.assignee.split(',')
    for assignee in assignees :
        assignee.strip()
        if args.watcher:
            if assignee not in args.watcher :
                if not args.watcher :
                    args.watcher = assignee
                else :
                    args.watcher = args.watcher + "," + assignee
        else :
            args.watcher = assignee

    for assignee in assignees:
        assignee.strip()
        if assignee :
            issue_create(
                  jira_assignee = assignee
                 , auth_name = args.authname
                 , auth_passwd = args.authpasswd
                 , jira_project = args.project
                 , jira_label = args.label
                 , jira_title = args.title
                 , jira_issuetype = args.issuetype
                 , jira_description = args.desc
                 , jira_component = args.component
                 , jira_priority = args.priority
                 , jira_reporter = args.reporter
                 , jira_watcher = args.watcher
                 , jira_attachment = args.attachment
                 , jira_remaindate =  int(args.remaindate)
                 )
