import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.io as pio

from collections import defaultdict

CHART_TITLE = '''Astoria Construction'''
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
COLORS = {
    'Design': '#4a90e2',        
    'Manufacturing': '#f39c12',
    'Construction': '#2ecc71',      
    'Habitation': '#e74c3c',   
    'Milestone': 'rgb(255, 140, 0)'  
} 
START_DATE = datetime(2074, 10, 12)


def parse_dependencies(dep_str):
    """Parse dependency list string into list of integers"""
    if dep_str.strip() == '[]':
        return []
    return [int(x.strip()) for x in dep_str.strip('[]').split(',') if x.strip()]

def parse_line(line):
    """Parse a single line of CSV, handling bracketed content properly"""
    start_idx = line.find('[')
    end_idx = line.find(']')
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"Invalid format - missing brackets: {line}")
    
    dependencies_str = line[start_idx:end_idx + 1]
    other_parts = (line[:start_idx] + line[end_idx + 1:]).strip()
    parts = [p.strip() for p in other_parts.split(',') if p.strip()]
    
    return parts, dependencies_str

def parse_gantt_csv(csv_content):
    tasks = {}
    milestones = {}
    
    for line in csv_content.splitlines():
        if not line.strip():
            continue
            
        parts, dependencies_str = parse_line(line)
        
        if len(parts) == 4: 
            task_id = int(parts[0])
            tasks[task_id] = {
                'name': parts[1],
                'duration': int(parts[2]),
                'dependencies': parse_dependencies(dependencies_str),
                'section': parts[3]
            }
        elif len(parts) == 2:  
            milestone_id = int(parts[0])
            milestones[milestone_id] = {
                'name': parts[1],
                'required_tasks': parse_dependencies(dependencies_str)
            }
        else:
            raise ValueError(f"Invalid line format: {line}")
            
    return tasks, milestones

def detect_cycles(graph):
    visited = set()
    path = set()
    
    def visit(vertex):
        if vertex in path:
            raise ValueError(f"Circular dependency detected at task {vertex}")
        if vertex in visited:
            return
            
        path.add(vertex)
        for dep in graph[vertex].get('dependencies', []):
            visit(dep)
        path.remove(vertex)
        visited.add(vertex)
    
    for vertex in graph:
        visit(vertex)

def calculate_task_dates(tasks, start_date):
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    for task_id, task in tasks.items():
        for dep in task['dependencies']:
            if dep not in tasks:
                raise ValueError(f"Task {task_id} depends on non-existent task {dep}")
            graph[dep].append(task_id)
            in_degree[task_id] += 1
    
    queue = [task_id for task_id in tasks if in_degree[task_id] == 0]
    if not queue:
        raise ValueError("No starting tasks found (possible circular dependency)")
    
    task_dates = {}
    
    while queue:
        current = queue.pop(0)
        
        if not tasks[current]['dependencies']:
            task_dates[current] = {
                'start': start_date,
                'finish': start_date + timedelta(days=tasks[current]['duration'])
            }
        else:
            max_end_date = max(task_dates[dep]['finish'] 
                             for dep in tasks[current]['dependencies'])
            task_dates[current] = {
                'start': max_end_date,
                'finish': max_end_date + timedelta(days=tasks[current]['duration'])
            }
        
        for dependent in graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    if len(task_dates) != len(tasks):
        raise ValueError("Not all tasks were processed (possible circular dependency)")
    
    return task_dates

def create_gantt_tasks(tasks, milestones, task_dates, start_date):
    result = []
    
    for task_id, task in tasks.items():
        dates = task_dates[task_id]
        result.append(dict(
            Task=task['name'],
            Start=dates['start'],
            Finish=dates['finish'],
            Resource=task['section']
        ))
    
    for milestone_id, milestone in milestones.items():
        if not milestone['required_tasks']:
            raise ValueError(f"Milestone {milestone_id} has no dependent tasks")
        milestone_date = max(task_dates[task_id]['finish'] 
                           for task_id in milestone['required_tasks'])
        result.append(dict(
            Task=f"★ {milestone['name']}",
            Start=milestone_date,
            Finish=milestone_date,
            Resource='Milestone'
        ))
    
    return result

def create_gantt_chart():
    colors = COLORS
    start_date = START_DATE
    csv_content = DATA
    tasks, milestones = parse_gantt_csv(csv_content)
    detect_cycles(tasks)
    task_dates = calculate_task_dates(tasks, start_date)
    final_tasks = create_gantt_tasks(tasks, milestones, task_dates, start_date)
    tasks = final_tasks
       
   
    tasks = sorted(tasks, key=lambda i: i['Start'])
    
    fig = ff.create_gantt(tasks,
                         colors=colors,
                         index_col='Resource',
                         show_colorbar=True,
                         group_tasks=True,
                         showgrid_x=True,
                         showgrid_y=False,
                         bar_width=0.45)
    
    unique_dates = sorted(list(set([task['Start'] for task in tasks] + [task['Finish'] for task in tasks])))

   
    fig.update_xaxes(
        ticktext=[date.strftime('%b %Y') for date in unique_dates],
        tickvals=unique_dates,
        tickangle=45,
        tickfont=dict(size=18),
        tickmode='array'
    )
    num_tasks = len(tasks)

    y_lines = [y - 0.5 for y in range(num_tasks + 1)]
    line_shapes = []
    for y_val in y_lines:
        line_shapes.append(
            # Add a line shape
            go.layout.Shape(
                type="line",
                xref="paper",  # 'paper' spans the entire plot width from 0 to 1
                x0=0,
                x1=1,
                yref="y",      # 'y' uses the data coordinates of the y-axis
                y0=y_val,
                y1=y_val,
                line=dict(
                    color="LightGrey",
                    width=1,
                )
            )
        )
    
    annotations = []
    for task in tasks:
        mid_date = task['Start']
        if task['Resource']=='Milestone':
            annotations.append(dict(x=mid_date,
                                 y=len(tasks)-1-tasks.index(task),
                                 text=task['Task'][0],
                                 showarrow=False,
                                 font=dict(color='rgb(255, 140, 0)', size=28),xanchor='left'),
                           )
            annotations.append(dict(x=mid_date,
                                 y=len(tasks)-1-tasks.index(task),
                                 text='     '+task['Task'][2:],
                                 showarrow=False,
                                 font=dict(color='rgb(255, 140, 0)', size=14),xanchor='left'),
                           )



    fig['layout']['annotations'] = annotations

    fig.update_layout(
        title=dict(
            text=CHART_TITLE,
            x=0.5,
            y=0.95,
            font=dict(size=24)
        ),
        xaxis_title='Timeline',
        height=800,
        font=dict(size=14),
        showlegend=True,
        bargap=0.2,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGrey'
        ),
        plot_bgcolor='#e3eeed',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        shapes=line_shapes
    )

    return fig


chart = create_gantt_chart()
chart.show()
pio.write_image(chart, 'gantt_chart.png', format='png', width=2800, height=2400, scale=2)
