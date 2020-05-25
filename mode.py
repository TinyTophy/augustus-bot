import sys
import json

def token_mode():
    print('------ TOKEN MODE ------')
    print('1 - dev\n2 - prod\n')
    modeInput = input('Enter mode: ')
    info = json.load(open('info.json'))
    if modeInput == '1':
        info['state'] = ':dev: '
        with open('info.json', 'w+') as data:
            json.dump(info, data)
        return 'dev'
    elif modeInput == '2':
        info['state'] = ':aug: '
        with open('info.json', 'w+') as data:
            json.dump(info, data)
        return 'prod'
    else:
        sys.exit('You must enter a value of 1 or 2! Please run bot again.')

def db_mode():
    print('------ DATABASE MODE ------')
    print('1 - dev\n2 - prod\n')
    modeInput = input('Enter mode: ')
    if modeInput == '1':
        return 'devbot'
    elif modeInput == '2':
        return 'prodbot'
    else:
        sys.exit('You must enter a value of 1 or 2! Please run bot again.')
