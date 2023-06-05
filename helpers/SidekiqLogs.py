from inspect import iscode
from pandas import json_normalize
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode
import json



sidekiq_columns = [
    "severity",
    "time",
    "retry",
    "meta.remote_ip",
    "meta.user",
    "meta.user_id",
    "meta.related_class",
    "meta.pipeline_id",
    "external_http_count",
    "external_http_duration_s",
    "queue",
    "version",
    "queue_namespace",
    "args",
    "class",
    "jid",
    "created_at",
    "scheduled_at",
    "meta.caller_id",
    "correlation_id",
    "meta.root_caller_id",
    "meta.feature_category",
    "meta.client_id",
    "worker_data_consistency",
    "wal_locations",
    "wal_location_source",
    "idempotency_key",
    "size_limiter",
    "enqueued_at",
    "job_size_bytes",
    "pid",
    "message",
    "job_status",
    "meta.project",
    "meta.job_id",
    "scheduling_latency_s",
    "redis_calls",
    "redis_duration_s",
    "redis_read_bytes",
    "redis_write_bytes",
    "redis_queues_calls",
    "redis_queues_duration_s",
    "redis_queues_read_bytes",
    "redis_queues_write_bytes",
    "redis_shared_state_calls",
    "redis_shared_state_duration_s",
    "redis_shared_state_read_bytes",
    "redis_shared_state_write_bytes",
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
    "gitaly_duration_s",
    "mem_total_bytes",
    "worker_id",
    "rate_limiting_gates",
    "extra.elastic_index_initial_bulk_cron_worker.records_count",
    "extra.elastic_index_initial_bulk_cron_worker.shard_number",
    "duration_s",
    "completed_at",
    "load_balancing_strategy",
    "db_duration_s",
]


def setupChartContorlsSK():
    cols = st.columns([3, 3, 3, 4, 3])
    cols[0].button("Show all columns")
    cols[1].button("Show all errors")
    cols[2].button("Show all warnings")
    cols[3].button("Get all selected rows")
    return True


def setupAGChart(df):
    gb = GridOptionsBuilder.from_dataframe(df)

    # makes columns resizable, sortable and filterable by default
    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
        width="100%",
        theme="ag-solar",
        enable_enterprise_modules = False
    )
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection("multiple", use_checkbox=True)  # Enable multi-row selection
    gb.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=20
    )
    gb.configure_auto_height(autoHeight=True),
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    data_return_mode = ("AS_INPUT")
    enable_enterprise_modules = (False,)
    groupIncludeFooter = True
    return gb.build()

def setupSmallAGChart(df):
    gb = GridOptionsBuilder.from_dataframe(df)

    # makes columns resizable, sortable and filterable by default
    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
        enable_enterprise_modules = False
    )
    gb.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=10
    )
    gb.configure_side_bar() 
    gb.configure_auto_height(autoHeight=True),
    return gb.build()

    
def read_log_file(file_path):
    print("reading file")
    lines = []
    debug = []
    with open(file_path + "/var/log/gitlab/sidekiq/current", "r") as file:
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


def convert_to_dataframe(log_data):
    return json_normalize(log_data)


def filterColumns(df):
    columns_remove = [
        "args",
        "extra.database_ci_namespace_mirrors_consistency_check_worker.results",
        "extra.elastic_index_initial_bulk_cron_worker.shard_number",
        "extra.elastic_index_initial_bulk_cron_worker.records_count",
        "db_main_replica_duration_s",
        "db_main_replica_wal_cached_count",
        "db_main_wal_cached_count",
        "db_primary_wal_cached_count",
        "db_main_replica_wal_count",
        "db_replica_cached_count",
        "db_replica_wal_count",
        "db_replica_count",
        "wal_locations",
        "db_main_replica_count",
        "db_main_replica_cached_count" ,
        "db_primary_wal_count",
        "db_main_wal_count",
        "db_replica_wal_cached_count",
        "db_replica_duration_s"
    ]
    missing_columns = []
    missing_columns = [column for column in sidekiq_columns if column not in df.columns]
    missing_columns = [elem for elem in missing_columns if elem not in columns_remove]
    for column in missing_columns:
        if column not in df.columns:
            df[column] = 0
            assert (df[column] == 0).all(), f"Unexpected non-zero values in {column}"
    for x in df.columns:
        if x not in sidekiq_columns or x in columns_remove:
            df = df.drop(columns=x)
    return [df,missing_columns]

