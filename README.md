# SOSParser :sos:

**SOSParser** makes dealing with logs collected from GitLabSOS a bit easier. Right now, it works with Production_json.log and Sidekiq current files, but it'll probably handle more file types later on. In addition, it can also provide a quick summary of information collected from various files in the GitLabSOS logs such as `cpuinfo`, `df_hT`, `gitlab_migrations`, `gitlab_status` and so on.



The tool is built using Python streamlit and pandas libraries, SOSParser turns log files into interactive tables where we can easily sort and filter columns. This helps us narrow down logs quickly. Once we filter the logs as per the requirements, we can export them as CSV files, with plans to add JSON export later on.


## Prerequisites

- Python 3.7 or higher
- pip (Python Package Installer)

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

## Running the Tool

To run the tool, execute the following command:

```bash
streamlit run app.py
```

After running the command, a new browser window should open automatically. If it doesn't, you can access the tool by navigating to the following URL in your browser:

```
http://localhost:8501
```

## Usage

- There are two ways to use the tool:
    1. ### Using web interface:
        1. Start the application from a terminal and let it run the background by using the command `streamlit run app.py`. 
        1. - Visit _http://localhost:8501_ and paste the folder path in the text box in the UI (absolute path to the logs root directory)
        1. location  in the webpage rendered by the application and then click on _Submit_
    
    2. ### Using command line interface:
        1. Set an alias in the `~/.bashrc` or `~/.zshrc` file as  `alias sosparser='streamlit run /path/to/your/app.py -- '`
        1. To start the app, pass the absolute path for log directory in the command line as follow : `sosparser /path/to/logs/root/folder`
        1. The new window should open in the browser and the logs should be ready to review. 


- If everything is okay you can find the logs details as follow:
    - **Metadata** : This page shows metadata extracted from varirous files , such as 'top', 'df_hT' etc. It
    it basically provides a quick overview of the system status.
    - **Sidekiq** : This UI intented for Sidelkiq logs. It has multiple tables to filter, sort and     export data. Currently the tool only reads the _current_ file from the `/var/log/gitlab/sidekiq/current` directory.
    - **Production** : Same thing as Sidekiq but for Production logs 
