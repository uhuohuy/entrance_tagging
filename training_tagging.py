

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 09:32:04 2019

@author: hu_xk
"""

from __future__ import division
import numpy as np
from smote import SMOTEBoost
import pandas as pd
from pandas import DataFrame, read_csv,read_excel
from collections import Counter
from imblearn.ensemble import BalancedRandomForestClassifier
from imblearn.ensemble import RUSBoostClassifier
from imblearn.ensemble import BalancedBaggingClassifier # doctest: +NORMALIZE_WHITESPACE
from imblearn.ensemble import EasyEnsembleClassifier
from sklearn.ensemble import RandomForestClassifier
import statsmodels.api as sm
import matplotlib.pyplot as plt
from openpyxl import load_workbook

def get_distance(dis_array,start_index,end_index):
    if start_index> end_index:
         a = start_index;
         start_index = end_index;
         end_index = a;            
    if start_index == end_index:
        return 0;
    temp_dis1 = sum(dis_array[start_index:end_index]);
    temp_dis2 = sum(dis_array[end_index:len(dis_array)])+sum(dis_array[0:start_index]);
    return min(temp_dis1,temp_dis2);

def distance_error(dis_array, entrance_index, probs):
    dis_error = 0;
    bb = probs.tolist()
    index = bb.index(max(bb))
    dis_error = get_distance(dis_array,int(entrance_index),index);
    bb.sort(reverse = True)
    estimated_rank = bb.index(probs[int(entrance_index)])
    return dis_error,index,estimated_rank

if __name__ == "__main__":
     path = '.\\tagging_result.xlsx'
     book = load_workbook(path)
     writer = pd.ExcelWriter(path, engine='openpyxl')
     writer.book = book
     estimated_sample_index = []
     c_x = []
     c_y = []
     truth_index = []
     len_samples = [];
     big_error_count = 0;
     estimated_rank = []
     wrf_clf = RandomForestClassifier(n_estimators=80, max_depth=12, random_state=0, class_weight={0:1,1:160});
     rf_clf = RandomForestClassifier(n_estimators=100, max_depth=14, random_state=0);
     brf_clf = BalancedRandomForestClassifier(n_estimators=100, max_depth=14, random_state=0)
     smote = SMOTEBoost(n_samples=130,k_neighbors=4, n_estimators=90)
     models =[wrf_clf,brf_clf,rf_clf,smote]
     for fm in range(2):
         saved_data  = []
         total_errors = []
         for group in range(1,6):
            test_head_file = '.\\Data\\'+str(group)+'\\test_rf_head.xls'
            test_file_base ='.\\Data\\'+str(group)+'\\'
            train_file =  '.\\Data\\'+str(group)+'\\features.csv'
            raw_data = pd.read_excel(test_head_file,header=None).values
            test_list = raw_data[0];
            test_truth = raw_data[1];
            test_candidate_len = raw_data[2];
            test_entrances_xs = raw_data[3];
            test_entrances_ys = raw_data[4];
            test_dis_array = [];
            test_num = len(test_list);
            sum_error = 0;
            target_name = 'class';
            T = pd.read_csv(train_file);
            head = list(T.columns)
            head.remove(target_name)
            Training_X = T[head].to_numpy()
            Training_Y = T[target_name].to_numpy()
            trained_models = []
            if fm in range(3):
                models[fm].fit(Training_X, Training_Y)
            else:
                models[fm].fit(Training_X,Training_Y,sample_weight=None, minority_target=1)
            sheet_names = ['wrf','brf','rf','smote']
            for i in range(test_num):
                dis_array= raw_data[5:5+int(test_candidate_len[i]),i];
                test_file = test_file_base+str(int(test_list[i]))+'rftest.csv';
                test_table = pd.read_csv(test_file);
                test_X = test_table[head].to_numpy();
                prob = models[fm].predict_proba(test_X)
                cur_dis_error, estimated_index,rank = distance_error(dis_array, test_truth[i], prob[:,1])
                temp_vec = []
                temp_vec.append(estimated_index);
                temp_vec.append(test_truth[i]);
                temp_vec.append(test_entrances_xs[i]);
                temp_vec.append(test_entrances_ys[i]);
                temp_vec.append(len(dis_array));
                temp_vec.append(cur_dis_error)
                temp_vec.append(rank+1)
                temp_vec.append(float(rank+1)/len(dis_array))
                saved_data.append(temp_vec)
                total_errors.append(cur_dis_error);
         m_acc = np.average(total_errors)
         print (len(total_errors))
         print('total_error for'+ sheet_names[fm]+': '+str(m_acc))
         df = pd.DataFrame(saved_data)
         df.to_excel(writer,sheet_name=sheet_names[fm])
     writer.save()
     writer.close()