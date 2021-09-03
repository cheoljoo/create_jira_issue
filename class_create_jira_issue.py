from jira import JIRA
import jira.client
import datetime
import re
import argparse

class CIssue :
    """ 
    This Class creates issue in jira system.
    each issue has only one owner (assignee)
    c = CIssue(...)
    c.print()
    c.connect()
    """
    def __init__(self
                 , jira_assignee
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
                 , index = 0
                ):
        """ 
        This funciton is issue create function.
        each issue has only one owner (assignee)
        """
        self.index = index;
        if not jira_assignee:
            print("ERROR : you should set assignee")
            quit()
        else :
            self.jira_assignee = jira_assignee
        self.auth_name = auth_name
        self.auth_passwd = auth_passwd
        if not jira_project:
            self.jira_project = 'TIGER'
        else :
            self.jira_project = jira_project
        self.jira_label = jira_label
        self.jira_title = jira_title
        if not jira_issuetype:
            self.jira_issuetype = 'Task'
        else :
            self.jira_issuetype = jira_issuetype
        self.jira_description = jira_description
        if not jira_component:
            self.jira_component = 'CMU'
        else :
            self.jira_component = jira_component
        if not jira_priority:
            self.jira_priority = 'P2'
        else :
            self.jira_priority = jira_priority
        if not jira_reporter:
            self.jira_reporter = auth_name
        else :
            self.jira_reporter = jira_reporter
        self.jira_watcher = jira_watcher
        self.jira_attachment = jira_attachment
        if jira_remaindate < 1:
            self.jira_remaindate = 1
        else :
            self.jira_remaindate = jira_remaindate

        self.jira_duedate = str(datetime.datetime.now() + datetime.timedelta(days = jira_remaindate)).split()[0]
        
    def print(self):
        print("Issue Ticket Status:")
        print("\tindex : " , self.index)
        print("\tjira_assignee : " , self.jira_assignee)
        print("\tauth_name : " , self.auth_name)
        print("\tauth_passwd : " , self.auth_passwd)
        print("\tjira_project : " , self.jira_project)
        print("\tjira_label : " , self.jira_label)
        print("\tjira_title : " , self.jira_title)
        print("\tjira_issuetype : " , self.jira_issuetype)
        print("\tjira_description : " , self.jira_description)
        print("\tjira_component : " , self.jira_component)
        print("\tjira_priority : " , self.jira_priority)
        print("\tjira_reporter : " , self.jira_reporter)
        print("\tjira_watcher : " , self.jira_watcher)
        print("\tjira_attachment : " , self.jira_attachment)
        print("\tjira_remaindate : " , self.jira_remaindate)
        print("\t\tjira_duedate : " , self.jira_duedate)


    def connect(self):
        options = {'server': 'http://vlm.lge.com/issue'}
        import jira.client
        jira = jira.client.JIRA(options, basic_auth = (self.auth_name, self.auth_passwd)) # Noted!! you need change your username and password

        # label , title , issuetype , component , watcher ,  attachment  , duedate
        # auth_user , auth_password
        # project , assignee , desc
        jira_task_dict = {
            'project' : { 'key': self.jira_project },
            'issuetype' : { 'name' : self.jira_issuetype },
            'summary' : self.jira_title,
            'description' : self.jira_description,
            'duedate': self.jira_duedate,
            'priority': { 'name' : self.jira_priority},
            'components': [{"name": self.jira_component}],
            'reporter': {'name': self.jira_reporter},
            'assignee': {'name': self.jira_assignee}
            }

        issue = jira.create_issue(fields=jira_task_dict)
        print('Jira issue id: ', issue)
        # print("{} to the power {} equals {}".format(args.x, args.y, answer)

        labels = self.jira_label.split(',')
        for label in labels:
            issue.fields.labels.append(label)
        issue.update(fields={"labels": issue.fields.labels})
        watchers = self.jira_watcher.split(',')
        for watcher in watchers:
            jira.add_watcher(issue, watcher)
        #add attachments file
        attachs = self.jira_attachment.split(',')
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

    parser.add_argument("-j", "--justprint", action="store_true" , help="just print : not connect to server")

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
        help='description : multiple lines between double quotation \"   \"')

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

    index = 1;
    for assignee in assignees:
        assignee.strip()
        if assignee :
            cissue = CIssue(
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
                 , index = index
                 )
            index += 1;
            cissue.print()
            if not args.justprint:
                cissue.connect()

