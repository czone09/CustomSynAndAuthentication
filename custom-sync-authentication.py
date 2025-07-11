import sys
from sys import stdin, stdout, stderr
import logging
import xmlrpc.client
from ssl import create_default_context, Purpose

auth = "Zuj0hiazoo5hahwa"
host = "http://127.0.0.1:9191/rpc/api/xmlrpc"

userDatabase = {
    "john": {"fullname": "John Smith", "email": "johns@here.com", "dept": "Accounts", "office": "Melbourne", "cardno": "1234", "otherEmails": "personal1@webmail.com", "secondarycardno": "01234", "password": "password1"},
    "jane": {"fullname": "Jane Rodgers", "email": "janer@here.com", "dept": "Sales", "office": "Docklands", "cardno": "5678", "otherEmails": "personal2@webmail.com", "secondarycardno": "05678", "password": "password2"},
    "ahmed": {"fullname": "Ahmed Yakubb", "email": "ahmedy@here.com", "dept": "Marketing", "office": "Home Office", "cardno": "4321", "otherEmails": "personal3@webmail.com", "secondarycardno": "04321", "password": "password3"},
}

groupDatabase = {
    "groupA": ["john"],
    "groupB": ["ahmed", "jane"],
}

def formatUserDetails(userName, extraData):
    if userName in userDatabase:
        user = userDatabase[userName]
        if extraData:
            return '\t'.join([userName, user["fullname"], user["email"], user["dept"], user["office"],
                              user["cardno"], user["otherEmails"], user["secondarycardno"]]) + '\n'
        else:
            return '\t'.join([userName, user["fullname"], user["email"], user["dept"], user["office"]]) + '\n'
    else:
        stderr.write(f'Call to formatUserDetails error for username "{userName}"\n')
        sys.exit(-1)

# 设置代理
proxy = xmlrpc.client.ServerProxy(host, verbose=False,
                                   context=create_default_context(Purpose.CLIENT_AUTH))

try:
    extraData = proxy.api.getConfigValue(auth, "user-source.update-user-details-card-id") != "N"
except Exception:
    stderr.write("Cannot use web services API. Please configure\n")
    sys.exit(-1)

# 用户认证模式
if len(sys.argv) == 1:
    name = stdin.readline().strip()
    password = stdin.readline().strip()
    if name in userDatabase and userDatabase[name]["password"] == password:
        stdout.write(f"OK\n{name}\n")  # 返回规范用户名
        sys.exit(0)
    else:
        stderr.write("Wrong username or password\n")
        stdout.write("ERROR\n")
        sys.exit(-1)

if len(sys.argv) < 2 or sys.argv[1] != '-':
    stderr.write(f'Incorrect argument passed {sys.argv}\n')
    sys.exit(-1)

# 回调处理
command = sys.argv[2]

if command == "is-valid":
    stdout.write(f'Y\n{"Long form user data record will provided" if extraData else "Short form user data record will provided"}\n')
    sys.exit(0)

if command == "all-users":
    for name in userDatabase:
        stdout.write(formatUserDetails(name, extraData))
    sys.exit(0)

if command == "all-groups":
    print('\n'.join(groupDatabase))
    sys.exit(0)

if command == "get-user-details":
    name = input().strip()
    if name in userDatabase:
        print(formatUserDetails(name, extraData))
        sys.exit(0)
    else:
        print(f"Can't find user {name}", file=sys.stderr)
        sys.exit(-1)

if command == "group-member-names":
    group = sys.argv[3]
    if group in groupDatabase:
        for user in groupDatabase[group]:
            if user in userDatabase:
                print(user)
            else:
                print(f"Invalid user name {user} found in group list {group}", file=sys.stderr)
                sys.exit(-1)
        sys.exit(0)
    else:
        print(f"Group name {group} not found", file=sys.stderr)
        sys.exit(-1)

if command == "group-members":
    group = sys.argv[3]
    if group in groupDatabase:
        for user in groupDatabase[group]:
            if user in userDatabase:
                print(formatUserDetails(user, extraData), end="")
            else:
                print(f"Invalid user name {user} found in group list {group}", file=sys.stderr)
                sys.exit(-1)
        sys.exit(0)
    else:
        print(f"Group name {group} not found", file=sys.stderr)
        sys.exit(-1)

if command == "is-user-in-group":
    group = sys.argv[3]
    user = sys.argv[4]
    if group in groupDatabase:
        print('Y' if user in groupDatabase[group] else 'N')
        sys.exit(0)
    else:
        print(f"Invalid Group name {group}", file=sys.stderr)
        sys.exit(-1)

# 默认处理
print(f"Can't process arguments {sys.argv}", file=sys.stderr)
