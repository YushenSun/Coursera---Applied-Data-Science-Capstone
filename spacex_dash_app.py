# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# 读取 SpaceX 数据并导入 pandas 数据框架
# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# 获取最大和最小有效载荷（单位：kg）
# Get the maximum and minimum payload (kg)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# 创建 Dash 应用程序
# Create a dash application
app = dash.Dash(__name__)

# 创建应用程序布局
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: 添加下拉列表以选择发射场
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                             ],
                                             value='ALL',  # 默认值为“ALL”，显示所有发射场
                                             placeholder="Select a Launch Site here",  # 提示用户选择发射场
                                             searchable=True  # 允许搜索发射场
                                             ),
                                html.Br(),

                                # TASK 2: 显示发射成功数量的饼图
                                # TASK 2: Pie chart for launch success count
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: 添加滑动条以选择有效载荷范围
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 10000)},
                                    value=[min_payload, max_payload]  # 默认值为整个有效载荷范围
                                ),
                                html.Br(),

                                # TASK 4: 显示有效载荷和发射成功率之间关系的散点图
                                # TASK 4: Scatter chart for correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                            ])

# TASK 2 Callback: Pie chart for Success vs. Failure
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If 'ALL' sites are selected, use all rows in the dataframe
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, 
                     values='class',  # 'class' column indicates success (1) or failure (0)
                     names='Launch Site',  # Names of the launch sites for the pie chart
                     title='Total Launch Success Count')  # Pie chart title
    else:
        # If a specific site is selected, filter the dataframe to include only the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count successes (class=1) and failures (class=0) for the selected site
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        
        # Create pie chart for the selected site
        fig = px.pie(values=[success_count, failure_count], 
                     names=['Success', 'Failure'], 
                     title=f'Success vs Failure for {entered_site}')
    
    return fig



# TASK 4 Callback: 根据选择的发射场和有效载荷范围筛选数据并绘制散点图
# TASK 4 Callback: Scatter chart for Payload vs. Launch Success
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # 根据选择的有效载荷范围筛选数据
    # Filter the dataframe based on the payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                             (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if entered_site != 'ALL':
        # 如果选择的是特定发射场，则进一步筛选该场的数据
        # If a specific site is selected, filter by the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # 绘制有效载荷与发射成功率之间的散点图
    # Create the scatter plot of Payload Mass vs. Success
    fig = px.scatter(filtered_df, 
                     x='Payload Mass (kg)',  # X轴为有效载荷（kg）
                     y='class',  # Y轴为发射成功（1）或失败（0）
                     color='class',  # 按成功与失败的颜色区分
                     title=f'Payload Mass vs. Launch Success for {entered_site}' if entered_site != 'ALL' else 'Payload Mass vs. Launch Success',
                     labels={'class': 'Launch Success (1=Success, 0=Failure)', 'Payload Mass (kg)': 'Payload Mass (kg)'},
                     color_continuous_scale='Viridis')  # 使用Viridis颜色映射
    return fig

# 运行应用
# Run the app
if __name__ == '__main__':
    app.run_server()
