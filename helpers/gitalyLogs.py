import json
import matplotlib.pylab as plt
import pandas as pd
from pandas import json_normalize


gitaly_columns = ['correlation_id', 'grpc.code', 'grpc.meta.auth_version',
       'grpc.meta.client_name', 'grpc.meta.deadline_type',
       'grpc.meta.method_type', 'grpc.method', 'grpc.request.deadline',
       'grpc.request.fullMethod', 'grpc.request.glProjectPath',
       'grpc.request.glRepository', 'grpc.request.payload_bytes',
       'grpc.request.repoPath', 'grpc.request.repoStorage',
       'grpc.response.payload_bytes', 'grpc.service', 'grpc.start_time',
       'grpc.time_ms', 'level', 'msg', 'peer.address', 'pid', 'remote_ip',
       'span.kind', 'system', 'time', 'user_id', 'username', 'command.count',
       'command.cpu_time_ms', 'command.inblock', 'command.majflt',
       'command.maxrss', 'command.minflt', 'command.oublock',
       'command.real_time_ms', 'command.system_time_ms',
       'command.user_time_ms', 'response_bytes', 'request_sha', 'stream_path',
       'service', 'diskcache', 'error', 'content_length_bytes', 'duration_ms',
       'method', 'status', 'url']

def read_log_file_gt(file_path):
    lines =[]
    debug = []
    with open(file_path + "/var/log/gitlab/gitaly/current", 'r') as file:
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
    return [lines,debug]

def convert_to_dataframe(log_data):
    return json_normalize(log_data)

def filterColumnsGT(df):
    columns_remove = []
    missing_columns = []
    missing_columns = [column for column in gitaly_columns if column not in df.columns]
    missing_columns = [elem for elem in missing_columns if elem not in columns_remove]
    for column in missing_columns:
        if column not in df.columns:
            df[column] = 0
    for x in df.columns:
        if x not in gitaly_columns or x in columns_remove:
            df = df.drop(columns=x)
    return [df,missing_columns]

def mapColumnsGT(df):
    to_time = ["grpc.start_time", "grpc.request.deadline", "time"]
    to_numeric = [
        "grpc.request.payload_bytes",
        "grpc.response.payload_bytes",
        "grpc.time_ms",
        "command.count",
        "command.cpu_time_ms",
        "command.inblock",
        "command.majflt",
        "command.maxrss",
        "command.minflt",
        "command.oublock",
        "command.real_time_ms",
        "duration_ms",
        "status"
        
    ]
    for l in to_time:
        df[l] = pd.to_datetime(df[l],errors='ignore')
    for l in to_numeric:
        df[l] = pd.to_numeric(df[l])
    df.fillna(0, inplace=True)
    return df


def metadataGT(df):
    meta_ = {}
    meta_['Count'] = df.query('`grpc.code` == "OK"')['grpc.code'].count()
    meta_['RPS'] = round((meta_['Count']/(df.iloc[-1]['time'] - df.iloc[0]['time']).total_seconds()),1)
    meta_['Duration'] = timeConversion( df['grpc.time_ms'].sum()/1000)
    meta_['CPU'] = timeConversion( (df['command.system_time_ms'].sum()+df['command.user_time_ms'].sum())/1000)
    meta_['GIT_RSS'] = convert_storage_units(df['command.maxrss'].sum())
    meta_['Response Bytes'] =  convert_storage_units(df['response_bytes'].sum()/1024)
    meta_['Disk Read'] =  df['command.inblock'].sum()
    meta_['Disk Write'] =  df['command.oublock'].sum()
    meta_['Fail Count'] = df.query('`grpc.code` == "NotFound"')['error'].count()
    return meta_

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
        
def timeConversion(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    formatted_duration = f"{int(hours)}h" if hours >= 1 else ""
    formatted_duration += f"{int(minutes)}m" if minutes >= 1 else ""
    formatted_duration += f"{seconds:.1f}s" if seconds >= 0.1 else ""
    return formatted_duration

dict_cType = {
    'Project':'grpc.request.glProjectPath', 'User': 'username', 'Client':'grpc.meta.client_name', 'Service' : 'grpc.service'
}

dict_filter = {
    'Duration':'grpc.time_ms', 'Command CPU Time' : 'command.cpu_time_ms' ,'GRPC Time (ms)':'grpc.time_ms', 'Response Bytes' : 'response_bytes' 
}

def getTopInfoGT(df, cType='grpc.request.glProjectPath',filter_type = 'grpc.time_ms'):
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
        dur_ = df.query("`{}` == '{}'".format(cType, cType_[0]))['grpc.time_ms'].sum()/1000
        t['TYPE'] = cType_[0]
        t['COUNT'] = df.query("`grpc.code` == 'OK' and `{}` == '{}'".format(cType, cType_[0]))[cType].count()
#        t['RPS'] = t['COUNT']/dur_
        t['DUR'] = timeConversion(dur_)
        t['CPU'] = timeConversion((df.query("`{}` == '{}'".format(cType, cType_[0]))['command.cpu_time_ms'].sum()+df.query("`{}` == '{}'".format(cType, cType_[0]))['command.user_time_ms'].sum())/1000)
        t['GIT_RSS'] = convert_storage_units(df.query("`{}` == '{}'".format(cType, cType_[0]))['command.maxrss'].sum()/1024)
        t['RESP_BYTES'] = convert_storage_units(df.query("`{}` == '{}'".format(cType, cType_[0]))['response_bytes'].sum())
        t['DISK_READ'] = (df.query("`{}` == '{}'".format(cType, cType_[0]))['command.inblock'].sum())
        t['DISK_WRITE'] = (df.query("`{}` == '{}'".format(cType, cType_[0]))['command.oublock'].sum())
        cType_data.append(t)
    return cType_data 
