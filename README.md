# SOSParser :sos:

**SOSParser** is a lightweight Python tool that parses the [GitLabSOS](https://gitlab.com/gitlab-com/support/toolbox/gitlabsos) logs and provides a graphical user interface to interact with them. We will see more details on this below in this page.

![sosparser_interface](static/interface.jpg)


## Prerequisites

- Python 3.7 or higher
- pip (or pip3)

## Installation steps

<details>
<summary>Steps to setup and run SOSParser</summary>

1. Clone the repository:

```bash
git clone git@gitlab.com:gitlab-com/support/toolbox/sosparser.git
cd sosparser
```

2. Install the dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If you have pip3 installed then you can use

```bash
pip3 install -r requirements.txt
```

Or if you want to use a [virtual environment](https://docs.python.org/3/library/venv.html), run the following commands instead:

```bash
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
</details>

---

## Steps to start the SOSParser

<details>
<summary>Steps to setup and run SOSParser</summary>

1. Add the following function to ~/.bashrc or ~/.zshrc file so that the log parser can be triggered from the command line directly:

 ```
sosparser() {
  local path="${1:-$(pwd)}"
  if [[ -z "$path" ]]; then
    path="$(pwd)"
  fi
  
  if [[ "$OSTYPE" == "darwin"* ]]; then
    /usr/bin/open "http://localhost:8501/?path=$path"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:8501/?path=$path"
  else
    echo "Unsupported OS"
  fi
}
 ```

2. Go to the SOSParser directory and run the following command. This should open a new tab in the browser at `http://localhost:8501`:

```bash
streamlit run app.py --browser.gatherUsageStats=false
```
3. Once the page is opened, copy the absolute path of the logs directory and paste it in the text box on the application UI, along with an optional comment, and then click on the Submit button.

4. We can also open the logs directly from the logs directory in the command line tool as follows:

```
# We can provide the absolute path to the sosparser command
> sosparser /Users/azzy/Downloads/gitlabsos.dv-git-_20230329105343 

# Or we can just execute sosparser; this will take the pwd value as input by default
> sosparser 
```
</details>

---

## How it work?

<details>
<summary>Expand</summary>

- GitLabSOS contains many files that hold valuable information. This tool extracts some metadata from each file and displays the information on the UI:

![sosparser_metadata](static/metadata.jpg)

- Other than the metadata, the tool converts the log file contents (GitLab, Production, API, etc.) into a Pandas DataFrame. We can perform a variety of arithmetic and logical operations on these DataFrames. For example, the application can generate the results of fast-stats, which is really helpful when troubleshooting an issue.

- In this tool, we also use the AgGrid (free version) tables and Streamlit libraries to provide a front end with dynamic tables that are searchable, sortable, paginated, and filterable in the UI.

![SOSParser](static/1.jpg "SOSParser")

</details>

---

## Working with tables/data

<details>
<summary>Expand</summary>

Here are the following things we can do with the tables to extract the data:

- *Filter the columns* : By default the table contains a lot of columns which we might not need. But we can select the columns which we are intersted in by clicking on the `Filter` button on the tables right side

![SOSParser](static/filter.jpg "SOSParser")
    
- *Sort columns* : We click on the name of the column to sort the column by either number or aplhabet

![SOSParser](static/filter.jpg "SOSParser")
    
- *Filter Rows* :We filter the rows of the table based on a value, for example, we can filter all the rows which have a perticular project name, user or correlation id. Infact, we can add multiple filters for the row, like user logs for a project xyz.

![SOSParser](static/filter.jpg "SOSParser")

- **

</details>

## Plotting graphs

- The tool provides an interactive graph to plot a table column's values over the time. The X-axis is the time and Y-axis is the value of the column, which can be changed in realtime by selecting a column from the dropdown.
- Each data point on the graph can be clicked to see the log data associated with it. Here's an example:

![SOSParser](static/2.png "SOSParser")

## Exporting Table Results 

You can export results from dataframes with right-click and select one of the `Export as ...` options. You can also export  
after you have filtered, sorted and modified columns on the output, so that only the selected data is generated in the export file.

![SOSParser](static/3-export-csv.png "SOSParser")

## Things to consider

- The tool expects the log files to be available in their default location inside the SOS logs directory. For example, the Sidekiq logs are located at `var/log/gitlab/sidekiq/current`. 
- If a column is missing in the log file, the tool will display that column's values as `0` in the table.
