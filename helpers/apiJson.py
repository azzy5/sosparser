import json
import matplotlib.pylab as plt
import pandas as pd
from .utils import *
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
    to_numeric = ['status', 'db_count', 'cpu_s', 'duration_s',  'db_duration_s', 'view_duration_s', 'redis_duration_s', 'mem_total_bytes', 'mem_bytes']
    for l in to_time:
        df[l] = pd.to_datetime(df[l])
    for l in to_numeric:
        df[l] = pd.to_numeric(df[l])
    df.fillna(0, inplace=True)
    return df 


def metadataAPI(df):
    meta_ = {}
    meta_['Count'] = df.query('correlation_id != ""')['correlation_id'].count()
    meta_['RPS'] = round((meta_['Count']/(df.iloc[-1]['time'] - df.iloc[0]['time']).total_seconds()),1)
    meta_['Duration'] = timeConversion(df['duration_s'].sum())
    meta_['DB Duration'] = timeConversion(df['db_duration_s'].sum())
    meta_['Redis Duration'] = timeConversion( df['redis_duration_s'].sum())
    meta_['Gitaly Duration'] = timeConversion( df['gitaly_duration_s'].sum())
    meta_['CPU'] = timeConversion( df['cpu_s'].sum())
    meta_['Memory'] = convert_storage_units(df['mem_bytes'].sum()/1024,'KB')
    return meta_


dict_cType = {
    'Project':'meta.project',  'Path':'path', 'User': 'meta.user', 'Puma Worker' : 'worker_id', 'Route' : 'route'
}

dict_filter = {
    'Duration':'duration_s', 'Memory' : 'mem_bytes' ,'DB Duration':'db_duration_s', 'CPU' :'cpu_s'
}

def getTopInfoAPI(df, cType='meta.project',filter_type = 'duration_s'):
    cType = dict_cType[cType]
    filter_type = dict_filter[filter_type]
    t_duration = {}
    df = df.loc[df[cType] != 0]
    sorted_duration = df[cType].value_counts().sort_values(ascending=False)
    for value in sorted_duration.index:
        t_duration[value] = df.query("`{}` == '{}'".format(cType, value))['{}'.format(filter_type)].sum()
    t_duration = sorted(t_duration.items(), key=lambda x: x[1], reverse=True)
    cType_data = []
    for cType_ in t_duration[:10]:
        t = {}
        t['TYPE'] = cType_[0]
        t['COUNT'] = df.query("`{}` == '{}'".format(cType, cType_[0]))[cType].value_counts()[0]
        t['DUR'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['duration_s'].sum())
        t['DB_DUR'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['db_duration_s'].sum())
        t['REDIS'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['redis_duration_s'].sum())
        t['GTLY'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['gitaly_duration_s'].sum())
        t['CPU'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['cpu_s'].sum())
        t['MEM'] = convert_storage_units(df.query("`{}` == '{}'".format(cType, cType_[0]))['mem_bytes'].sum()/1024,"kb")
        cType_data.append(t)
    return cType_data 

