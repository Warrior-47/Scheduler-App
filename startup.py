import os

roaming_dir = os.environ['APPDATA']

filename = roaming_dir + \
    '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\runScheduler.bat'

directory = os.path.dirname(__file__)

with open(filename, 'w') as f:
    f.write(f'{directory[:2]}\n')
    f.write(f'cd {directory}\n')
    f.write('cd ..\n')
    f.write(f'start Scheduler.exe\n')
