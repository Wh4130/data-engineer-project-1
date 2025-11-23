import streamlit as st
import pandas as pd
from ui_utils.data_manager import DataTools


class UIManager:
        
    @staticmethod
    def render_sidebar():
        with st.sidebar:
            
            # * Icon & Title
            text_box, icon_box = st.columns((0.8, 0.2))
            with icon_box:
                st.markdown(f'''
                                <img class="image" src="data:image/jpeg;base64,{DataTools.image_to_b64(f"./assets/icon.png")}" alt="III Icon" style="width:500px;">
                            ''', unsafe_allow_html = True)
            with text_box:
                st.write(" ")
                st.header("Taiwanese Media Dashboard")
                st.caption(f"**Literature Review Tool**")

            # * Pages
            st.page_link("./pages/page_about.py", label = 'About this app', icon = ":material/help:")
            st.page_link("dashboard.py", label = 'Dashboard', icon = ":material/widgets:")
            st.page_link("./pages/page_query.py", label = 'News Querying Tool', icon = ":material/feature_search:")

                
class P1_Keywords:

    @staticmethod
    def kw_trans_func(keywords):

        return pd.Series([kw for kw_ls in keywords if isinstance(kw_ls, list) for kw in kw_ls ]).value_counts().to_dict()
    
    @staticmethod
    def get_top_k_tags(data, k):
        kws = P1_Keywords.kw_trans_func(data['keywords'])
        return list(kws.keys())[:k]


    @staticmethod
    def get_kw_count_ts(data, tag):

        data['date'] = data['updated_time'].dt.date
        date_keyword_count = (data
                                .groupby(
                                    by = "date"
                                )
                                .agg(
                                    keywords = ('keywords', P1_Keywords.kw_trans_func)
                                )
                                .sort_index(ascending = True)
                                .iloc[-8: -1]
                            )

        tag_series = [pairs.get(tag, 0) for pairs in date_keyword_count['keywords']]
        return tag_series
    
    @staticmethod
    def plot_single_kw_count(tag, tag_series):
        
        st.metric(f"#:blue[**{tag}**]", 
                  tag_series[-1], 
                  delta = tag_series[-1] - tag_series[-2], 
                  chart_data = tag_series,
                  border = True)

