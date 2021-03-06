# -*- coding: UTF-8 -*-
import numpy as np
from dnn import DNN
from prepare_data import PrepareData
from config import CorpusType, TrainMode
from re_cnn import RECNN


def evaluate_mlp():
  cws = DNN('mlp', mode=TrainMode.Sentence)
  model = 'tmp/mlp-model20.ckpt'
  # print(cws.seg('小明来自南京师范大学', model, debug=True))
  # print(cws.seg('小明是上海理工大学的学生', model))
  # print(cws.seg('迈向充满希望的新世纪', model))
  # print(cws.seg('我爱北京天安门', model))
  # print(cws.seg('在中国致公党第十一次全国代表大会隆重召开之际，中国共产党中央委员会谨向大会表示热烈的祝贺，向致公党的同志们',model))
  print(cws.seg('多饮多尿多食', model))
  print(cws.seg('无明显小便泡沫增多,伴有夜尿3次。', model))
  print(cws.seg('无明显小便泡沫增多,伴有夜尿3次。', model, ner=True))
  print(cws.seg('无明显双脚疼痛,无间歇性后跛行,无明显足部红肿破溃', model))
  # evaluate_model(cws, model)


def evaluate_mlp_ner():
  cws = DNN('mlp', mode=TrainMode.Sentence, is_seg=True, task='ner')
  model = 'tmp/mlp/mlp-ner-model1.ckpt'
  # print(cws.seg('在中国致公党第十一次全国代表大会隆重召开之际，中国共产党中央委员会谨向大会表示热烈的祝贺，向致公党的同志们', model,ner=True))
  print(cws.seg('多饮多尿多食', model, ner=True))
  print(cws.seg('无明显小便泡沫增多,伴有夜尿3次。', model, ner=True))
  print(cws.seg('无明显双脚疼痛,无间歇性后跛行,无明显足部红肿破溃', model, ner=True, debug=False))


def evaluate_lstm():
  cws = DNN('lstm', is_seg=True)
  model = 'tmp/lstm-model100.ckpt'
  print(cws.seg('小明来自南京师范大学', model, debug=True))
  print(cws.seg('小明是上海理工大学的学生', model))
  print(cws.seg('迈向充满希望的新世纪', model))
  print(cws.seg('我爱北京天安门', model))
  print(cws.seg('多饮多尿多食', model))
  print(cws.seg('无明显小便泡沫增多,伴有夜尿3次。无明显双脚疼痛,无间歇性后跛行,无明显足部红肿破溃', model))
  # evaluate_model(cws, model)


def evaludate_RECNN():
  reCNN = RECNN()
  reCNN.test()


def evaluate_model(cws, model):
  pre = PrepareData(4000, 'pku', dict_path='corpus/pku_dict.utf8', type=CorpusType.Test)
  sentences = pre.raw_lines
  labels = pre.labels_index
  corr_count = 0
  re_count = 0
  total_count = 0

  for _, (sentence, label) in enumerate(zip(sentences, labels)):
    _, tag = cws.seg(sentence, model)
    cor_count, prec_count, recall_count = estimate_cws(tag, np.array(label))
    corr_count += cor_count
    re_count += recall_count
    total_count += prec_count
  prec = corr_count / total_count
  recall = corr_count / re_count

  print(prec)
  print(recall)
  print(2 * prec * recall / (prec + recall))


def estimate_cws(current_labels, correct_labels):
  cor_dict = {}
  curt_dict = {}
  curt_start = 0
  cor_start = 0
  for label_index, (curt_label, cor_label) in enumerate(zip(current_labels, correct_labels)):
    if cor_label == 0:
      cor_dict[label_index] = label_index + 1
    elif cor_label == 1:
      cor_start = label_index
    elif cor_label == 3:
      cor_dict[cor_start] = label_index + 1

    if curt_label == 0:
      curt_dict[label_index] = label_index + 1
    elif curt_label == 1:
      curt_start = label_index
    elif curt_label == 3:
      curt_dict[curt_start] = label_index + 1

  cor_count = 0
  recall_length = len(curt_dict)
  prec_length = len(cor_dict)
  for curt_start in curt_dict.keys():
    if curt_start in cor_dict and curt_dict[curt_start] == cor_dict[curt_start]:
      cor_count += 1

  return cor_count, prec_length, recall_length


def estimate_ner(current_labels, correct_labels):
  corr_dict = {}
  curr_dict = {}
  corr_start = -2
  curr_start = -2

  # print('curr',current_labels)
  # print('corr', correct_labels)
  for label_index, (curr_label, corr_label) in enumerate(zip(current_labels, correct_labels)):
    if corr_label == 1:
      corr_start = label_index
      if corr_start == label_index - 1:
        corr_dict[corr_start] = 1
    elif label_index > 0 and corr_label == 2 and correct_labels[label_index - 1] != 2:
      corr_dict[corr_start] = label_index - corr_start

    if curr_label == 1:
      curr_start = label_index
      if curr_start == label_index - 1:
        curr_dict[curr_start] = 1
    elif label_index > 0 and curr_label == 2 and current_labels[label_index - 1] != 2:
      curr_dict[curr_start] = label_index - curr_start

  corr_count = 0
  prec_length = len(curr_dict)
  recall_length = len(corr_dict)
  for curr_start in curr_dict:
    if curr_start in corr_dict and curr_dict[curr_start] == corr_dict[curr_start]:
      corr_count += 1

  return corr_count, prec_length,recall_length

if __name__ == '__main__':
  # evaluate_mlp()
  evaluate_mlp_ner()
  # evaluate_lstm()
  # evaludate_RECNN()
