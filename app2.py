import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import json
from datetime import datetime


app = dash.Dash()

server = app.server

def datasetUpdate(filename, datasetlabel):
    '''
    Reads data into pandas dataframe,
    then adds an extra column for the
    label of the set of data.

    Also converts the entries in column 2
    into datetime objects.
    '''

    df = pd.read_csv(filename)
    df['test_label'] = datasetlabel

    df['Column 2'] = pd.to_datetime(df['Column 2'],format= '%a %m/%d/%y %I:%M:%S.%f %p')

    df = df.iloc[::3] #take only a third of the dataframe

    return df


df_0529test1 = datasetUpdate('0529test1.csv', 1)
df_0529test3 = datasetUpdate('0529test3.csv', 2)
df_0530test4 = datasetUpdate('0530test4.csv', 3)

df = pd.concat([df_0529test1, df_0529test3, df_0530test4])

# text on the dashboard

text_1 = '''
#### My thoughts on the original data:
- There is an Outlier at the beginning of Phase 0 for each test.
- In comparison to all other phases, Phase 0 lasts a short time.
  This makes me assume that Phase 0 is just a baseline, and testing
  begins during Phase 1.
'''

text_2 = '''
#### Action taken:
- Phase 0 was removed from the training data set.
'''

text_3 = '''
#### Features with most similar trends:
- Columns 11 & 12 (target)
- Columns 4 & 5
- Columns 6 & 7

#### Effect of feature outliers on target (Column 12):
- Outliers in Phase 1 of training set 3 for
  Columns 4, 5 influence target.
- Outliers in Phase 1 of training set 1 for
  Column 1 don't influence target.
'''


# test phases before and after outlier removal

original_phases = [0, 1, 2, 3, 4]
after_removal = [1, 2, 3, 4]
colormap = {0: 'blue', 1: 'orange', 2: 'green', 3: 'red', 4: 'purple'}


# features that will explored on the dashboard

features = ['Column 1', 'Column 4', 'Column 5', 'Column 6', 'Column 7',
            'Column 8', 'Column 9', 'Column 10', 'Column 11', 'Column 12']

# dashboard Layout

