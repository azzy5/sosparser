# AgGrid (free) https://www.ag-grid.com/javascript-data-grid/getting-started/
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode

# pandas: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html 
import pandas as pd

# streamlit : https://discuss.streamlit.io
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_plotly_events import plotly_events

from helpers.file_process import *
from helpers.gitalyLogs import *
from helpers.plotting import *
from helpers.productionLogs import *
from helpers.sidekiqLogs import *
from helpers.apiJson import *
from helpers.utils import *
from helpers.workhorse import *

from PIL import Image
from os.path import exists

def validateFilepath(file_, c):
    file_path = file_
    with c:
        for f in files_:
            if exists(file_ + f):
                st.markdown(" Read file : _*" + f + "*_  :white_check_mark:")
            else:
                return False
    return True

def main():
    initialize()
    file_path = ""
    with st.sidebar:
        # Ensure "Metadata" remains top of menu after "Home" in sidebar for quick system details check
        menuItems = ["Home", "Metadata","Version Manifest", "Gitaly", "Production", "Sidekiq","API Json", "Workhorse"]
        choice = option_menu(
            "Menu",
            menuItems,
            icons=[
                "house",
                "book fill",
                "123",
                "git",
                "gear",
                "kanban",
                "arrow-down-up",
                "pc-display-horizontal"
                
            ],
            menu_icon="app-indicator",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#0a0a0a"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "20px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "grey",
                },
                "nav-link-selected": {"background-color": "#02ab21"},
            },
        )

    if choice == "Home":
        logo("\U0001F6A8	SOS \U0001F6A8 Parser \U0001F5C3")
        indexPage()
    elif choice == "Version Manifest":
        logo("Version Manifest :1234:")
        versionMainfestPage()
    elif choice == "Gitaly":
        logo("Gitaly Logs :hourglass_flowing_sand:")
        if checkFileExists(st.session_state.file_path,"Gitaly"):
            gitalyPage()
        else:
            logFileNotFound("Gitaly")
    elif choice == "Metadata":
        logo("Metadata :warning:")
        metadataPage()
    elif choice == "Production":
        logo("Production Logs :gear:")
        if checkFileExists(st.session_state.file_path,"Production"):
            productionLogsPage()
        else:
            logFileNotFound("Production")
    elif choice == "Sidekiq":
        logo("Sidekiq Logs \U0001F916")
        if checkFileExists(st.session_state.file_path,"Sidekiq"):
            sidekiqPage()
        else:
            logFileNotFound("Sidekiq")
    elif choice == "API Json":
        logo("API Json :spiral_note_pad:")
        if checkFileExists(st.session_state.file_path,"API"):
            apiJsonLogs()
        else:
            logFileNotFound("API")
    elif choice == "Workhorse":
        logo("Workhorse Logs :mechanical_arm:")
        if checkFileExists(st.session_state.file_path,"Workhorse"):
            workhorsePage()
        else:
            logFileNotFound("Workhorse")
    return True

def gitalyPage():
    if st.session_state.valid:
        df,debug = getGitalyDataFrame(st.session_state.file_path)
        df,missing_columns = filterColumnsGT(df)
        df = mapColumnsGT(df)
        if len(missing_columns) > 0:
            st.warning(
                "The following columns are missing from the log file : {}".format(
                    ", ".join(missing_columns))
                )
            st.warning("The tool will auto populate the missing columns with default values, so the results might be inaccurate")
        cm = st.columns([1, 1, 1, 1, 1, 1, 1, 1,1])
        metadata = metadataGT(df)
        for x, meta_in in enumerate(metadata.keys()):
            cm[x].metric(meta_in, metadata[meta_in])
        goShort = setupAGChart(df)
        response = AgGrid(
            df, gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True
        )
        selected = response["selected_rows"]
        if selected:
            st.markdown(
                '<p class="font1">  Selected rows :  </p>', unsafe_allow_html=True
            )
            AgGrid(convert_to_dataframe(selected))
            sjl = st.button("Show Job Logs")
            if sjl:
                st.markdown(
                    '<p class="font1">  JSON Logs :  </p>', unsafe_allow_html=True
                )
                st.write(getJobLogsForCorrelationID(selected,st.session_state.file_path ,"Gitaly"))
        slt1, slt2, slt3 = st.columns([2, 2, 6])
        top_type = slt1.selectbox(" ", ("Project", "User", "Client", "Service"))
        top_filter = slt2.selectbox(" ", ("Duration", "Command CPU Time", "GRPC Time (ms)", "Response Bytes"))
        dt = pd.json_normalize(getTopInfoGT(df, top_type, top_filter))
        st.markdown(
            '<p class="font1"> Top 10 {} by {} </p>'.format(top_type, top_filter),
            unsafe_allow_html=True,
        )
        goShort = setupSmallAGChart(dt)
        AgGrid(dt,gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True)
        st.divider()
        fig = interactiveGraph(df)
