
import json, os
from datetime import datetime as dt

# global variables
error_class = "alert alert-danger"
success_class = "alert alert-success"
# checks if connected to the internal server : time out is 3 seconds
# def isInternalNetwork():
#     response =  os.system("ping -c 1 -W 3 " + "10.50.40.166")
#     return False if (response>0) else True

files_ = [
    "/lscpu",
    "/free_m",
    "/uptime",
    "/gitlab_status",
    "/gitlab_migrations",
    "/df_hT",
    "/pressure_cpu.txt",
    "/top_cpu"
]

def checkFileExists(realtivePath, logsType):
    logsType_ = {
        "Production": ["/var/log/gitlab/gitlab-rails/production_json.log","/var/log/apps/gitlab/gitlab-rails/production_json.log"],
        "Sidekiq": ["/var/log/gitlab/sidekiq/current","/var/log/apps/gitlab/sidekiq"],
        "Gitaly": ["/var/log/gitlab/gitaly/current","/var/log/apps/gitlab/sidekiq"],
        "API": ["/var/log/gitlab/gitlab-rails/api_json.log","/var/log/apps/gitlab/gitlab-rails/api_json.log"],
        "Workhorse" : ["/var/log/gitlab/gitlab-workhorse/current","/var/log/apps/gitlab/gitlab-workhorse/current"],
        "Audit Events" : ["/var/log/gitlab/gitlab-rails/audit_json.log","/var/log/apps/gitlab/gitlab-rails/audit_json.log"]
    }
    if os.path.exists(realtivePath + logsType_[logsType][0]):
        return True
    elif os.path.exists(realtivePath + logsType_[logsType][1]):
        return True
    else:
        return False

def getFilteredDataSK(df):
    return df[["time", "severity", "cpu_s", "duration_s", "db_duration_s"]]


def getJobLogsForCorrelationID(correlation_id, realtivePath, logsType):
    logsType_ = {
        "Production": "/var/log/gitlab/gitlab-rails/production_json.log",
        "Sidekiq": "/var/log/gitlab/sidekiq/current",
        "Gitaly": "/var/log/gitlab/gitaly/current",
        "API": "/var/log/gitlab/gitlab-rails/api_json.log"
    }
    correlation_id_ = []
    for c in correlation_id:
        correlation_id_.append(c["correlation_id"])
    read_path = realtivePath + logsType_[logsType]
    lines = []
    debug = []
    with open(
        read_path , "r"
    ) as file:
        log_lines = file.readlines()
    for x, line in enumerate(log_lines):
        try:
            l = json.loads(line)
            if any(item in l["correlation_id"] for item in correlation_id_): 
                lines.append(l)
        except:
            pass
    return lines




def convert_storage_units(value, input_unit="KB"):
    if input_unit.upper() == "KB":
        mb = value / 1024
    elif input_unit.upper() == "MB":
        mb = value
    if mb < 1024:
        return f"{mb:.2f} MB"
    else:
        gb = mb / 1024
        if gb < 1024:
            return f"{gb:.2f} GB"
        else:
            tb = gb / 1024
            return f"{tb:.2f} TB"


custom_css_prd = {
    ".ag-row-hover": {"background-color": "#70dfdb !important"},
    ".ag-header": {
        "background-color": "white !important",
        "font-size": "15px !important",
        "font-color": "black !important",
        "border": "1px solid #eee !important;",
        "align": "left !important",
    },
}


def timeConversion(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    formatted_duration = f"{int(hours)}h" if hours >= 1 else ""
    formatted_duration += f"{int(minutes)}m" if minutes >= 1 else ""
    formatted_duration += f"{seconds:.1f}s" if seconds >= 0.1 else ""
    return formatted_duration

def saveLogEntry(logPath, comment):
    current_data = {
        "Timestamp": dt.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Comment": comment,
        "Path": logPath
    }
    
    try:
        with open('log_history.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    data.insert(0, current_data)
    
    if len(data) > 10:
        data.pop()

    with open('log_history.json', 'w') as file:
        json.dump(data, file, indent=4)


def showLogHistory():
    try:
        with open('log_history.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data