'''
You have to rename or create a new file to credential.py and fill the fields rightly.
'''
import getpass
import sys
import requests
import urllib3

def validate_cred():
    #Domain data
    domain = ''

    try:
        user = str(input('Digite o usuário: '))
        password = getpass.getpass('Digite a sua senha: ', stream=None)
        
        basicAuthUrl = f'https://{user}:{password}@{domain}'
        urllib3.disable_warnings()
        response = requests.get(url=basicAuthUrl+'/api/user', verify=False)

        if response.status_code == 200:
            return domain, user, password
        else:
            print("Incorrect user or password. Try again")
            sys.exit()
    except KeyboardInterrupt:
        print("Ctrl + C")
        sys.exit()