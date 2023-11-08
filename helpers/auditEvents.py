import json, os
from pandas import json_normalize
import pandas as pd

def read_log_file_ae(file_path):
    lines =[]
    debug = []
    file_path = selectPath(file_path)
    with open(file_path , 'r') as file:
        logs = file.readlines()
    error_logs = []
    data_logs = []
    for log in logs:
        try:
            log_data = json.loads(log)
            if 'error' in log_data or 'address' in log_data :
                error_logs.append(log_data)
            else:
                data_logs.append(log_data)
        except json.JSONDecodeError:
            print("Error decoding JSON log:", log)

    error_df = pd.DataFrame(error_logs)
    data_df = pd.DataFrame(data_logs)
    return [data_df,error_df]

def selectPath(file_path):
    if os.path.exists(file_path + "/var/log/gitlab/gitlab-rails/audit_json.log"):
        return file_path + "/var/log/gitlab/gitlab-rails/audit_json.log"
    else:
        return file_path + "/var/log/apps/gitlab/gitlab-rails/audit_json.log"

def convert_to_dataframe(log_data):
    return json_normalize(log_data)

