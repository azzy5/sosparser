# global variables
error_class = 'alert alert-danger'
success_class = 'alert alert-success'
# checks if connected to the internal server : time out is 3 seconds
# def isInternalNetwork():
#     response =  os.system("ping -c 1 -W 3 " + "10.50.40.166")
#     return False if (response>0) else True

files_ = [
    '/lscpu', '/free_m',  '/uptime', '/gitlab_status', '/gitlab_migrations', '/df_hT',
    '/pressure_cpu.txt', '/top_cpu' , '/var/log/gitlab/gitlab-rails/production_json.log', '/var/log/gitlab/sidekiq/current'
]

def getFilteredDataSK(df):
    return df[['time', 'severity', 'cpu_s', 'duration_s', 'db_duration_s']]

def convert_storage_units(value, input_unit="KB"):
    if input_unit.upper() == "KB":
        mb = value / 1024
    elif input_unit.upper() == "MB":
        mb = value

    if mb < 1024:
        return f"{mb:.2f} MB"
    else:
        gb = mb / 1024
        return f"{gb:.2f} GB"

custom_css_prd = {
    ".ag-row-hover": {"background-color": "#70dfdb !important"},
    ".ag-header": {"background-color": "white !important", "font-size": "15px !important", "font-color": "black !important","border": "1px solid #eee !important;", "align": "left !important"},
    }