#        st.plotly_chart(fig, use_container_width=True)
        selected_point = plotly_events(fig, click_event=True, hover_event=False)
        if selected_point:
#            st.write(selected_point)
            timeStamp =pd.to_datetime(selected_point[0]["x"],utc=True).isoformat()
            st.table(df.query("time == '{}'".format(timeStamp)))
        return True
    else:
        filePathExists()

def metadataPage():
    if st.session_state.valid:
        pm1, pm2 = st.columns([6, 2])
        with pm1:
            m1, m2, m3 = st.columns([3, 2, 3], gap="small")
            m5, m6 = st.columns([2, 1], gap="small")
            # CPU info
            with m1:
                m1.markdown('<p class="font1"> CPU Details </p>', unsafe_allow_html=True)
                if st.session_state.valid:
                    cpu_ = extract_cpuInfo(st.session_state.file_path)
                    for c in cpu_:
                        m1.markdown("**" + c + " : " + str(cpu_[c]) + "**")
                    m1.markdown("---")
                else:
                    m1.markdown("No data found")
            # Memory info
            with m2:
                m2.markdown('<p class="font1"> Memory </p>', unsafe_allow_html=True)
                if st.session_state.valid:
                    mem_info = meminfo(st.session_state.file_path)
                    for c in mem_info:
                        m2.markdown("**" + c + " : " + convert_storage_units(int(mem_info[c]),"MB") + "**")
                    m2.markdown("---")
                else:
                    m2.markdown("No data found")

            # Up time
            with m3:
                m3.markdown('<p class="font1"> Uptime  </p>', unsafe_allow_html=True)
                if st.session_state.valid:
                    up_time = uptime(st.session_state.file_path)
                    for c in up_time:
                        m3.markdown("**" + c + " : " + str(up_time[c]) + "**")
                    m3.markdown("---")
                else:
                    m3.markdown("No data found")

            # Top five mounts
            with m5:
                m5.markdown(
                    '<p class="font1">  Top 5 Disk mounts  </p>', unsafe_allow_html=True
                )
                if st.session_state.valid:
                    disk_mount = parse_df_hT_output(st.session_state.file_path)
                    data_ = []
                    data_.append(disk_mount[0].keys())
                    for d in disk_mount:
                        data_.append(d.values())
                    m5.table(data_)
                    m5.markdown("---")
                else:
                    m5.markdown("No data found")

            # CPU_Test
            with m6:
                m6.markdown(
                    '<p class="font1"> CPU Pressure test  </p>', unsafe_allow_html=True
                )
                if st.session_state.valid:
                    cpu_pressure = pressure_results(st.session_state.file_path)[0]
                    data_ = []
                    data_x = []
                    data_.append(cpu_pressure["some"].keys())
                    for d in cpu_pressure["some"]:
                        data_x.append(cpu_pressure["some"][d])
                    data_.append(data_x)
                    data_x = []
                    data_.append(cpu_pressure["full"].keys())
                    for d in cpu_pressure["full"]:
                        data_x.append(cpu_pressure["full"][d])
                    data_.append(data_x)
                    m6.table(data_)
                    m6.markdown("---")
                else:
                    m6.markdown("No data found")

            # Top 10 processes
            with pm1:
                pm1.markdown(
                    '<p class="font1"> Top 10 processes  </p>', unsafe_allow_html=True
                )
                if st.session_state.valid:
                    top_p = extract_top_processes(st.session_state.file_path)
                    data_ = []
                    for d in top_p:
                        pm1.text(d + "\n")
                    pm1.markdown("---")
                else:
                    pm1.markdown("No data found")

            # Failed migrations
            with pm1:
                pm1.markdown(
                    '<p class="font1"> Failed migrations </p>', unsafe_allow_html=True
                )
                if st.session_state.valid:
                    failed_migration = failed_migrations(st.session_state.file_path)
                    data_ = []
                    if failed_migration:
                        data_.append(failed_migration[0].keys())
                    for d in failed_migration:
                        data_.append(d.values())
                    pm1.table(data_)
                    pm1.markdown("---")
                else:
                    pm1.markdown("No data found")

        # Gitlab services
        with pm2:
            pm2.markdown('<p class="font1"> GitLab Services  </p>', unsafe_allow_html=True)
            if st.session_state.valid:
                s_status = extract_services(st.session_state.file_path)
                for s in s_status:
                    pm2.markdown(
                        "**" + s + " : " + ("✅" if s_status[s] == "run:" else "🔥") + "**"
                    )
                pm2.markdown("---")
            else:
                pm2.markdown("No data found")

            # Memory Test
            pm2.markdown(
                '<p class="font1">  Memory Pressure test  </p>', unsafe_allow_html=True
            )
            if st.session_state.valid:
                cpu_pressure = pressure_results(st.session_state.file_path)[1]
                data_ = []
                data_x = []
                data_.append(cpu_pressure["some"].keys())
                for d in cpu_pressure["some"]:
                    data_x.append(cpu_pressure["some"][d])
                data_.append(data_x)
                data_x = []
                data_.append(cpu_pressure["full"].keys())
                for d in cpu_pressure["full"]:
                    data_x.append(cpu_pressure["full"][d])
                data_.append(data_x)
                pm2.markdown("---")
            else:
                pm2.markdown("No data found")
        return True
    else:
        filePathExists()

