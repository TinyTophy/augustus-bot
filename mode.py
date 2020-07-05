import sys
import json
import os

def token_mode():
    print('------ TOKEN MODE ------')
    print('1 - dev')
    print('2 - prod')
    modeInput = input('Enter mode: ')
    if modeInput == '1':
        return os.environ['DEV']
    elif modeInput == '2':
        return os.environ['PROD']
    else:
        sys.exit('You must enter a value of 1 or 2! Please run bot again.')

def db_mode():
    print('------ DATABASE MODE ------')
    print('1 - dev\n2 - prod\n')
    modeInput = input('Enter mode: ')
    if modeInput == '1':
        return 'dev'
    elif modeInput == '2':
        return 'prod'
    else:
        sys.exit('You must enter a value of 1 or 2! Please run bot again.')
