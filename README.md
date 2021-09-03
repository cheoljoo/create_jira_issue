# create_jira_issue
- it is made for my convenience to overcome the speed of our system. you can use all fields in jira ticket.
- when i want to make a ticket each 3 persons with the same message , i takes a lot of time because our system is very low.
    - this script register the tickets each person separately.

## help
- python3 jira_create_issue.py -h 

## run
- run
    - $ python3 class_create_jira_issue.py --authname your_id --authpasswd "your_password"  --label test --title "version 1 테스xm "  --desc "지금은 테스트중 ... multiple line
제대로 되는지 확인 필요" --assignee "cheoljoo.lee,seungdae.goh" --attachment ./a.sh --remaindate 1 
    - assignee is mendatory : others are optional
- just print the ticket ( it is just for verfication)
    - add -j option 
    - $ python3 class_create_jira_issue.py --authname your_id --authpasswd "your_password"  --label test --title "version 1 테스xm "  --desc "TTT" --assignee "cheoljoo.lee,seungdae.goh"  -j

# install package
- apt-get update
- apt-get install -y python3-pip
- python3 -m pip install jira
    - virtualenv error
```
$ pip3 install jira --user
ERROR: Could not find an activated virtualenv (required).

$ export PIP3_REQUIRE_VIRTUALENV=false
$ export PIP_REQUIRE_VIRTUALENV=false
$ pip3 install jira --user
Collecting jira
  Downloading jira-3.0.1-py3-none-any.whl (61 kB)
     |████████████████████████████████| 61 kB 6.7 MB/s
Collecting requests-toolbelt
  Downloading requests_toolbelt-0.9.1-py2.py3-none-any.whl (54 kB)
     |████████████████████████████████| 54 kB 21.7 MB/s
Collecting defusedxml
  Downloading defusedxml-0.7.1-py2.py3-none-any.whl (25 kB)
Requirement already satisfied: requests>=2.10.0 in /usr/lib/python3/dist-packages (from jira) (2.22.0)
Requirement already satisfied: setuptools>=20.10.1 in /usr/lib/python3/dist-packages (from jira) (45.2.0)
Collecting requests-oauthlib>=1.1.0
  Downloading requests_oauthlib-1.3.0-py2.py3-none-any.whl (23 kB)
Requirement already satisfied: keyring in /usr/lib/python3/dist-packages (from jira) (18.0.1)
Requirement already satisfied: oauthlib>=3.0.0 in /usr/lib/python3/dist-packages (from requests-oauthlib>=1.1.0->jira) (3.1.0)
Requirement already satisfied: secretstorage in /usr/lib/python3/dist-packages (from keyring->jira) (2.3.1)
Installing collected packages: requests-toolbelt, defusedxml, requests-oauthlib, jira
Successfully installed defusedxml-0.7.1 jira-3.0.1 requests-oauthlib-1.3.0 requests-toolbelt-0.9.1

```


# reference
- I think internet is alreay have guideline and example for it. I learned it from below link:
    - https://jira.readthedocs.io/en/master/examples.html  
    - https://github.com/atlassian-api/atlassian-python-api 

## python3 arg parser
```python
import argparse

. . .

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='tiger_ia.py',
        description=
        'Launcher for Log Analyzer of Intelligence Artificial about Tiger Log files'
    )

    parser.add_argument('-i',
                        '--input_dir',
                        metavar="IN_DIR",
                        type=str,
                        help='folder names (mulitple)')

parser.add_argument(
        '-f',
        '--input_file',
        metavar="IN_FILE",
        type=str,
        help=
        'input parameter for log_file (plain text) or zip_file which includes multiple log files'
 )

    . . .

    args = parser.parse_args()

  if (args.input_file and args.input_dir):
        print("ERROR:  do not use '-f' and '-i'). Usage: {} -h".format(
            sys.argv[0]))
        sys.exit(1)

    in_file = args.input_file

```
