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


UIManager.render_sidebar()

# * ------------------------------------------------------------------------------
# *** --- session state init ---
with st.spinner("Initializing dashboard..."):
    if "mongo" not in st.session_state:
        st.session_state["mongo"] = MongoDbManager()

    if "dashboard" not in st.session_state:
        st.session_state["dashboard"] = {}

        # - default: past 7 day data
        st.session_state["dashboard"]["df_full"] = st.session_state["mongo"].SELECT_ALL_BY_TIME([dt.datetime.now() - dt.timedelta(days = 7), dt.datetime.now()])

        # - initializing wordcloud plot
        st.session_state["dashboard"]["wc_data"] = WordCloudManager.worcdloud_generate(st.session_state["dashboard"]["df_full"])

        # - initializing filter toggles
        st.session_state['dashboard']['toggle_source'] = True
        st.session_state['dashboard']['toggle_type'] = True

        st.session_state['dashboard']['selected_types'] = []

# st.write(st.session_state["dashboard"]["df_full"])
# * ------------------------------------------------------------------------------
# *** --- sidebar filter ---
mong = MongoDbManager()

with st.sidebar:
    TAB1, TAB2 = st.tabs(["Source Data", "Filters"])
    BOX1 = TAB1.container(border = True)
    BOX2 = TAB2.container(border = True)

    

# * source data interval filter
with BOX1:

    st.write("#### Source Data")
    date_col, time_col = st.columns(2)

    with date_col:
        day1 = st.date_input("start date", value = dt.date.today() - dt.timedelta(days = 7))
        day2 = st.date_input("end date", value = dt.date.today())
    with time_col:
        time1 = st.time_input("start time")
        time2 = st.time_input("end time")

    dt1 = dt.datetime.combine(day1, time1).replace(tzinfo = None)
    dt2 = dt.datetime.combine(day2, time2).replace(tzinfo = None)

    st.caption(f"FROM: :blue[**{dt1.strftime('%Y-%m-%d %H:%M')}**]\n\nTO: :blue[**{dt2.strftime('%Y-%m-%d %H:%M')}**]")

    # * apply change on time interval
    on_click = st.button("Apply change", width = 'stretch', type = 'primary',
                        help = "Clicking this button will update the dashboard based on the selected time interval.")
        
# * source filter
with BOX2:
    st.write("#### Filters")

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
        options=items_with_toggle,
        default=all_items,
        selection_mode="multi",
        key="selected_types",
        on_change=handle_selection,
    )


# * ------------------------------------------------------------------------------
# *** --- "Apply change" button
if on_click:
    # * clear cache to avoid stale data
    st.cache_data.clear()

    # - at least two hours
    cond = dt2 - dt1 >= dt.timedelta(hours = 2)

    if not cond:
        st.error("Please select a time interval of at least **two days**.")
        st.stop()

    # * update session state full dashboard data
    st.session_state['dashboard']['df_full'] = st.session_state['mongo'].SELECT_ALL_BY_TIME([dt1, dt2])



# * ------------------------------------------------------------------------------
# *** --- slice the source data by filter set by the user
sliced_data = st.session_state['dashboard']['df_full'][
    (st.session_state['dashboard']['df_full']['source'].isin(input_sources))
]

sliced_data = sliced_data[
    (sliced_data['type'].isin(input_types))
]

if sliced_data.empty:
    st.error("No data available! Loose your filter to get more data.")
    st.stop()

# * ------------------------------------------------------------------------------
# *** --- dashboard ---
st.header("ss", help = 'ww')
cols = st.columns(3)
for i, tag in zip([0, 1, 2], P1_Keywords.get_top_3_tags(st.session_state['dashboard']['df_full'])):
    with cols[i].container(border = True):
        tag_series = P1_Keywords.get_kw_count_ts(st.session_state['dashboard']['df_full'], tag)
        P1_Keywords.plot_single_kw_count(tag, tag_series)

with st.container(border = True):
    
    # *** ------------------------------------------
    # * --- pivot table for article count
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
                   text = pv_count[col],
                   marker = dict(color = color_mapping[col]))
            for col in pv_count.columns if col not in ['type', 'total']
        ]
    )
    fig_count.update_layout(barmode = 'stack', 
                            title = 'Article Count by Type and Source'
                            )
    

    st.plotly_chart(fig_count)

with st.container(border = True):
    
    # *** ------------------------------------------
    # * --- distribution of article length
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
    ).update_layout(title = "Article Length Distribution by Source")

    # fig_avg_len = go.Figure(
    #     data = [
    #         go.Bar(name = col, x = pv_avglen['type'], y = pv_avglen[col])
    #         for col in pv_avglen.columns if col not in ['type']
    #     ]
    # )
    # fig_avg_len.update_layout(barmode = 'group', title = 'Article Count by Type and Source')

    st.plotly_chart(fig_len)

with st.container(border = True):
    st.write("###### Article Count by Time and Source")

    
    # *** ------------------------------------------
    # * --- time series histogram for article count
    fig_ts = px.histogram(sliced_data, 
                          x = "updated_time",
                          text_auto = False,
                          color = "source")
    fig_ts.update_layout(bargap = 0.2)
    fig_ts.update_traces(xbins_size=7200000) # TODO
    st.plotly_chart(fig_ts)



with st.container(border = True):
    st.write("###### WordCloud (Manual generation required!)")
    if st.button("Regenerate", width = 'stretch', type = "primary"):
        with st.spinner("Generating wordcloud..."):
            st.session_state["dashboard"]["wc_data"] = WordCloudManager.worcdloud_generate(sliced_data, width = 800, height = 1500)
        st.rerun()

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

