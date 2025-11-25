# nlp_test.py
import torch
import os

# 設置 PyTorch 使用單線程
torch.set_num_threads(1)
# 確保底層線程庫也被限制
os.environ["OMP_NUM_THREADS"] = "1" 

from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
# ... 繼續您的程式碼 ...
ws = WS("./data")
pos = POS("./data")
ner = NER("./data")

sentence_list = ["傅達仁今將執行安樂死，卻突然爆出自己20年前遭緯來體育台封殺，    他不懂自己哪裡得罪到電視台。",
                  "美國參議院針對今天總統布什所提名的勞工部長趙小蘭展開認可聽證會，預料她將會很順利通過參議院支持，成為該國有史以來第一 位的華裔女性內閣成員。"]

word_s = ws(sentence_list,
            sentence_segmentation=True,
            segment_delimiter_set={'?', '？', '!', '！', '。', ',',   
                                   '，', ';', ':', '、'})

word_p = pos(word_s)

word_n = NER(word_s, word_p)

print(word_n)