from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import datetime
import dateutil.relativedelta
import plotly
from plotly.tools import FigureFactory as FF
import plotly.graph_objs as go
import time


def data_analysis(data, user):
    time_now = time.time()
    length = len(data)
    data_not_completed = []
    for i in range(length):
        if data[i]['completed'] == -1 and data[i]['deadline'] <= time_now:
            data_not_completed.append(data[i])

    data_not_completed_sorted = sorted(data_not_completed, key=lambda student: student['priority'], reverse=True)

    # print(data_not_completed_sorted)

    length_sorted = len(data_not_completed_sorted)
    data_matrix = [[0 for x in range(3)] for y in range(length_sorted + 1)]
    # print(data_matrix)

    data_matrix[0][0] = 'Priority'
    data_matrix[0][1] = 'Task Name'
    data_matrix[0][2] = 'Delay'

    reliability = 0
    for i in range(length):
        if data[i]['completed'] == -1 and data[i]['deadline'] <= time_now:
            dt1 = datetime.datetime.fromtimestamp(time_now)
            dt2 = datetime.datetime.fromtimestamp(data[i]['deadline'])
            rd = dateutil.relativedelta.relativedelta(dt1, dt2)

            reliability += float(data[i]['priority']+rd.days)/ 10 ** 4
        elif data[i]['completed'] != -1 and data[i]['deadline'] <= time_now:
            dt1 = datetime.datetime.fromtimestamp(time_now)
            dt2 = datetime.datetime.fromtimestamp(data[i]['deadline'])
            rd = dateutil.relativedelta.relativedelta(dt1, dt2)

            reliability += float(data[i]['priority']*rd.days)/ 10 ** 4
    for i in range(length_sorted):
        dt1 = datetime.datetime.fromtimestamp(time_now)
        dt2 = datetime.datetime.fromtimestamp(data_not_completed_sorted[i]['deadline'])
        rd = dateutil.relativedelta.relativedelta(dt1, dt2)
        data_not_completed_sorted[i]['completed'] = {'Years': rd.years, 'Months': rd.months, 'Days': rd.days,
                                                     'Hours': rd.hours, 'Minutes': rd.minutes, 'Seconds': rd.seconds}
    for i in range(length_sorted):
        dt1 = datetime.datetime.fromtimestamp(time_now)
        dt2 = datetime.datetime.fromtimestamp(data_not_completed_sorted[i]['deadline'])
        rd = dateutil.relativedelta.relativedelta(dt1, dt2)
        data_not_completed_sorted[i]['completed'] = {'Days': rd.days, 'Hours': rd.hours}
    for i in range(1, length_sorted + 1):
        data_matrix[i][0] = data_not_completed_sorted[i - 1]['priority']
        data_matrix[i][1] = data_not_completed_sorted[i - 1]['task_name']
        data_matrix[i][2] = data_not_completed_sorted[i - 1]['completed']
    figure = FF.create_table(data_matrix, height_constant=100)

    # begining the pi chart
    dwd = 0
    dad = 0
    nud = 0
    nad = 0
    length = len(data)

    for i in range(length):
        if data[i]['completed'] <= data[i]['deadline'] and data[i]['completed'] != -1:
            dwd += 1
        elif data[i]['completed'] > data[i]['deadline'] and data[i]['completed'] != -1:
            dad += 1
        elif data[i]['completed'] == -1 and data[i]['deadline'] >= time_now:
            nud += 1
        elif data[i]['completed'] == -1 and data[i]['deadline'] < time_now:
            nad += 1

    Pie = {
        'labels': ['Done before deadline', 'Done after deadline', 'Not done but under deadline',
                   'Not done even after deadline'],
        'values': [dwd, dad, nud, nad],
        'type': 'pie',
        'domain': {'x': [0, 1],
                   'y': [.4, 1]},
        'hoverinfo': 'label+percent+name',
        'textinfo': 'none'}

    figure['data'].extend(go.Data([Pie]))
    figure.layout.yaxis.update({'domain': [0, .30]})
    figure.layout.margin.update({'t': 75, 'l': 170})
    figure.layout.update({'title': '%s\'s Performance Report[Reliability :- %s ]' % (user, (1 - reliability))})
    figure.layout.update({'font': {'size': 16, 'family': 'Courier New, monospace', 'color': '#7f7f7f'}})
    figure.layout.update({'height': 950})

    return plot(figure)
