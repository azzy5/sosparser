# SOSParser :sos:

**SOSParser** makes dealing with logs collected from GitLabSOS a bit easier. Right now, it works with Production, Sidekiq and Gitaly log files. In addition, it can also provide a quick summary of information collected from various files in the GitLabSOS logs such as `cpuinfo`, `df_hT`, `gitlab_migrations`, `gitlab_status` and so on.


The tool is built using Python streamlit and pandas libraries, SOSParser turns log files into interactive tables where we can easily sort and filter columns. This helps us narrow down logs quickly. Once we filter the logs as per the requirements, we can export them as CSV files, with plans to add JSON export later on.


## Prerequisites

- Python 3.7 or higher
- pip (or pip3)

## Installation

1. Clone the repository:

```bash
git clone gitlab-gold/azhar/support-projects/traceparser_sos.git
cd traceparser_sos
```

2. Install the dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If you have pip3 installed then you can use

```bash
pip3 install -r requirements.txt
```

If you want to use a [virtual environment](https://docs.python.org/3/library/venv.html), run the following commands instead:


```bash
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Running the Tool

To run the tool, execute the following command:

```bash
streamlit run app.py
```

After running the command, a new browser window should open automatically. If it doesn't, you can access the tool by navigating to the following URL in your browser:

```
http://localhost:8501
```

Once the page is ready copy the absolute path of the logs directory and paste it in the text box on the application UI 

Example path for log directory:

```
/Users/azzy/Downloads/gitlabsos.dv-git-_20230329105343
```

Then click on _Submit_ button and the application should validate the files that it is going to process further. If all the files exist, then then the logs can seen in thier respective UIs

## How does this work?

For each type of log, the tool looks for the file thier respective log directory and with bit of processing it converts the file contents into a [Padas Dataframe](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) which is 2D data structure ideal for storing data for rows and columns. 

Once we have the Dataframe ready, we can perform lot of aithmentic and logical operations on the data as per requirement. For example, the application does all the calculations and produces output of fast-stat application with few lines of code for each log file.

Also, we can simply output the dataframe content as a table on the webpage. However, when we combine  this with the libraries like [AgGrid](https://www.ag-grid.com/javascript-data-grid/getting-started/) (free version) and [Streamlit](https://streamlit.io/) we can easily render a table which very interactive and provides lot of out of the features such as fitltering, sorting, pagination etc. 

![SOSParser](static/1.jpg "SOSParser")

## Things to consider

- The tool expects the log files to be available in thier default location inside SOS logs directory. For example, the Sidekiq logs are located at `var/log/gitlab/sidekiq/current`. 
- If there's any column missing in the log file, the tool will add `0` to that column values and proceeds with the calculations