app.layout = html.Div([
                      html.Div([
                                html.H2('Target Outlier Detection and Removal',
                                        style = {'text-align': 'center'}),

                                html.Div([
                                         html.H4('Make a Selection:',
                                                 style = {'display': 'inline-block'}),

                                         dcc.RadioItems(id = 'outlier-removal',
                                                        options = [{'label': 'Original Data',
                                                                    'value': original_phases},
                                                                    {'label': 'After Outlier Removal',
                                                                    'value': after_removal}],
                                                                 value = original_phases,
                                                                 labelStyle = {'display': 'block'},
                                                                 style = {'display': 'inline-block',
                                                                          'vertical-align': 'bottom'})
                                        ]),

                                dcc.Graph(id = 'target-plot',
                                          figure = {'data': [go.Scattergl(x=df[df['Column 3']==phase]['Column 2'],
                                                                        y=df[df['Column 3']==phase]['Column 12'],
                                                                        mode = 'markers',
                                                                        marker = dict(size = 3,
                                                                                      color = colormap[phase]),
                                                                        name=phase) for phase in original_phases],
                                                    'layout': go.Layout(title='Transient Output during each Test Phase',
                                                                        xaxis = dict(title = 'Column 2'),
                                                                        yaxis = dict(title = 'Column 12'),
                                                                        hovermode='closest')
                                                   }),

                               dcc.Markdown(id = 'outlier-explanation',
                                            children = text_1)


                                ]),



                                html.Div([html.H2('Feature Exploration',
                                          style = {'text-align': 'center'})],
                                          style = {'paddingTop': '80px'}),

                                html.H5('*Hover over datapoints within any phase on the left figure to closely examine the corresponding phase on both right figures'),


                                html.Div([
                                        html.Div([
                                                 dcc.Dropdown(id = 'left-dropdown',
                                                              options = [{'label' : i, 'value': i} for i in features],
                                                              value = 'Column 4')
                                                ], style = {'width': '30%',
                                                            'display': 'inline-block'}),
                                        html.Div([
                                                 dcc.Dropdown(id = 'right-dropdown',
                                                              options = [{'label' : i, 'value': i} for i in features],
                                                              value = 'Column 12')
                                                ], style = {'width': '70%',
                                                            'display': 'inline-block'})
                                       ]),

                                html.Div([
                                       html.Div([html.H5('*Select Training Set:'),

                                                 html.Div([dcc.Slider(id = 'choose-test',
                                                                      min = 1,
                                                                      max = 3,
                                                                      step = 1,
                                                                      marks = {str(i):str(i) for i in range(1,4)},
                                                                      value = 2),
                                                          ],
                                                           style = {'fontSize': 36,
                                                                    'font-weight': 'bold',
                                                                    'paddingRight': '10px',
                                                                    'paddingBottom': '20px'}),

                                                 dcc.Graph(id = 'view-specific-test',
                                                           figure = {'data': [go.Scattergl(x=df[(df['Column 3']==phase) & (df['test_label']==2)]['Column 2'],
                                                                                         y=df[(df['Column 3']==phase) & (df['test_label']==2)]['Column 4'],
                                                                                         mode = 'markers',
                                                                                         marker = dict(size = 3,
                                                                                                       color = colormap[phase]),
                                                                                         name=phase) for phase in after_removal],
                                                                     'layout': go.Layout(title='Training Set 2',
                                                                                         yaxis = dict(title = 'Column 4'),
                                                                                         showlegend = False,
                                                                                         margin = {'r':0},
                                                                                         hovermode ='closest')},
                                                           clear_on_unhover = True
                                                            ),

                                                 html.P(dcc.Markdown(id = 'exploration',
                                                              children = text_3))

                                                ],
                                                 style = {'width': '30%',
                                                          'float': 'left'}),

                                       html.Div([
                                                dcc.Graph(id = 'top-figure',
                                                          figure = {'data': [go.Scattergl(x = df[df['Column 3']==phase]['Column 2'],
                                                                                        y = df[df['Column 3']==phase]['Column 4'],
                                                                                        mode = 'markers',
                                                                                        marker = dict(size = 3,
                                                                                                      color = colormap[phase]),
                                                                                        name = phase) for phase in after_removal],
                                                                     'layout': go.Layout(title = 'Compare trends across phases of Column 4 & Column 12',
                                                                                         yaxis = dict(title = 'Column 4'),
                                                                                         showlegend = False,
                                                                                         margin = {'r': 0,
                                                                                                   'b': 0},
                                                                                         hovermode ='closest')},
                                                          clear_on_unhover = True
                                                                   ),


                                                 dcc.Graph(id = 'bottom-figure',
                                                           figure = {'data': [go.Scattergl(x=df[df['Column 3']==phase]['Column 2'],
                                                                                         y=df[df['Column 3']==phase]['Column 12'],
                                                                                         mode = 'markers',
                                                                                         marker = dict(size = 3,
                                                                                                       color = colormap[phase]),
                                                                                         name=phase) for phase in after_removal],
                                                                     'layout': go.Layout(yaxis = dict(title = 'Column 12'),
                                                                                         showlegend = False,
                                                                                         margin = {'r': 0,
                                                                                                   't': 0},
                                                                                         hovermode ='closest')},
                                                           clear_on_unhover = True
                                                           )

                                                ],
                                                 style = {'width': '70%',
                                                          'float': 'right'})


                                        ])



])


@app.callback(Output('target-plot', 'figure'),
              [Input('outlier-removal', 'value')])
def updateOutlierGraph(phases):
    '''
    Takes in user dashboard input to update the
    phases of tests that were plotted.
    '''
    figure = {'data': [go.Scattergl(x = df[df['Column 3']==phase]['Column 2'],
                                  y = df[df['Column 3']==phase]['Column 12'],
                                  mode = 'markers',
                                  marker = dict(size = 3,
                                  color = colormap[phase]),
                                  name = phase) for phase in phases],
             'layout': go.Layout(title='Transient Output during each Test Phase',
                                 xaxis = dict(title = 'Column 2'),
                                 yaxis = dict(title = 'Column 12'),
                                 hovermode ='closest')}
    return figure


@app.callback(Output('outlier-explanation', 'children'),
              [Input('outlier-removal', 'value')])

def updateOutlierMarkdown(phases):
    '''
    Edits my explanation of the Outlier Figure
    based on user dashboard input.
    '''
    if phases == after_removal:
        return text_2
    else:
        return text_1


