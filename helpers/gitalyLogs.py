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

def timeConversion(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    formatted_duration = f"{int(hours)}h" if hours >= 1 else ""
    formatted_duration += f"{int(minutes)}m" if minutes >= 1 else ""
    formatted_duration += f"{seconds:.1f}s" if seconds >= 0.1 else ""
    return formatted_duration