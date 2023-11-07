import json
import matplotlib.pylab as plt
import pandas as pd
from .utils import *
from pandas import json_normalize


def read_log_file_wh(file_path):
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
    if os.path.exists(file_path + "/var/log/gitlab/gitlab-workhorse/current"):
        return file_path + "/var/log/gitlab/gitlab-workhorse/current"
    else:
        return file_path + "/var/log/apps/gitlab/gitlab-workhorse/current"