@app.callback(Output('view-specific-test', 'figure'),
              [Input('left-dropdown', 'value'),
               Input('choose-test', 'value')])
def updateTestingSetFig(feature, test):
    '''
    Takes in user dashboard input to update the
    Training Set Figure.
    '''
    figure = {'data': [go.Scattergl(x = df[(df['Column 3']==phase) & (df['test_label']==test)]['Column 2'],
                                  y = df[(df['Column 3']==phase) & (df['test_label']==test)][feature],
                                  mode = 'markers',
                                  marker = dict(size = 3,
                                  color = colormap[phase]),
                                  name=phase) for phase in after_removal],
             'layout': go.Layout(title='Training Set '+ str(test),
                                 yaxis = dict(title = feature),
                                 showlegend = False,
                                 margin = {'r':0},
                                 hovermode ='closest')}
    return figure


@app.callback(Output('top-figure', 'figure'),
              [Input('view-specific-test', 'hoverData'),
               Input ('left-dropdown', 'value'),
               Input ('right-dropdown', 'value')])

def updateTopFigure2(hoverData, yaxistitle, title):
    '''
    Updates top trend-comparison-figure
    based on user dashboard inputs
    '''

    if json.dumps(hoverData) == 'null':
        figure = {'data': [go.Scattergl(x = df[df['Column 3']==phase]['Column 2'],
                                      y = df[df['Column 3']==phase][yaxistitle],
                                      mode = 'markers',
                                      marker = dict(size = 3,
                                      color = colormap[phase]),
                                      name = phase) for phase in after_removal],
                 'layout': go.Layout(title='Compare trends across phases of ' + yaxistitle + ' & ' + title,
                                     yaxis = dict(title = yaxistitle),
                                     showlegend = False,
                                     margin = {'r':0,
                                               'b': 0},
                                     hovermode ='closest')}

    else:
        data_time = hoverData['points'][0]['x']
        data_time = datetime.strptime(data_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%a %m/%d/%y %I:%M:%S.%f %p')
        phase = int(df[df['Column 2']==data_time]['Column 3'].unique())


        figure = {'data': [go.Scattergl(x = df[df['Column 3']==phase]['Column 2'],
                                      y = df[df['Column 3']==phase][yaxistitle],
                                      mode = 'markers',
                                      marker = dict(size = 3,
                                      color = colormap[phase]),
                                      name = phase)],
                 'layout': go.Layout(title='Compare trends across phases of ' + yaxistitle + ' & ' + title,
                                     yaxis = dict(title = yaxistitle),
                                     showlegend = False,
                                     margin = {'r':0,
                                               'b': 0},
                                     hovermode ='closest')}


    return figure

@app.callback(Output('bottom-figure', 'figure'),
              [Input('view-specific-test', 'hoverData'),
               Input('right-dropdown', 'value')])

def updateBottomFigure2(hoverData, yaxis):
    '''
    Updates bottom trend-comparison-figure
    based on user dashboard inputs
    '''

    if json.dumps(hoverData) == 'null':
        figure = {'data': [go.Scattergl(x = df[df['Column 3']==phase]['Column 2'],
                                      y = df[df['Column 3']==phase][yaxis],
                                      mode = 'markers',
                                      marker = dict(size = 3,
                                      color = colormap[phase]),
                                      name = phase) for phase in after_removal],
                 'layout': go.Layout(yaxis = dict(title = yaxis),
                                     showlegend = False,
                                     margin = {'r':0,
                                               't': 0},
                                     hovermode ='closest')}


    else:
        data_time = hoverData['points'][0]['x']
        data_time = datetime.strptime(data_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%a %m/%d/%y %I:%M:%S.%f %p')
        phase = int(df[df['Column 2']==data_time]['Column 3'].unique())


        figure = {'data': [go.Scattergl(x = df[df['Column 3']==phase]['Column 2'],
                                      y = df[df['Column 3']==phase][yaxis],
                                      mode = 'markers',
                                      marker = dict(size = 3,
                                      color = colormap[phase]),
                                      name = phase)],
                 'layout': go.Layout(yaxis = dict(title = yaxis),
                                     showlegend = False,
                                     margin = {'r':0,
                                               't': 0},
                                     hovermode ='closest')}


    return figure


if __name__ == '__main__':
    app.run_server()
