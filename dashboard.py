# * ------------------------------------------------------------------------------
# ********************************************************************************
# *** --- by source analysis page ---

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from utils.constants import media_sources, color_mapping
from ui_utils.data_manager import MongoDbManager, MathTools
from ui_utils.wc_manager import WordCloudManager
from ui_utils.ui_manager import UIManager, P1_Keywords

import datetime as dt
from zoneinfo import ZoneInfo
st.title("Taiwan Media Dashboard")

# * ------------------------------------------------------------------------------
# *** --- page config ---
st.set_page_config(page_title = "Media Analytics Tool", 
                   page_icon = ":material/history_edu:", 
                   layout="wide", 
                   initial_sidebar_state = "auto", 
                   menu_items={
        'Get Help': None,
        'Report a bug': "mailto:huang0jin@gmail.com",
        'About': """
- Developed by - **[Wally, Huang Lin Chun](https://antique-turn-ad4.notion.site/Wally-Huang-Lin-Chun-182965318fa7804c86bdde557fa376f4)**"""
    })

# *** --- Load css style sheet ---
with open("style.css") as style_sheet:
            st.markdown(f"<style>{style_sheet.read()}</style>", unsafe_allow_html = True)

UIManager.render_sidebar()

# * ------------------------------------------------------------------------------
# *** --- session state init ---
with st.spinner("Initializing dashboard... (It takes about 30 seconds)"):

    if "dashboard" not in st.session_state:
        st.session_state["dashboard"] = {}

        # - default: past 7 day data
        st.session_state["dashboard"]["df_full"] = MongoDbManager.SELECT_ALL_BY_TIME([dt.datetime.now() - dt.timedelta(days = 7), dt.datetime.now()])

        # - default: past 7 day data
        st.session_state["dashboard"]["df_7day"] = st.session_state["dashboard"]["df_full"].copy()

        # - initializing filter toggles
        st.session_state['dashboard']['toggle_source'] = True
        st.session_state['dashboard']['toggle_type'] = True

        st.session_state['dashboard']['selected_types'] = []

# st.write(st.session_state["dashboard"]["df_full"])
# * ------------------------------------------------------------------------------
# *** --- sidebar filter ---
mong = MongoDbManager()

with st.sidebar:
    TAB1, TAB2, TAB3, TAB4 = st.tabs(["Source", "Filters", "Setting", "Download"])
    BOX1 = TAB1.container(border = True)
    BOX2 = TAB2.container(border = True)
    BOX3 = TAB3.container(border = True)
    BOX4 = TAB4.container(border = True)



    

# * source data interval filter
with BOX1:

    st.write("#### :material/database: Source Data")
    date_col, time_col = st.columns(2)

    with date_col:
        day1 = st.date_input("start date", value = dt.date.today() - dt.timedelta(days = 7))
        day2 = st.date_input("end date", value = dt.date.today())
    with time_col:
        time1 = st.time_input("start time")
        time2 = st.time_input("end time")

    dt1 = dt.datetime.combine(day1, time1).replace(tzinfo = ZoneInfo("Asia/Taipei"))
    dt2 = dt.datetime.combine(day2, time2).replace(tzinfo = ZoneInfo("Asia/Taipei"))


    # * apply change on time interval
    on_click = st.button("Apply change", width = 'stretch', type = 'primary',
                        help = "Clicking this button will update the dashboard based on the selected time interval.")
        
# * source filter
with BOX2:
    st.write("#### :material/filter_alt: Filters")

    # * filter selections
    # -- select source
    input_sources = st.pills("#### Source Filter", 
                                options = [values["MandName"] for values in media_sources.values()], default = [values["MandName"] for values in media_sources.values()],
                                selection_mode = 'multi')
    
    # -- select article type

    all_items = st.session_state["dashboard"]["df_full"]['type'].unique().tolist()

    items = st.session_state.get("selected_types", [])
    all_selected = set(items) == set(all_items)
    toggle_label = "Deselect All" if all_selected and all_items else "Select All"
    items_with_toggle = all_items + [toggle_label] if all_items else []

    def handle_selection():
        selected = st.session_state.get("selected_types", [])
        if toggle_label in selected:
            st.session_state["selected_types"] = [] if all_selected else all_items.copy()
        else:
            st.session_state["selected_types"] = [x for x in selected if x != toggle_label]

    input_types = st.pills(
        "Select Items:",
        options = items_with_toggle,
        default = all_items,
        selection_mode = "multi",
        key = "selected_types",
        on_change = handle_selection,
    )






