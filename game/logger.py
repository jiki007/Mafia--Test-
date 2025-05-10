import datetime

def log(message: str, to_file=False):
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    
    print(log_entry)  # Always print to console
    
    if to_file:
        with open("game_log.txt", "a", encoding="utf-8") as file:
            file.write(log_entry + "\n")
