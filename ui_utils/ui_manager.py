import streamlit as st
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
            st.page_link("dashboard.py", label = 'Introduction & Demos', icon = ":material/info:")
            st.page_link("./pages/page_bysource.py", label = '媒體分析儀表版', icon = ":material/folder_open:")
            st.page_link("./pages/page_raw.py", label = '新聞資料下載', icon = ":material/folder_open:")
                