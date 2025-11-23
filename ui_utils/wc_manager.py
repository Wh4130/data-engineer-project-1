import streamlit as st
import pandas as pd
import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np 
from PIL import Image
import random
import re
from collections import Counter

from utils.constants import DICTIONARY_PATH, STOPWORDS_PATH, FONT_PATH

class WordCloudManager:

    @staticmethod
    def worcdloud_generate(data, width = 400, height = 600):

        with st.spinner("generating wordcloud..."):

            x, y = np.ogrid[:300, :300]
            mask = (x - 150)**2 + (y - 150)**2 > 150**2
            mask = 255 * mask.astype(int)

            mask = np.array(Image.open("./assets/filter.png"))
            '''
            text should be separated by comma
            '''
            text = ' '.join(data.loc[:, 'content'].astype(str)).replace(' ', ', ')

            jieba.set_dictionary(DICTIONARY_PATH)
            jieba.analyse.set_stop_words(STOPWORDS_PATH)

            tags = jieba.analyse.extract_tags(text, topK = 50)
            seg_list = jieba.lcut(text, cut_all = False)
            dictionary = Counter(seg_list)

            freq = {}
            for ele in dictionary:
                if ele in tags:
                    if not re.match(r"\d+", ele):
                        freq[ele] = dictionary[ele]

            # Create and generate a word cloud image:
            wordcloud = WordCloud(
                background_color=None,  # No background color
                mode='RGBA',             # Enable transparency
                font_path=FONT_PATH,
                random_state = 1214,
                width = width,
                height = height,
                mask = mask
            ).generate_from_frequencies(freq)


            fig, ax = plt.subplots(1, 1)
            ax.imshow(wordcloud, interpolation = 'bilinear')
            ax.axis('off')
            fig.patch.set_alpha(0)

            return freq, fig
        
    