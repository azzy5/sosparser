import plotly_express as px
import streamlit as st
import plotly.io as pio
pio.templates.default = "plotly_dark"

color_sequence=[
    "#0068c9",
    "#83c9ff",
    "#ff2b2b",
    "#ffabab",
    "#29b09d",
    "#7defa1",
    "#ff8700",
    "#ffd16a",
    "#6d3fc0",
    "#d5dae5",
]

def interactiveGraph(df , x_lable='time', title= "Graph"):
    y_lable = st.selectbox("Select y-axis for graph", df.columns)
    fig = px.scatter (df, x="time", y=y_lable, title=title, color=y_lable, color_discrete_sequence = color_sequence, hover_data=['correlation_id']) 
    return fig

def matrixGraphPD(df, x_lable='time', title= "Production Matrix Graph"):
    fig = px.ecdf(df,y="time", x=["status"])
    return fig
