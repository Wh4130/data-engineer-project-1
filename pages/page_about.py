# * ------------------------------------------------------------------------------
# ********************************************************************************
# *** --- by source analysis page ---

import streamlit as st
import pandas as pd
from utils.constants import media_sources
from ui_utils.data_manager import MongoDbManager
from ui_utils.wc_manager import WordCloudManager
import datetime as dt
st.title("About This APP")


from ui_utils.ui_manager import UIManager

UIManager.render_sidebar()


# * ------------------------------------------------------------------------------
# *** --- sidebar filter ---
mong = MongoDbManager()