# * ------------------------------------------------------------------------------
# *** --- "Apply change" button
if on_click:
    # * clear cache to avoid stale data
    st.cache_data.clear()

    # - at least two hours
    cond = dt2 - dt1 >= dt.timedelta(days = 2)

    if not cond:
        st.error("Please select a time interval of at least **two days**.")
        st.stop()

    # * update session state full dashboard data
    st.session_state['dashboard']['df_full'] = MongoDbManager.SELECT_ALL_BY_TIME([dt1, dt2])



# * ------------------------------------------------------------------------------
# *** --- slice the source data by filter set by the user
# """sliced_data: for dashboard block other than keyword trend"""
# """sliced_data_kwt: for dashboard block 'keyword trend' (first block)"""
sliced_data = st.session_state['dashboard']['df_full'][
    (st.session_state['dashboard']['df_full']['source'].isin(input_sources))
]
sliced_data_kwt = st.session_state['dashboard']['df_7day'][
    (st.session_state['dashboard']['df_7day']['source'].isin(input_sources))
]

sliced_data = sliced_data[
    (sliced_data['type'].isin(input_types))
]
sliced_data_kwt = sliced_data_kwt[
    (sliced_data_kwt['type'].isin(input_types))
]

if sliced_data.empty or sliced_data_kwt.empty:
    st.error("No data available! Loose your filter to get more data.")
    st.stop()


# ---
# F2 - pie chart
# F3 - type & source
# F4 - time & source
# F5 - length dist.
# F6 - wc bar
# * setting
source_prop_data = sliced_data.groupby("source").agg(count = ("title", "count"))

with BOX3:
    st.write("#### :material/settings: Setting")

    with st.container(border = False, height = 400):

        graph_params = {f"F{i}": {} for i in range(1, 7)}
        st.write("##### Article Source & Type Dist.")
        graph_params['F2']["source"] = st.pills("Source", 
                                                source_prop_data.index,
                                                default = source_prop_data.index[0])

        st.write("##### Article Count by Type / Source")
        graph_params["F3"]["labels_on"] = st.pills("Labels", [True, False], 
                                                   default = True, 
                                                   format_func = lambda x: "On" if x else "Off")
        graph_params["F3"]["bar_mode"] = st.pills("Bar mode", ["stack", "group"], 
                                                  default = "stack")

        st.write("##### Article Count by Time / Source")
        graph_params["F4"]["bin_size"] = st.slider("Bin size (hour)", min_value = 1, max_value = 24, value = 2)

# * download
with BOX4:
    st.write("#### :material/download: Download")
    st.download_button(
        "Source data",
        st.session_state["dashboard"]["df_full"].to_csv().encode("utf-8"),
        width = "stretch",
        file_name = "source_data.csv",
        mime = "text/csv",
        icon = ":material/download:",
    )
    st.download_button(
        "Filtered data",
        sliced_data.to_csv().encode("utf-8"),
        width = "stretch",
        file_name = "filtered_data.csv",
        mime = "text/csv",
        icon = ":material/download:",
    )
    

# * ------------------------------------------------------------------------------
# *** --- dashboard ---
# *** ------------------------------------------
    # * --- basic statistics
with st.container():
    st.markdown("##### Basic Statistics")
    
    cols_r1 = st.columns(3)

    with cols_r1[0].container(border = True, height = 165):
        st.markdown("###### **:gray[Time Interval]**", help = "Time interval covered by the source news data")
        # st.write(f":material/event_upcoming: :blue[**{dt1.strftime('%Y-%m-%d %H:%M')}**] (start)<br><br>:material/calendar_check: :blue[**{dt2.strftime('%Y-%m-%d %H:%M')}**] (end)", unsafe_allow_html = True)
        st.markdown(f"""
    <div class="data-pair-container">
        <div class="data-block">
            <span class="data-label">from</span>
            <span class="data-number date">{dt1.strftime('%y/%m/%d')}</span>
            <span class="data-label time">{dt1.strftime('%H:%M')}</span>
        </div>
        <div class="data-block">
            <span class="data-label">to</span>
            <span class="data-number date">{dt2.strftime('%y/%m/%d')}</span>
            <span class="data-label time">{dt2.strftime('%H:%M')}</span>
        </div>
    </div>""", unsafe_allow_html = True)


    with cols_r1[1].container(border = True, height = 165):
        st.markdown("###### **:gray[Article Count]**", help = "The number of articles in the filtered news data.")
        
        st.markdown(f"""
    <div class="data-pair-container">
        <div class="data-block">
            <span class="data-label">filtered</span>
            <span class="data-number filtered">{sliced_data.shape[0]:,.0f}</span>
        </div>
        <div class="data-block">
            <span class="data-label">source</span>
            <span class="data-number source">{st.session_state['dashboard']['df_full'].shape[0]:,.0f}</span>
        </div>
    </div>""", unsafe_allow_html = True)


    with cols_r1[2].container(border = True, height = 165):
        st.markdown("###### **:gray[Top 10 Hot Keywords]**", help = "Top 10 keywords that are mentioned in the filtered news the most frequently.")
        
        st.markdown(" ".join(
            [ f":blue-badge[{ele}]" for ele in 
                P1_Keywords.get_top_k_tags(sliced_data, 10)
            ]
            ))
    # *** ------------------------------------------
    # * --- article keyword dashboard

