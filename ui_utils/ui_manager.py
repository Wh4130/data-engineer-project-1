import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import networkx as nx
from ui_utils.data_manager import DataTools


class UIManager:
        
    @staticmethod
    def render_sidebar():
        with st.sidebar:
            
            # * Title
            
            st.write(" ")
            st.header("Taiwanese Media Dashboard")
            # st.caption(f"**Literature Review Tool**")

            # * Pages
            st.page_link("dashboard.py", label = 'Dashboard', icon = ":material/widgets:")
            st.page_link("./pages/page_query.py", label = 'News Querying Tool', icon = ":material/feature_search:")

                
class P1_Keywords:

    @staticmethod
    def kw_trans_func(keywords):

        return pd.Series([kw for kw_ls in keywords if isinstance(kw_ls, list) for kw in kw_ls ]).value_counts().to_dict()
    
    @staticmethod
    def get_top_k_tags(data, k):
        kws = P1_Keywords.kw_trans_func(data['keywords'])

        if k == -1:
            return list(kws.keys())
        else:
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


class P_network_graph:

    @staticmethod
    def create_graph(data):
        G = nx.Graph()
        kws = P1_Keywords.kw_trans_func(data['keywords'])
        kws = [(k, {"count": v}) for k, v in kws.items()]
        G.add_nodes_from(kws)

        for left in G.nodes:
            for right in G.nodes:
                weight = 0
                if left != right:
                    for _, row in data.iterrows():
                        if isinstance(row['keywords'], list):
                            if left in row['keywords'] and right in row['keywords']:
                                weight = 1
                                break
                    if weight == 1:
                        G.add_edge(left, right, weight = weight)

        pos = nx.spring_layout(G)
        nx.set_node_attributes(G, pos, 'pos')
        return kws, G

    @staticmethod
    def plot(kws, G: nx.Graph) -> go.Figure:

        kws = [{elm[0]: elm[1]['count']} for elm in kws]
        """
        將 NetworkX 圖轉換為 Plotly 圖形，使用 G.degree() 進行高效的連線數計算。
        
        Args:
            G: 帶有 'pos' 屬性 (來自 nx.spring_layout 等) 的 NetworkX 圖。
            
        Returns:
            go.Figure: Plotly 圖形物件。
        """
        
        # --- 1. 邊緣追蹤：保持不變，因為 Plotly 要求此結構 ---
        edge_x = []
        edge_y = []
        # 使用 G.edges(data=False) 確保只獲取 (u, v) 元組
        for u, v in G.edges():
            # 假設 G.nodes[n]['pos'] 已經存在
            x0, y0 = G.nodes[u]['pos']
            x1, y1 = G.nodes[v]['pos']
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Edges'
        )
        
        # --- 2. 節點數據收集：合併迴圈並使用 G.degree() ---
        
        # 2.1. 高效計算所有節點的 Degree
        # G.degree() 返回 (node_name, degree_count) 的迭代器
        # 將其轉換為字典，以便 O(1) 查找
        degree_dict = dict(G.degree()) 

        node_x = []
        node_y = []
        node_adjacencies = []
        node_size = []
        node_text = []

        # 使用 G.nodes(data=False) 迭代節點名稱
        for node in G.nodes():
            # 獲取位置 (必須存在)
            x, y = G.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)
            
            # 獲取連線數 (從 Degree 字典中獲取)
            num_connections = degree_dict.get(node, 0)
            node_adjacencies.append(num_connections)

            # 獲取節點 tag 的文章提及數
            mentioned = G.nodes[node]["count"]
            
            # 創建懸停文本
            node_text.append(f"{node}, # of connections: {num_connections}, # of mentioning articles: {mentioned}")

        # --- 3. 節點追蹤：使用收集的數據 ---
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,  # 使用優化後的懸停文本
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=node_adjacencies, # 顏色直接使用連線數列表
                size=10, # 如果需要根據 Degree 調整大小，這裡可以修改
                colorbar=dict(
                    thickness=15,
                    title=dict(
                    text='Node Connections',
                    side='right'
                    ),
                    xanchor='left',
                ),
                line_width=2
            ),
            name='Nodes'
        )
        
        # --- 4. 圖形組裝 ---
        
        fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b = 20,l = 5,r = 5,t = 40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

        return fig