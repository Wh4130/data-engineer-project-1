# * ------------------------------------------------------------------------------
# ********************************************************************************
# *** --- by source analysis page ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from utils.constants import media_sources, color_mapping
from ui_utils.data_manager import MongoDbManager
from ui_utils.wc_manager import WordCloudManager
from ui_utils.ui_manager import P1_Keywords, P_network_graph
import datetime as dt
from zoneinfo import ZoneInfo
st.title("Taiwan News Query Tool")


from ui_utils.ui_manager import UIManager

UIManager.render_sidebar()

# *** --- Load css style sheet ---
with open("style.css") as style_sheet:
            st.markdown(f"<style>{style_sheet.read()}</style>", unsafe_allow_html = True)


# * ------------------------------------------------------------------------------
# *** --- sidebar filter ---
with st.container(border = True, key = "filter"):

    st.write("#### :material/document_search: Search News")
    cl, cr = st.columns(2)

    with cl:
        day1 = st.date_input("start date", value = dt.date.today() - dt.timedelta(days = 7))
        day2 = st.date_input("end date", value = dt.date.today())
        keywords = st.text_input("keywords to query", help = "input the keywords you want to query and separate them by a comma **:blue[',']** .")
    with cr:
        time1 = st.time_input("start time")
        time2 = st.time_input("end time")
        source = st.pills("source", media_sources.keys(), default = media_sources.keys(), format_func = lambda key: media_sources[key]["MandName"], selection_mode = "multi")



    dt1 = dt.datetime.combine(day1, time1).replace(tzinfo = ZoneInfo("Asia/Taipei"))
    dt2 = dt.datetime.combine(day2, time2).replace(tzinfo = ZoneInfo("Asia/Taipei"))
    query = st.button("Query", width = 'stretch', type = 'primary')
        
if query:
    # * query
    df_ls = []
    with st.spinner("Querying...", show_time = True):
        for src in source:
            df = MongoDbManager.SELECT_BY_QUERY(
                src,
                [dt1, dt2],
                keywords
            )
            df['source'] = media_sources[src]['MandName']
            df_ls.append(df)
        df_final = pd.concat(df_ls)

    cols = st.columns(3)

    # * count
    with cols[0].container(height = 200):
        st.markdown("###### **:gray[Article Count]**", help = "Time interval covered by the source news data")
        st.markdown(f"""
        <div class="centering-container">
            <div class="data-pair-container">
                <div class="data-block">
                    <span class="data-label">Found</span>
                    <span class="data-number found">{df_final.shape[0]:,.0f}</span>
                </div>
            </div>
        </div>""", unsafe_allow_html = True)
    
    # * source dist.
    with cols[1].container(height = 200):
        st.markdown("###### **:gray[Sources]**")
        source_val_count = df_final.groupby("source").agg(count = ("title", len))
        fig_donut = go.Figure(data = [
            go.Pie(labels = source_val_count.index, 
                   values = source_val_count['count'], 
                   hole = .4)
        ])
        fig_donut.update_layout(margin = dict(
                                    t = 0, 
                                    b = 20, 
                                    l = 0, 
                                    r = 0), 
                                height = 150,
                                legend = dict(
                                    yanchor = "top",
                                    y = 0.7,
                                    xanchor = "left",
                                    x = 1.
                                ))
        fig_donut.update_traces(marker = dict(
                                    colors = [color_mapping[src] for src in source_val_count.index]))
        st.plotly_chart(fig_donut)

    # * tags
    with cols[2].container(height = 200):
        st.markdown("###### **:gray[Top Keyword Tags]**")
        st.markdown(" ".join(
            [ f":blue-badge[{ele}]" for ele in 
                P1_Keywords.get_top_k_tags(df_final, 10)
            ]
            ))

    st.dataframe(
            df_final,
            column_config = {
                "_id": None,
                "title": st.column_config.TextColumn(
                    "Title",
                    width = "large"
                ),
                "url": st.column_config.LinkColumn(
                    "Link",
                    width = "small",
                    display_text=":material/link:"
                ),
                "type": st.column_config.TextColumn(
                    "Category",
                    width = "small"
                ),
                "updated_time": st.column_config.DatetimeColumn(
                    "Updated Time",
                    width = "medium",
                    format = "D MMM YYYY, h:mm a"
                ),
                "content": st.column_config.TextColumn(
                    "Content",
                    width = "small"
                ),
                "len": st.column_config.ProgressColumn(
                    "Content Length",
                    width = "medium",
                    max_value = 3000,
                    format = "compact"
                ),
            }
        )
         
    # with TABS[1].container(border = True):
    #     with st.spinner("Calculating tag network...", show_time = True):
    #         kws, G = P_network_graph.create_graph(df_final)
    #         nx_fig = P_network_graph.plot(kws, G)
    #         st.plotly_chart(nx_fig)
# 