def productionLogsPage():
    if st.session_state.valid:
        df, debug = getProductionLogDF(st.session_state.file_path)
        df,missing_columns = filterColumnsPD(df)
        df = mapColumnsPD(df)
        if len(missing_columns) > 0:
            st.warning(
                "The following columns are missing from the log file : {}".format(
                    ", ".join(missing_columns))
                )
            st.warning("The tool will auto populate the missing columns with default values, so the results might be inaccurate")
        cm = st.columns([1, 1, 1, 1, 1, 1,1,1])
        metadata = metadataPD(df)
        for x, meta_in in enumerate(metadata.keys()):
            cm[x].metric(meta_in, metadata[meta_in])
        go = setupAGChart(df)
        response = AgGrid(
            df, gridOptions=go, custom_css=custom_css_prd, allow_unsafe_jscode=True,  key = "logTable"
        )
        selected = response["selected_rows"]
        if selected:
            st.markdown(
                '<p class="font1">  Selected rows :  </p>', unsafe_allow_html=True
            )
            AgGrid(convert_to_dataframe(selected), gridOptions=go)
            sjl = st.button("Show Job Logs")
            if sjl:
                st.markdown(
                    '<p class="font1">  JSON Logs :  </p>', unsafe_allow_html=True
                )
                st.write(getJobLogsForCorrelationID(selected,st.session_state.file_path ,"Production"))
        slt1, slt2, slt3 = st.columns([2, 2, 6])
        top_type = slt1.selectbox(" ", ['Controller','Project','Path', 'Remote IP', 'User', 'Worker ID', 'User Agent'])
        top_filter = slt2.selectbox(" ", ("Duration", "Memory", "DB Duration", "CPU"))
        dt = pd.json_normalize(getTopInfoPD(df, top_type, top_filter))
        st.markdown(
            '<p class="font1"> Top 10 {} by {} </p>'.format(top_type, top_filter),
            unsafe_allow_html=True,
        )
        go = setupSmallAGChart(dt)
        AgGrid(dt,gridOptions=go, custom_css=custom_css_prd, allow_unsafe_jscode=True)
        st.divider()
        errors_ = showErrorsPD(df)
        goShort = setupSmallAGChart(errors_)
        st.markdown(
            '<p class="font2">  Status between 400 - 500  </p>', unsafe_allow_html=True
        )
        AgGrid(errors_,gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True, key = "400Table")
        errors_ = showErrorsPD1(df)
        st.markdown(
            '<p class="font2">  Status above 499  </p>', unsafe_allow_html=True
        )
        AgGrid(errors_,gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True, key = "500Table")
        st.divider()
        fig = interactiveGraph(df)
#        st.plotly_chart(fig, use_container_width=True)
        selected_point = plotly_events(fig, click_event=True, hover_event=False)
        if selected_point:
#            st.write(selected_point)
            timeStamp =pd.to_datetime(selected_point[0]["x"],utc=True).isoformat()
            st.table(df.query("time == '{}'".format(timeStamp)))
        return True
    else:
        filePathExists()


@st.cache_data()
def getProductionLogDF(file_path):
    lines, debug = read_log_file_pr(file_path)
    df = convert_to_dataframe(lines)
    return [df,debug]


@st.cache_data()
def getSKDataFrame(file_path):
    log_file, debug = read_log_file(file_path)
    df = convert_to_dataframe(log_file)
    return [df,debug]

@st.cache_data()
def getGitalyDataFrame(file_path):
    log_file, debug = read_log_file_gt(file_path)
    df = convert_to_dataframe(log_file)
    return [df,debug]

