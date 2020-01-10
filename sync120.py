'''
  Created by Weihao Zeng.
  Disclaimer: Use at your own risk.

  Free to use for anything that is legal and align with UCSD Academic Integrity.
  Use at you own risk.
'''


from paramiko import SSHClient
from scp import SCPClient
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
import atexit

# file syncing config
'''
  This assumes you have folder structure like
  all_pas:
    PA1:
      mycode1.c
      ...
    PA2:
      ...

  Just change PA_STR when you change PA

  E.g.:

    PA_STR = "pa1"
    PAS_DIR = ".../CSE 120/PAs/"  Remember the "/" in the end
'''
PAS_DIR = "DIR FOR ALL PAS"   # CHANGE ME
PA_STR = "CHANGE ME TO THE PA FOLDER" # CHANGE ME

# SSH Config
# CHANGE THESE!
ssh_host = "ieng9.ucsd.edu"
ssh_username = "YOUR CSE120 SSH USER NAME"  # CHANGE ME
ssh_pwd = "YOUR SSH PASSWORD, AT YOUR RISK; U R RESPONSIBLE LIKE PROF WOULD SAY. HAHA : )"  # CHANGE ME

# create scp client
ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect(ssh_host, username=ssh_username, password=ssh_pwd, look_for_keys=False)
scp = SCPClient(ssh.get_transport())

pa_dir = PAS_DIR + PA_STR

# A lazy dummy function to sync files
def syncFile(evt=None, src_dir=None, dest_dir="~/" + PA_STR):
  '''
    I use this function to deal both call from event handler 
    and my own initializaion on start up.  Will use directory for evt (event handler)
    if it exists; otherwise, src_dir.  You are doomed if both invalid.

    evt:      the event from watch dog
    src_dir:  passing in the src_dir works too
    dest_dir: default to home folder on remote
  '''
  sync_dir = ''
  if evt is not None:
    sync_dir = evt.src_path
  else:
    sync_dir = src_dir

  print(sync_dir)
  scp.put(sync_dir, dest_dir, recursive=True)

# handler for file changes
'''
  !!! Only syncing *.c and *.h
'''
my_event_handler = PatternMatchingEventHandler(case_sensitive=False, patterns=["*.c", "*.h"])
# my_event_handler.on_any_event = syncFile # incorrect behavior for deletion, don't care about moving
my_event_handler.on_created = syncFile
my_event_handler.on_modified = syncFile

# create observer and do a startup sync
observer = Observer()
observer.schedule(my_event_handler, pa_dir, recursive=True)
syncFile(src_dir=pa_dir)
observer.start()
print("Sync started")


# close everything on exit
def closeAll():
  scp.close()
  observer.stop()
  print("Close all")

atexit.register(closeAll)

# prevents the program to exit, so observer works
# use CTR + C / CTR + D to exit program
while True:
  try:
    time.sleep(1)
  except KeyboardInterrupt:
    print("Stopping")
    break
