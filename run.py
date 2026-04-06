from core.watcher import follow

LOG_FILE = "/var/log/auth.log"

if __name__ == "__main__":
    for line in follow(LOG_FILE):#is a generator for (tail -f /var/log/auth.log)
        print(line)
        