@st.cache_data()
def getAPIDataFrame(file_path):
    log_file, debug = read_log_file_api(file_path)
    df = convert_to_dataframe(log_file)
    return [df,debug]

@st.cache_data()
def getWorkhorseLogs(file_path):
    df_logs, df_errors = read_log_file_wh(file_path)
    return [df_logs, df_errors]


def sidekiqPage():
    if st.session_state.valid:
        df, debug = getSKDataFrame(st.session_state.file_path)
        df,missing_columns = filterColumns(df)
        df = mapColumns(df)
        if len(missing_columns) > 0:
            st.warning(
                "The following columns are missing from the log file : {}".format(
                    ", ".join(missing_columns))
                )
            st.warning("The tool will auto populate the missing columns with default values, so the results might be inaccurate")
            
        cm = st.columns([1, 1, 1, 1, 1, 1, 1,0.5, 1, 1])
        metadata = metadataSK(df)
        for x, meta_in in enumerate(metadata.keys()):
            cm[x].metric(meta_in, metadata[meta_in])
        cm[8].metric(
            "Errors", df.query('severity == "ERROR"')["severity"].value_counts().get(0, 0)
        )
        cm[9].metric(
            "Warnings", df.query('severity == "WARN"')["severity"].value_counts().get(0, 0)
        )
        goShort = setupAGChart(df)
        response = AgGrid(
            df, gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True
        )
        selected = response["selected_rows"]
        if selected:
            st.markdown(
                '<p class="font1">  Selected rows :  </p>', unsafe_allow_html=True
            )
            AgGrid(convert_to_dataframe(selected))
            sjl = st.button("Show Job Logs")
            if sjl:
                st.markdown(
                    '<p class="font1">  JSON Logs :  </p>', unsafe_allow_html=True
                )
                st.write(getJobLogsForCorrelationID(selected,st.session_state.file_path ,"Sidekiq"))
        slt1, slt2, slt3 = st.columns([2, 2, 6])
        top_type = slt1.selectbox(" ", ("User", "Project", "Class"))
        top_filter = slt2.selectbox(" ", ("Duration", "Memory", "DB Duration", "CPU"))
        dt = pd.json_normalize(getTopInfo(df, top_type, top_filter))
        st.markdown(
            '<p class="font1"> Top 10 {} by {} </p>'.format(top_type, top_filter),
            unsafe_allow_html=True,
        )
        goShort = setupSmallAGChart(dt)
        AgGrid(dt,gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True)

        ##
	## Create tables for Warnings and Errors

        cw,ce = st.columns([1,1])
	
	##
	## Warnings table 
        
        with cw:
            warnings_ = showWarningsSK(df)
            goShort = setupSmallAGChart(warnings_)
            st.markdown(
                '<p class="font2">  Warnings  </p>', unsafe_allow_html=True
            )
            
            AgGrid(warnings_,gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True, key = "SKWarnings")
        
	#
	# Errors table 
	
        with ce:
            errors_ = showErrorsSK(df)
            goShort = setupSmallAGChart(errors_)
            st.markdown(
                '<p class="font2">  Errors  </p>', unsafe_allow_html=True
            )
            AgGrid(errors_,gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True, key = "SKErrors")
        
        st.divider()
        fig = interactiveGraph(df)
#        st.plotly_chart(fig, use_container_width=True)
        selected_point = plotly_events(fig, click_event=True, hover_event=False)
        if selected_point:
#            st.write(selected_point)
            timeStamp =pd.to_datetime(selected_point[0]["x"],utc=True).isoformat()
            st.table(df.query("time == '{}'".format(timeStamp)))
        return True
    else:
        filePathExists()


def apiJsonLogs():
    if st.session_state.valid:
        df, debug = getAPIDataFrame(st.session_state.file_path)
        df,missing_columns = filterColumnsAPI(df, df.columns)
        df = mapColumnsAPI(df)
        goShort = setupAGChart(df)
        response = AgGrid(
            df, gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True
        )
    else:
        filePathExists()


def process_file(file_):
    st.spinner(text="File uploaded, processing...")
    file__ = process_file(file_)
    return file__