with st.container():
    st.markdown("##### Overall Keyword Trend - Top 3 Article Keywords in the past 7 days", help = """① Source LTN（自由時報）has no attribute 'keywords', so keywords statistics are relevant to other sources only. 
                 
② Keyword statistics are calculated tracing back to past 7 days, no matter how you select your raw data.
""")

    cols_r2 = st.columns(3)

# st.session_state['dashboard']['df_7day']
    for i, tag in zip([0, 1, 2], P1_Keywords.get_top_k_tags(sliced_data_kwt, 3)):
        with cols_r2[i]:
            tag_series = P1_Keywords.get_kw_count_ts(sliced_data_kwt, tag)
            P1_Keywords.plot_single_kw_count(tag, tag_series)

with st.container():
    st.markdown("##### Top 100 Article Keywords in the past 7 days")
    tags = list(P1_Keywords.kw_trans_func(sliced_data_kwt['keywords']).keys())[:100]
    tag_df = pd.DataFrame(columns = ["tag", "ts"])
    for tag in tags:
        tag_df.loc[len(tag_df), ["tag", "ts"]] = [tag, P1_Keywords.get_kw_count_ts(sliced_data_kwt, tag)]
    tag_df['total'] = tag_df.apply(lambda row: int(sum(row['ts'])), axis = 1)

    tag_df = tag_df.sort_values("total", ascending = False)

    st.data_editor(
        tag_df,
        row_height = 50,
        height = 300,
        disabled = True,
        hide_index = True,
        column_config = {
            "tag": st.column_config.TextColumn(
                "Keyword Tag",
                width = "small"
            ),
            "ts": st.column_config.BarChartColumn(
                "Trend Time Series",
                color = "auto-inverse",
                help = "daily time series of # articles that mentioned the keyword"
            ),
            "total": st.column_config.ProgressColumn(
                "Total Mentioned Count",
                format = "compact",
                max_value = 200
            )
        }
    )




    
        
    # *** ------------------------------------------
    # * --- article type distribution
st.markdown("##### Article Source and Type Distribution")
with st.container(border = True):

    cols_r3 = st.columns(2)
    
    with cols_r3[0]:
        # ** article source pie chart

        fig_donut = go.Figure(data = [
            go.Pie(labels = source_prop_data.index, 
                   values = source_prop_data['count'], 
                   hole = .4,
                   pull = [0.1 if source == graph_params['F2']["source"] else 0 for source in source_prop_data.index ])
        ])
        fig_donut.update_layout(margin = dict(
                                    t = 70, 
                                    b = 20, 
                                    l = 10, 
                                    r = 0), 
                                height = 400,
                                legend = dict(
                                    yanchor = "top",
                                    y = 0.65,
                                    xanchor = "left",
                                    x = 1
                                ),
                                title = "Article Source Distribution")
        fig_donut.update_traces(marker = dict(
                                    colors = [color_mapping[src] for src in source_prop_data.index]))
        st.plotly_chart(fig_donut)

    with cols_r3[1]:

        # ** article type dist. by source
        source_type_sub_df = sliced_data[sliced_data['source'] == graph_params['F2']["source"]]
        type_prop_data = source_type_sub_df.groupby("type").agg(count = ("title", "count"))
        fig_donut_2 = go.Figure(data = [
            go.Pie(labels = type_prop_data.index, values = type_prop_data['count'], hole=.5)
        ])
        fig_donut_2.update_layout(margin = dict(
                                    t = 70, 
                                    b = 70, 
                                    l = 10, 
                                    r = 0), 
                                  height = 400,
                                  legend = dict(
                                    yanchor = "top",
                                    y = 1,
                                    xanchor = "left",
                                    x = 1
                                  ),
                                  title = f"Article Type Distribution: {graph_params['F2']["source"]}") 
        fig_donut_2.update_traces(marker = dict (colors = [color_mapping[src] for src in source_prop_data.index]))
        st.plotly_chart(fig_donut_2)


    
