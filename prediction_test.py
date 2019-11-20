

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 09:32:04 2019

@author: hu_xk
"""

from __future__ import division
#import csv
#import xlwt
#import xlrd
#import random
#import os
#import copy;
import numpy as np
from smote import SMOTEBoost
# from impyute.imputation.cs import fast_knn
# from impyute.imputation.cs import mice
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
def cdf_plot(data, name, number):
    """
    data: 一组数据
    name: 在legend上显示的名称
    number: 数据最大最小值之间划分多少段
    """
    ecdf = sm.distributions.ECDF(data)
    x = np.linspace(min(data), max(data), number)
    y = ecdf(x)
    plt.xlabel('distance error (m)')
    plt.ylabel('accuracy')
    plt.grid()
    plt.xticks(np.arange(min(data), max(data)+1, 20))
    #plt.step(x, y, label=name)
    plt.plot(x, y, label=name,linewidth=4)

contexts =['service_way_dis','landmark_dis','post_dis','main_p_dis','park_dis','ped_dis','addr_sort','axis_sort','rail_dis']
category = ['opp_shape','shape','bool_arc','bool_v_addr', 'bool_post','bool_addr_acc','face_own', 'bool_visual_mr','bool_landmark'\
,'opp_hole', 'bool_visual_se','bool_v_addr', 'bool_post', 'main_access', 'bool_addr_acc','bool_visual_mr', 'bool_landmark','bool_visual_se'] 
context_num = [0]*len(contexts)
original_features = ['addr_sort','main_access','bool_visual_se','ped_dis','park_dis','landmark_dis']
new_exist_feat_names = ['addr_exist','main_exist','service_exist','pedestrain_exist','bike_exist','landmark_exist']
class Prediction:       
    def get_distance(self, dis_array,start_index,end_index):
        if start_index> end_index:
             a = start_index;
             start_index = end_index;
             end_index = a;            
        if start_index == end_index:
            return 0;
        temp_dis1 = sum(dis_array[start_index:end_index]);
        temp_dis2 = sum(dis_array[end_index:len(dis_array)])+sum(dis_array[0:start_index]);
        return min(temp_dis1,temp_dis2);
    
    def distance_error_rf(self,dis_array, entrance_index, probs):
        dis_error = 0;
        bb = probs.tolist()
        index = bb.index(max(bb))
#        for i in index:
        dis_error = self.get_distance(dis_array,int(entrance_index),index);
#        dis_error = (dis_error)/len(index);
        return dis_error,index
if __name__ == "__main__":
     ignore_list = []
     min_error = 100;
     min_total_error = [];
     
     for n_s in range(120,130,10):
         for n_k in range (6,7,1):
             for ratio in range (70,80,10):
    #             for n_e in range(50,200,10):
                 classifer = Prediction() 
                 total_errors = [];
                 for group in range(1,6):
                    test_head_file = '.\\Data\\'+str(group)+'\\test_rf_head.xls';#back-up-25\\test\\temper\\
                    test_file_base ='.\\Data\\'+str(group)+'\\'#back-up-25\\\\tempertemper\\test\\temper\\
                    train_file =  '.\\Data\\'+str(group)+'\\features.csv';#back-up-25\\\\tempertemper\\test\\
                    raw_data = pd.read_excel(test_head_file,header=None).values
                    test_list = raw_data[0];
                    test_truth = raw_data[1];
                    test_candidate_len = raw_data[2];
                    test_entrances_xs = raw_data[3];
                    test_entrances_ys = raw_data[4];
                    test_dis_array = [];
                    test_num = len(test_list);
                    sum_error = 0
                    target_name = 'class';
                    T = pd.read_csv(train_file);
                    head = list(T.columns)
                    head.remove(target_name)
                    Training_X = T[head].to_numpy()
                    Training_Y = T[target_name].to_numpy()
                    clf = SMOTEBoost(n_samples=n_s,k_neighbors=n_k, n_estimators=ratio)
                    clf.fit(Training_X,Training_Y,sample_weight=None, minority_target=1)

#                    clf = BalancedRandomForestClassifier(n_estimators=n_s, max_depth=n_k, random_state=0)
#                    clf.fit(Training_X, Training_Y)
                    for i in range(test_num):
                        if test_list[i] not in ignore_list:
                            dis_array= raw_data[5:5+int(test_candidate_len[i]),i];
                            test_file = test_file_base+str(int(test_list[i]))+'rftest.csv';
                            test_table = pd.read_csv(test_file);
                            test_X = test_table[head].to_numpy();
                            prob = clf.predict_proba(test_X)
                            cur_dis_error, estimated_index = classifer.distance_error_rf(dis_array, test_truth[i], prob[:,1]);
                            total_errors.append(cur_dis_error);
                        else:
                            print (test_list[i])
                            print (str(test_entrances_xs[i])+' ' + str(test_entrances_ys[i]))
                 m_acc = np.average(total_errors)
                 print (len(total_errors))
                 if m_acc < min_error:
                     prior_n_s = n_s
                     prior_n_k = n_k
                     prior_n_ratio = ratio
                     min_error = m_acc
                     min_total_error = total_errors;
                     print('pn_s:'+str(prior_n_s)+'pn_k:'+str(prior_n_k)+'pratio:' + str(prior_n_ratio))#
                 print('n_s:'+str(n_s)+' n_k:'+str(n_k)+' ratio:' + str(ratio))#
                 print('total_error: '+ str(m_acc))
                 print ('min_error ' + str(min_error))
     
     cdf_plot(min_total_error, 'entrance detection', 100)
     plt.show();
     df = pd.DataFrame(min_total_error)
     df.to_excel('filename8.xlsx')
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     
     