dict_cType = {
    'User':'meta.user', 'Project': 'meta.project', 'Class' : 'class'
}

dict_filter = {
    'Duration':'duration_s', 'Memory' : 'mem_bytes' ,'DB Duration':'db_duration_s', 'CPU':'cpu_s'
}

def getTopInfo(df, cType='meta.user',filter_type = 'duration_s'):
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
        dur_ = df.query("`{}` == '{}'".format(cType, cType_[0]))['duration_s'].sum()
        t['TYPE'] = cType_[0]
        t['COUNT'] = df.query("job_status =='done' and `{}` == '{}'".format(cType, cType_[0]))[cType].count()
        t['RPS'] = (df['meta.user'].count()/dur_)
        t['DUR'] = timeConversion(dur_)
        t['DB'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['db_duration_s'].sum())
        t['REDIS'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['redis_duration_s'].sum())
        t['GITLY'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['gitaly_duration_s'].sum())
        t['CPU'] = timeConversion(df.query("`{}` == '{}'".format(cType, cType_[0]))['cpu_s'].sum())
        t['MEM'] = convert_storage_units(df.query("`{}` == '{}'".format(cType, cType_[0]))['mem_bytes'].sum()/1024,"KB")
        cType_data.append(t)
    return cType_data   

def metadataSK(df):
    meta_ = {}
    meta_['Count'] = df.query('job_status =="done"')['job_status'].count()
#    meta_['RPS'] = round((meta_['Count']/(df.iloc[-1]['time'] - df.iloc[0]['time']).total_seconds()),1)
    meta_['Duration'] = timeConversion( df['duration_s'].sum())
    meta_['DB Duration'] = timeConversion( df['db_duration_s'].sum())
    meta_['Redis Duration'] = timeConversion( df['redis_duration_s'].sum())
    meta_['Gitaly Duration'] = timeConversion( df['gitaly_duration_s'].sum())
    meta_['CPU'] = timeConversion( df['cpu_s'].sum())
    meta_['Memory'] = convert_storage_units(df['mem_bytes'].sum()/1024,"KB")
    return meta_


def timeConversion(seconds):
    hours, rem = divmod(int(seconds), 3600)
    minutes, seconds = divmod(rem, 60)
    formatted_duration = f"{hours}h" if hours > 0 else ""
    formatted_duration += f"{minutes}m" if minutes > 0 else ""
    formatted_duration += f"{seconds}s"
    return formatted_duration

def mapColumns(df):
    to_time = ["completed_at", "time", "created_at", "enqueued_at"]
    to_numeric = [
        "duration_s",
        "cpu_s",
        "redis_duration_s",
        "redis_read_bytes",
        "redis_write_bytes",
        "redis_queues_duration_s",
        "redis_shared_state_duration_s",
        "mem_objects",
        "mem_bytes",
        "mem_mallocs",
        "mem_total_bytes",
    ]
    for l in to_time:
        df[l] = pd.to_datetime(df[l])
    for l in to_numeric:
        df[l] = pd.to_numeric(df[l])
    df.fillna(0, inplace=True)
    return df

def showWarningsSK(df):
    return df.query('severity == "WARN"')[['time', 'correlation_id' ,'severity','message']]

def showErrorsSK(df):
    return df.query('severity == "ERROR"')[['time' ,'correlation_id' , 'severity','message']]

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