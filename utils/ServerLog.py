import time

LOG_FILE = None
LOG_OPEN = False

def open_log(logF):
    logF = logF + str(int(time.time())) + ".txt"
    global LOG_OPEN
    global LOG_FILE
    if not LOG_OPEN:
        try:
            LOG_FILE = open(logF, 'w')
        except:
            logF = 'logs/pvs_log' + str(int(time.time()))
            LOG_FILE = open(logF, 'w')

        LOG_OPEN = True
        print "SC: Log Open - " + str(logF)

    return logF

def close_log():
    global LOG_FILE
    LOG_FILE.close()
    print "SC: Log Closed"

def print_log(str):
    global LOG_FILE
    print >> LOG_FILE, str
