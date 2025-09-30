# Gantt Chart Generator

This tool generates a Plotly Gantt chart from a simple, CSV-like text format. It automatically resolves task dependencies using a Breadth-First Search (BFS) algorithm, starting each task as early as possible after all of its dependencies are completed. Both project tasks and key milestones are supported.

*Note: This tool was prototyped with the assistance of AI coding assistants for the UK Space Design Competition.*


### How to Use

**1. Prepare Your Data**

The script is configured using three main variables at the top of the file: `CHART_TITLE`, `DATA` and `START_DATE`.

- `CHART_TITLE`: A string for the chart's title.
- `DATA`: A multi-line string containing the task and milestone information.
- `START_DATE`: A datetime object containing the starting year, month and day in that order.

**Data Format**

The `DATA` variable uses a CSV-like format. There are two types of lines:

**Tasks:**
`id,task_name,length_in_days,[dependency_id_list],task_section`

**Milestones:**
`id,milestone_name,[task_ids_needed]`

**2. Example `DATA` Variable**

```python
DATA = '''1,initial design,150,[],Design
2,design finalisation,60,[1],Design
3,raw materials and machines collection,450,[1,2],Manufacturing
4,transhabs and robots manufactured,210,[1,2],Manufacturing
5,transhabs and robots shipped,420,[4],Manufacturing
6,construction of structural skeleton,360,[3,4,5],Construction
7,construction of core and CASSSC meshes,120,[3,4,5],Construction
8,construction of alpha ring,720,[3,5,6,7],Construction
9,construction of sigma ring,720,[1,2,3,4,5,6,7,8],Construction
10,sigma ring machine installation,540,[1,2,3,4,5,6,7,8,9],Construction
11,final safety checks,60,[1,2,3,4,5,6,7,8,9,10],Construction
12,temporary habitation,360,[1,2,3,4,5,6,7,8,9,10,11],Habitation
13,inset period,360,[1,2,3,4,5,6,7,8,9,10,11,12],Habitation
14,permanent habitation,420,[1,2,3,4,5,6,7,8,9,10,11,12,13],Habitation

1,beginning of assembly,[3]
2,alpha ring completed,[8]
3,IOC reached,[11]
4,permanent resident introduction,[13]'''

```
**3. Additional Customisation**

You can also change the categories of tasks and the colours used in the `colors` variable.

**4. Run the Script**

Execute the Python file. It will generate and open an HTML file containing the Gantt chart in your default web browser.
Ensure that you have plotly installed - it can be installed using `pip install plotly`.