# *** ------------------------------------------
# * --- pivot table for article count

st.markdown("##### Article Count by Type / Source")
with st.container(border = True):

    pv_count = (sliced_data
                .pivot_table(index = 'type', 
                             columns = 'source', 
                             aggfunc = 'count', 
                             fill_value = 0,
                             values = 'title')
                )
    pv_count['total'] = pv_count.sum(axis = 1)
    pv_count.reset_index(inplace = True)

    fig_count = go.Figure(
        data = [
            go.Bar(name = col, 
                   x = pv_count['type'], 
                   y = pv_count[col], 
                   text = pv_count[col] if graph_params["F3"]["labels_on"] else None,
                   marker = dict(color = color_mapping[col]))
            for col in pv_count.columns if col not in ['type', 'total']
        ]
    )
    fig_count.update_layout(barmode = graph_params["F3"]["bar_mode"], 
                            margin = dict(
                                t = 0, b = 0, l = 0, r = 0
                                ),
                            legend = dict(
                                    yanchor = "top",
                                    y = 0.6,
                                    xanchor = "left",
                                    x = 1
                                )
                            )
    

    st.plotly_chart(fig_count)

# *** ------------------------------------------
# * --- time series histogram for article count

st.markdown("##### Article Count by Time / Source")
with st.container(border = True):


    fig_ts = px.histogram(sliced_data, 
                          x = "updated_time",
                          text_auto = False,
                          color = "source",
                          color_discrete_map = color_mapping)
    fig_ts.update_layout(bargap = 0.2, 
                         margin = dict(
                                t = 0, b = 0, l = 0, r = 0
                                ),
                         legend = dict(
                                yanchor = "top",
                                y = 0.8,
                                xanchor = "left",
                                x = 1
                            ))
    fig_ts.update_traces(xbins_size = graph_params["F4"]["bin_size"] * 3600000)
    st.plotly_chart(fig_ts)



# *** ------------------------------------------
# * --- distribution of article length

st.markdown("##### Article Length Distribution")
with st.container(border = True):
    
    gb_lenBySource = {
        source: MathTools.remove_outliers(
            sliced_data[sliced_data['source'] == source]['len']
            ) for source in input_sources
    }
    fig_len = ff.create_distplot(
        hist_data = [gb_lenBySource[source] for source in gb_lenBySource],
        group_labels = list(gb_lenBySource.keys()),
        bin_size = 50,
        show_rug = True,
        show_hist = False,
        colors = [color_mapping[src] for src in gb_lenBySource]
    ).update_layout(
        margin = dict(
            t = 0, b = 0, l = 0, r = 0
            ),
        legend = dict(
            yanchor = "top",
            y = 0.8,
            xanchor = "left",
            x = 1
        ))

    # fig_avg_len = go.Figure(
    #     data = [
    #         go.Bar(name = col, x = pv_avglen['type'], y = pv_avglen[col])
    #         for col in pv_avglen.columns if col not in ['type']
    #     ]
    # )
    # fig_avg_len.update_layout(barmode = 'group', title = 'Article Count by Type and Source')

    st.plotly_chart(fig_len)





with st.container(border = True):
    st.write("###### WordCloud (Manual generation required!)")

    # - initializing wordcloud plot
    if "wc_data" not in st.session_state["dashboard"]:
        btn_str = "Generate"
    else:
        btn_str = "Regenerate"

    generate_btn = st.button(btn_str, width = 'stretch', type = "primary", key = "gen_wc")
    if generate_btn:
        st.session_state["dashboard"]["wc_data"] = WordCloudManager.worcdloud_generate(sliced_data, width = 800, height = 1500)

        cl, cr = st.columns(2)
        with cl:
            wordcloud = st.pyplot(st.session_state["dashboard"]["wc_data"][1])
        with cr:
            data = pd.DataFrame(st.session_state["dashboard"]["wc_data"][0].items(),
                                columns = ["word", "count"]).sort_values("count")
            fig_wcount = go.Figure(go.Bar(
                x=data['count'],
                y=data['word'],
                orientation='h'))
            fig_wcount.update_layout(
                height = 700
            )
            st.plotly_chart(fig_wcount)




# TODO * 4. 情感分析引擎？ textblob