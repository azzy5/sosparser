import json
import matplotlib.pylab as plt
import pandas as pd
from pandas import json_normalize

def read_log_file_api(file_path):
    lines =[]
    debug = []
    with open(file_path + "/var/log/gitlab/gitlab-rails/api_json.log", 'r') as file:
        log_lines = file.readlines()
    for x, line in enumerate(log_lines):
        try:
            l = json.loads(line)
            lines.append(l)
            if len(l) == 3 :
                if len(l["message"].split(" ")) < 4:
                    debug.append(l)
        except:
            if line != "\n":
                debug.append(line)
    return [lines, debug]

def convert_to_dataframe(log_data):
    return json_normalize(log_data)


def filterColumnsAPI(df, api_columns):
    columns_remove = ["db_main_replica_cached_count",
                      "db_main_replica_count",
                      "db_main_replica_duration_s",
                      "db_main_replica_wal_cached_count",
                      "db_primary_wal_cached_count",
                      "db_main_wal_count",
                      "db_main_replica_wal_count",
                      "db_replica_wal_cached_count",
                      "db_primary_wal_count",
                      "db_replica_wal_count",
                     "db_ci_cached_count",
                     "db_ci_replica_cached_count",
                     "db_ci_replica_wal_count",
                     "db_ci_wal_cached_count",
                     "db_ci_wal_count",
                     "db_main_replica_count",
                     "db_main_wal_cached_count",
                    "db_primary_wal_count"]
    missing_columns = []
    missing_columns = [elem for elem in missing_columns if elem not in columns_remove]
    for column in missing_columns:
        if column not in df.columns:
            df[column] = 0
    for x in df.columns:
        if x not in api_columns or x in columns_remove:
            df = df.drop(columns=x)
    return [df,missing_columns]


def mapColumnsAPI(df):
    to_time=['time']
    to_numeric = ['status', 'db_count', 'cpu_s', 'queue_duration_s', 'duration_s',  'db_duration_s', 'view_duration_s', 'redis_duration_s', 'mem_total_bytes', 'mem_bytes']
    for l in to_time:
        df[l] = pd.to_datetime(df[l])
    for l in to_numeric:
        df[l] = pd.to_numeric(df[l])
    df.fillna(0, inplace=True)
    return df 