def indexPage():
    c1, c2 = st.columns([6.5,3.5])
    with c1:
        st.markdown(
            " This tool uses *Streamlit & Pandas* libraries to parse and display the logs on the page."
        )
        st.markdown(
            "For more information on the tool, please refer to the project : [SOSParser](https://gitlab.com/gitlab-com/support/toolbox/sosparser)"
        )
        st.markdown(   "---")
        st.markdown(
            '<p class="font2">Input log details or select from previous entries</p>',
            unsafe_allow_html=True,
        )
        stb = st.text_input("Log directory path", key="path", placeholder="")
        stb1 = st.text_input("Comment (Optional) :", key="comment", placeholder="")
        scb = st.checkbox("Save log entry", value=True)
        if st.button("Submit"):
            with st.spinner(text="Validating the folder content, processing..."):
                if validateFilepath(stb, c2):
                    if scb:
                        saveLogEntry(stb, stb1)
                    st.session_state.valid = True
                    c2.markdown("---")
                    c2.markdown(
                        ":arrow_backward: Select the page from the dropdown menu in the side bar "
                    )
                    st.session_state.file_path = stb
                    c2.success("This is a success message!", icon="✅")
                else:
                    c2.error("Something went wrong, please check file path", icon="🔥")
        st.markdown(
            '<p class="font2">Last 10 log files</p>',
            unsafe_allow_html=True,
        )
        logHistory = showLogHistory()
        #st.table(logHistory)
        showTabls(logHistory,c2)

def initialize():
    st.set_page_config(
        page_title="SOS Parser",
        page_icon="\U0001F6A8",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if "file_path" not in st.session_state:
        st.session_state["file_path"] = ""
    if "valid" not in st.session_state:
        st.session_state["valid"] = False
    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    # Font 1
    st.markdown(
                """ <style> .font1 {
        font-size:30px ; color: #FF9633;} 
        </style> """,
        unsafe_allow_html=True,
    )
    # Font 2
    # Font 1
    st.markdown(
                """ <style> .font2 {
        font-size:35px ; color: #FF9633;} 
        </style> """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
            <style>
                .css-18e3th9 {
                        padding-top: 0rem;
                        padding-bottom: 10rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
                .css-1d391kg {
                        padding-top: 3.5rem;
                        padding-right: 1rem;
                        padding-bottom: 3.5rem;
                        padding-left: 1rem;
                    }
            </style>
            """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <style>
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
    overflow-wrap: break-word;
    white-space: break-spaces;
    color: green;
    }
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div p {
    font-size: 120% !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    return True

def logo(text):

    cl1,cl2,cl3 = st.columns([10,10,5])
    st.write(
        "<style>div.block-container{padding-top:0rem;}</style>",
        unsafe_allow_html=True,
    )
    cl1.title(text)
    image = Image.open('static/gitlab_logo.png')
    cl3.image(image,width=200)

def versionMainfestPage():
    if st.session_state.valid:
        data_ = getManifestVersions(st.session_state.file_path)
        cm = st.columns([1, 1, 1, 1, 1, 1,1,1])
        metadata = importantVersions(data_)
        print(metadata)
        for x, meta_in in enumerate(metadata.keys()):
            cm[x].metric(meta_in, metadata[meta_in])
        st.table(data_)
        return True
    else:
        filePathExists()

def workhorsePage():
    if st.session_state.valid:
        df_logs, df_errors = getWorkhorseLogs(st.session_state.file_path)
        goShort = setupAGChart(df_logs)
        response = AgGrid(
            df_logs, gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True
        )
        st.markdown("---")
        goShort = setupSmallAGChart(df_errors)
        AgGrid(
            df_errors, gridOptions=goShort, custom_css=custom_css_prd, allow_unsafe_jscode=True, key = "workhorse_errors")

    else:
        filePathExists()


def filePathExists():
    st.markdown("#### Please provide a valid path to the logs directory")

def logFileNotFound(type_):
    st.markdown('<p class="font1"> \U0001F6A8 The {} log file was not found. Maybe the logs are not collected from {} node. </p>'.format(type_, type_), unsafe_allow_html=True)    

def showTabls(log_history, c2):
    colms = st.columns((0.5, 2, 2, 6,1))
    fields = ["#", 'Timestamp', 'Comment', 'Path']
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)
    st.markdown("---")
    for x, entry in enumerate(log_history):
        col1, col2, col3, col4, col5 = st.columns((0.5, 2, 2, 6,1))
        col1.write(x)  # index
        col2.write(entry['Timestamp'])  
        col3.write(entry['Comment']) 
        col4.write(entry['Path'])  
        if col5.button("Load", key=x):
            if validateFilepath(entry['Path'], c2):
                st.session_state.valid = True
                st.session_state.file_path = entry['Path']
                c2.success("Successfully loaded the logs", icon="✅")
                c2.markdown("---")
                c2.markdown(
                    ":arrow_backward: Select the page from the dropdown menu in the side bar "
                )
            else:
                c2.error("Something went wrong, please check file path", icon="🔥")


if __name__ == "__main__":
    main()
