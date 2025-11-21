# * ------------------------------------------------------------------------------
# ********************************************************************************
# *** --- by source analysis page ---

import streamlit as st
import pandas as pd
from utils.constants import media_sources
from ui_utils.data_manager import MongoDbManager
from ui_utils.wc_manager import WordCloudManager
import datetime as dt
st.title("Taiwan Media Dashboard")


from ui_utils.ui_manager import UIManager

UIManager.render_sidebar()


# * ------------------------------------------------------------------------------
# *** --- sidebar filter ---
mong = MongoDbManager()


with st.sidebar.container(border = True):
    st.write("#### Select Source Data Interval")

    selected = st.selectbox("collection", list(media_sources.keys()), format_func = lambda x: media_sources[x]['MandName'])

    date_col, time_col = st.columns(2)

    with date_col:
        day1 = st.date_input("start date")
        day2 = st.date_input("end date")
    with time_col:
        time1 = st.time_input("start time")
        time2 = st.time_input("end time")

    dt1 = dt.datetime.combine(day1, time1).replace(tzinfo = None)
    dt2 = dt.datetime.combine(day2, time2).replace(tzinfo = None)

    st.caption(f"FROM: :blue[**{dt1.strftime('%Y-%m-%d %H:%M')}**]\n\nTO: :blue[**{dt2.strftime('%Y-%m-%d %H:%M')}**]")

    on_click = st.button("Apply change", width = 'stretch', type = 'primary')

if on_click:
    

    cond = dt2 - dt1 >= dt.timedelta(hours = 2)

    if not cond:
        st.error("Please select a time interval of at least **two hours**.")
        st.stop()

    res = mong.SELECT_BY_TIME(
        collection_name = selected,
        time_interval = [dt1, dt2]
    )
    with st.container():
        wc_left = WordCloudManager.worcdloud_generate(res)[1]
        st.pyplot(wc_left)

