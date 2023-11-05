import json
import matplotlib.pylab as plt
import pandas as pd
from .utils import *
from pandas import json_normalize


def read_log_file_wh(file_path):
    with open(file_path + '/var/log/gitlab/gitlab-workhorse/current', 'r') as file:
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
    print(data_df.columns)
    return [data_df,error_df]


