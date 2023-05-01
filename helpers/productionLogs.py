import json
import matplotlib.pylab as plt
from .utils import *
import pandas as pd
from pandas import json_normalize

prodcution_columns = [
    "method",
    "path",
    "format",
    "controller",
    "action",
    "status",
    "time",
    "params",
    "correlation_id",
    "meta.caller_id",
    "meta.remote_ip",
    "meta.feature_category",
    "meta.client_id",
    "meta.project",
    "ua",
    "remote_ip",
    "meta.user",
     "meta.user_id",
     "graphql",
     "user_id",
     "username",
     "redis_allowed_cross_slot_calls",
     "redis_sessions_allowed_cross_slot_calls",
     "redis_shared_state_calls",
     "redis_shared_state_duration_s",
     "redis_shared_state_write_bytes",
    "ua",
    "queue_duration_s",
    "request_urgency",
    "target_duration_s",
    "redis_calls",
    "redis_duration_s",
    "redis_read_bytes",
    "redis_write_bytes",
    "redis_cache_calls",
    "redis_cache_duration_s",
    "redis_cache_read_bytes",
    "redis_cache_write_bytes",
    "redis_sessions_calls",
    "redis_sessions_duration_s",
    "redis_sessions_read_bytes",
    "redis_sessions_write_bytes",
    "db_count",
    "db_write_count",
    "db_cached_count",
    "db_replica_count",
    "db_primary_count",
    "db_main_count",
    "db_main_replica_count",
    "db_replica_cached_count",
    "db_primary_cached_count",
    "db_main_cached_count",
    "db_main_replica_cached_count",
    "db_replica_wal_count",
    "db_primary_wal_count",
    "db_main_wal_count",
    "db_main_replica_wal_count",
    "db_replica_wal_cached_count",
    "db_primary_wal_cached_count",
    "db_main_wal_cached_count",
    "db_main_replica_wal_cached_count",
    "db_replica_duration_s",
    "db_primary_duration_s",
    "db_main_duration_s",
    "db_main_replica_duration_s",
    "cpu_s",
    "mem_objects",
    "mem_bytes",
    "mem_mallocs",
    "mem_total_bytes",
    "pid",
    "worker_id",
    "gitaly_duration_s",
    "rate_limiting_gates",
    "db_duration_s",
    "view_duration_s",
    "duration_s",
]


def read_log_file_pr(file_path):
    print("reading file")
    lines = []
    debug = []
    with open(
        file_path + "/var/log/gitlab/gitlab-rails/production_json.log", "r"
    ) as file:
        log_lines = file.readlines()
    for x, line in enumerate(log_lines):
        try:
            l = json.loads(line)
            lines.append(l)
            if len(l) == 3:
                if len(l["message"].split(" ")) < 4:
                    debug.append(l)
        except:
            if line != "\n":
                debug.append(line)
    return [lines, debug]


dict_cType = {
    'Controller':'controller',  'Project':'meta.project','Path': 'path', 'Remote IP' : 'remote_ip', 'User': 'meta.user', 'Worker ID' : 'worker_id', 'User Agent' : 'ua'
}

dict_filter = {
    'Duration':'duration_s', 'Memory' : 'mem_bytes' ,'DB Duration':'db_duration_s', 'CPU' :'cpu_s'
}

def getTopInfoPD(df, cType='status',filter_type = 'duration_s'):
    if cType == 'Controller':
        df['controller'] = df['controller'] + df['action']
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


def convert_to_dataframe(log_data):
    return json_normalize(log_data)

def filterColumnsPD(df):
    columns_remove = ["db_main_replica_duration_s","db_replica_duration_s","db_main_replica_wal_cached_count","db_main_wal_cached_count","db_primary_wal_cached_count","db_main_wal_count","db_main_replica_wal_count","db_replica_wal_cached_count","db_write_count","db_primary_wal_count","db_replica_count", "db_main_replica_count", "db_replica_cached_count","db_primary_wal_count," "db_replica_count","db_main_replica_cached_count", "db_replica_wal_count"]
    missing_columns = []
    missing_columns = [column for column in prodcution_columns if column not in df.columns]
    missing_columns = [elem for elem in missing_columns if elem not in columns_remove]
    for column in missing_columns:
        if column not in df.columns:
            df[column] = 0
    for x in df.columns:
        if x not in prodcution_columns or x in columns_remove:
            df = df.drop(columns=x)
    return [df,missing_columns]

def mapColumnsPD(df):
    to_time=['time']
    to_numeric = ['status', 'db_count', 'cpu_s', 'queue_duration_s', 'duration_s',  'db_duration_s', 'view_duration_s', 'redis_duration_s', 'mem_total_bytes', 'mem_bytes', 'cpu_s']
    for l in to_time:
        df[l] = pd.to_datetime(df[l])
    for l in to_numeric:
        df[l] = pd.to_numeric(df[l])
    df.fillna(0, inplace=True)
    return df 

def timeConversion(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    formatted_duration = f"{int(hours)}h" if hours >= 1 else ""
    formatted_duration += f"{int(minutes)}m" if minutes >= 1 else ""
    formatted_duration += f"{seconds:.1f}s" if seconds >= 0.1 else ""
    return formatted_duration

#MetaData extraction and return

def metadataPD(df):
    meta_ = {}
    meta_['Count'] = df.shape[0]
    meta_['Duration'] = timeConversion( df['duration_s'].sum())
    meta_['RPS'] = round(meta_['Count']/df['duration_s'].sum(), 2)
    meta_['DB Duration'] = timeConversion( df['db_duration_s'].sum())
    meta_['Redis Duration'] = timeConversion( df['redis_duration_s'].sum())
    meta_['Queue Duration'] = timeConversion( df['queue_duration_s'].sum())
    meta_['CPU'] = timeConversion( df['cpu_s'].sum())
    meta_['Memory'] = convert_storage_units(df['mem_bytes'].sum()/1024,'KB')
    return meta_

def showWarningsPD(df):
    return df.query('status > 200 and status <= 299')[['time','correlation_id' ,'status','controller']]

def showWarningsPD1(df):
    return df.query('status > 300 and status <= 399')[['time','correlation_id' ,'status','controller']]

def showErrorsPD(df):
    return df.query('status > 399 and status <= 499')[['time','correlation_id' , 'status','controller']]

def showErrorsPD1(df):
    return df.query('status > 499')[['time','correlation_id' , 'status','controller']]