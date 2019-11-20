# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 17:12:11 2019

@author: xiaohu
"""
from __future__ import division
import csv
import xlwt
import xlrd
import os
import copy;
import numpy as np
from collections import Counter
import pandas as pd
contexts = ['service_ways','landmark','post','main road','parking','pedestrian ways','address street','axis','railway']
context_feature =['service_way_dis','landmark_dis','post_dis','main_p_dis','park_dis','ped_dis','addr_sort','axis_sort','rail_dis']
category = []; """
['opp_shape','shape','bool_arc','bool_v_addr', 'bool_post','bool_addr_acc','face_own', 'bool_visual_mr','bool_landmark'\
,'opp_hole', 'bool_visual_se','bool_v_addr', 'bool_post', 'main_access', 'bool_addr_acc','bool_visual_mr', 'bool_landmark','bool_visual_se'] """
context_num = [0]*len(contexts)
original_features = ['addr_sort','main_access','bool_visual_se','ped_dis','park_dis','landmark_dis']
new_exist_feat_names = ['addr_exist','main_exist','service_exist','pedestrain_exist','bike_exist','landmark_exist']

class DataExtraction:       
    def get_distance(self, dis_array,start_index,end_index):
        ''' Calculate the minimum linear distance between two samples 
            [start_index end_index] along the footprint
            
            Output: the complete training features after imputation:
            Inout:
                dis_array: list of distance between two consecutive samples
                            in the footprint
                start_index: index of the first sample 
                end_index: index of the second sample
             '''
        if start_index> end_index:
             a = start_index;
             start_index = end_index;
             end_index = a;            
        if start_index == end_index:
            return 0;
        temp_dis1 = sum(dis_array[start_index:end_index]);
        temp_dis2 = sum(dis_array[end_index:len(dis_array)])+sum(dis_array[0:start_index]);
        return min(temp_dis1,temp_dis2);
        
    def feature_distance(self,feature1,feature2):
        '''Calculate the feature distance between two normalized feature sets
            Output: euclidean distance between two feature sets:
            Inout:
                feature1: first feature set
                feature2: second feature set 
        '''
        sum_dis = 0;
        for i in range(0,len(feature1)):
            sum_dis += abs(feature1[i]-feature2[i]);
        sum_dis = sum_dis/len(feature1);
        return sum_dis;
            
    def process_missing_data(self,training_features,head,missing_filename):
        ''' impute the missing data in the 'training_features' by using strawman strategy. 
        Specifically, we fill out the missing value of a numerical feature with the median 
        value of the non-missing values of this feature in the 'training_features'. 
        Likewise, we fill out the missing value of a categorical feature with the most frequent
        value of the non-missing values of this feature in the 'training_features'.
        Imputed value will be saved in 'missing_filename', which will be used to fill out the 
        missing values in the test samples.
        
        Output: the complete training features after imputation.
        Input:
            training_features: raw training samples with missing data
            head: set of feature names 
            missing_filename: the name of the file that will be used 
                              to save the imputed value of each feature
            '''

        if os.path.exists(missing_filename):
            os.remove(missing_filename);
        f = xlwt.Workbook();
        ws = f.add_sheet('Sheet1');
        cur_line = 0;
        for column_name in head:
            if column_name != 'class':
                cur_valus = [];
                miss_value = 0;
                bool_missing_column = False;
                missing_row_indexs = [];
                for i, feature in enumerate(training_features):
                    if column_name in feature:
                        cur_valus.append(feature[column_name]);
                    else:
                        bool_missing_column = True;
                        missing_row_indexs.append(i);
                if bool_missing_column:
                    unique_value = np.unique(cur_valus);
                    if len(unique_value)<=4:   # categorical feature
                        max_fre = 0;
                        result = Counter(cur_valus);
                        for val in unique_value:
                            if result[val]>max_fre:
                                miss_value = val;
                                max_fre = result[val]
                    else: # numeric feature
                        miss_value = np.median(cur_valus);
                    for miss_index in missing_row_indexs:
                        training_features[miss_index][column_name] = miss_value;
                ws.write(cur_line,0,column_name);
                ws.write(cur_line,1,miss_value);
                cur_line+=1;
        f.save(missing_filename);
        return training_features;
                        
    def resampling(self,entrance_index, dis_array, feature_values, feature_distance_thres,pyhsical_distance_thres):
        ''' resample the negative samples. That is to choose only strong 
            negative samples into the training set. When the distance
            the negative samples that are close to the positive sample in 
            either physical or feature distance are ruled out from the training 
            samples in order to reduce the interference of the negative 
            samples on the positive sample.
        
        Output: the index of strong negative samples in a building
        Input:
            entrance_index: index of the entrance point (positive sample) 
            feature_values: an 2-d array that containes the values of each feature set 
            feature_distance_thres: the feature distance threshold used to
                                    select the strong negative samples
            pyhsical_distance_thres: the physical distance threshold used to
                                    select the strong negative samples
            '''
        in_range_feature_list = [];
        total_samples_index = range(0,len(dis_array));
        spatil_distance_list = []
        for i in range(0,len(dis_array)):
            temp_dis = self.get_distance(dis_array,entrance_index,i)
            if temp_dis < pyhsical_distance_thres:
                in_range_feature_list.append(i);
                spatil_distance_list.append(temp_dis)
        """feature normalization"""
        norm_features = feature_values;
        for i in range(len(feature_values[0])):
             b=[x[i] for x in feature_values];
             max_b = max(b);
             min_b = min(b);
             for j in range(0,len(feature_values)):
                 if max_b-min_b != 0:
                    norm_features[j][i] = (feature_values[j][i]-min_b)/(max_b-min_b);
                 else:
                    norm_features[j][i] = 0;
        """feature distance calculation"""
        final_merge_distance = [];
        final_sampling_list = [];
        for i, index in enumerate(in_range_feature_list):
            temp_f_dis = self.feature_distance(norm_features[index],norm_features[entrance_index]);
            if temp_f_dis < feature_distance_thres:
                final_sampling_list.append(index);
                temp_merge_dis = spatil_distance_list[i]*temp_f_dis;
                if temp_merge_dis != 0:
                    final_merge_distance.append(1.0/temp_merge_dis);
                else:
                    final_merge_distance.append(0.0);
        negative_list = [x for x in total_samples_index if x not in final_sampling_list];
        return negative_list;
                      
    def load_training_data(self,test_index_list,raw_file_name,missing_filename,group,fea_dis_threshold, phy_dis_threshold):
        ''' extract the training samples for the test group 'group'
        
        Output: non
        Input:
            test_index_list: list of the index of test buildings, which 
                             will be ignored when extracting training samples 
            raw_file_name: name of the file that contains the raw features extracted from OSM 
            group: the index of the test group
            '''
        workbook = xlrd.open_workbook(raw_file_name)
        sheet2 = workbook.sheet_by_index(0) 
        sheet2 = workbook.sheet_by_name('Sheet1')
        negative_training_features = [];
        unique_training_features = [];
        head = set()
        Class = 'class';
        head.add(Class);
        cur_sample = 0;
        entrances = [];
        sum_training_features = [];
        cur_row_index = 0;
        while cur_row_index < sheet2.nrows:
            entrance_index = int(sheet2.cell(cur_row_index,1).value)
            entrance_x = float(sheet2.cell(cur_row_index,2).value)
            entrance_y = float(sheet2.cell(cur_row_index,3).value)
            cur_sample_num = int(sheet2.cell(cur_row_index,4).value);
            if cur_sample not in test_index_list:
                dis_array = [];
                cur_building_features = []
                temp_row_count = 0;
                feature_num = int((int(sheet2.cell(cur_row_index+1,0).value-4))/2);
                temp_feature_valus =  [([0] * feature_num) for p in range(cur_sample_num)]
                temp_feature_names = set()
                for row in range(cur_row_index+1,cur_row_index+cur_sample_num+1):
                    dis_array.append(float(sheet2.cell(row,1).value))
                    features = {};
                    for j in range(0,feature_num):
                        temp_feature_valus[temp_row_count][j] = float(sheet2.cell(row,4+j*2+1).value);
                        column_name = str(sheet2.cell(row,4+j*2).value);
                        temp_feature_names.add(column_name);
                        if column_name in category:
                            features[column_name] = 'str'+str(sheet2.cell(row,4+j*2+1).value);#float(sheet2.cell(row,4+j*2+1).value);
                        else:
                            features[column_name] = float(sheet2.cell(row,4+j*2+1).value);                          
                        head.add(str(sheet2.cell(row,4+j*2).value));
                        """test"""
                    for new_feat in new_exist_feat_names:   
                        head.add(new_feat);
                    for f,ori_feat in enumerate(original_features):
                        if ori_feat in temp_feature_names:
                            features[new_exist_feat_names[f]] = 1;
                        else:
                            features[new_exist_feat_names[f]] = 0;
                    temp_row_count = temp_row_count + 1;
                    cur_building_features.append(features);
                    unique_training_features.append(features);
                """sampling"""
                negative_sample_indexs = self.resampling(entrance_index, dis_array, temp_feature_valus,fea_dis_threshold,phy_dis_threshold);
                sample_result_init = 1;
                sample_indexs = [entrance_index];
                sample_result = [sample_result_init]
                print ('current training building:'+str(cur_sample));
                for i, feat in enumerate(cur_building_features):
                    bool_matched = False;
                    for k, index in enumerate(sample_indexs):
                        if i == index:
                           feat[Class] = 1;
                           entrances.append([entrance_x,entrance_y])
                           for j in range(0,int(sample_result[k])):
                               new_feat = copy.deepcopy(feat);
                               sum_training_features.append(new_feat);
                           bool_matched = True;
                           break;
                    if not bool_matched:
                        if  i in negative_sample_indexs:
                            feat[Class] = 0;
                            negative_training_features.append(feat)
                            new_feat = copy.deepcopy(feat);
                            sum_training_features.append(new_feat);

            cur_row_index = cur_row_index + cur_sample_num + 1;
            cur_sample = cur_sample + 1;
        self.process_missing_data(sum_training_features,head,missing_filename);

        """save into csv"""
        csv_file = r'.\\Data\\'+str(group)+'\\features.csv';
        if os.path.exists(csv_file):
            os.remove(csv_file);
        with open(csv_file, 'w') as csvfile:
            fieldnames = list(head);
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for dic in sum_training_features:
                writer.writerow(dic)
                
        """save entrance data"""
        test_e_file = r'.\\Data\\'+str(group)+'\\positive_entrance.xls'
        f_test_head = xlwt.Workbook();
        ws_test_head = f_test_head.add_sheet('Sheet1');
        if os.path.exists(test_e_file):
            os.remove(test_e_file);
        for i, data in enumerate(entrances):
            ws_test_head.write(i,0,data[0]);
            ws_test_head.write(i,1,data[1]);
        f_test_head.save(test_e_file);
                
    def load_missing_data(self,group,missing_filename):
        workbook = xlrd.open_workbook(missing_filename)
        sheet2 = workbook.sheet_by_index(0)
        sheet2 = workbook.sheet_by_name('Sheet1')
        row = 0;
        missing = {};
        while row < sheet2.nrows:
            missing[str(sheet2.cell(row,0).value)] = float(sheet2.cell(row,1).value);
            row = row +1;
        return missing;

    def load_testing_data(self,test_list,raw_file_name,missing_filename,group):
        ''' extract the test samples for the test group 'group'
        Output: non
        Input:
            test_list: list of the index of test buildings
            raw_file_name: name of the file that contains the raw features extracted from OSM 
            group: the index of the test group
            '''
        '''files used to save the head information of each test buildings, such as the true positive sample'''    
        test_head_file = r'.\\Data\\'+str(group)+'\\test_rf_head.xls'
        if os.path.exists(test_head_file):
            os.remove(test_head_file);
        f_test_head = xlwt.Workbook();
        ws_test_head = f_test_head.add_sheet('Sheet1');
        cur_line = 0;
        for i, data in enumerate(test_list):
            ws_test_head.write(cur_line,i,data);
        cur_line+=5

        test_file_base = r'.\\Data\\'+str(group)+'\\';
        missing_data = self.load_missing_data(group,missing_filename);
        """load the raw feature file"""
        workbook = xlrd.open_workbook(raw_file_name)
        sheet2 = workbook.sheet_by_index(0) # 
        sheet2 = workbook.sheet_by_name('Sheet1')
        head = missing_data.keys();
        cur_sample = 0;
        cur_row_index = 0;
        test_count = 0;
        entrance_index_list = [0]*len(test_list);
        entrace_lat_list = [0]*len(test_list);
        entrace_lont_list = [0]*len(test_list);
        candidat_nums = [0]*len(test_list);
        while cur_row_index < sheet2.nrows:
            entrance_index = int(sheet2.cell(cur_row_index,1).value)
            entrance_x = float(sheet2.cell(cur_row_index,2).value)
            entrance_y = float(sheet2.cell(cur_row_index,3).value)
            cur_sample_num = int(sheet2.cell(cur_row_index,4).value);
            if cur_sample in test_list:
                sample_index = test_list.index(cur_sample);
                entrance_index_list[sample_index] = entrance_index;
                entrace_lat_list[sample_index] = entrance_x;
                entrace_lont_list[sample_index] = entrance_y;
                dis_array = [];
                cur_building_features = []
                temp_row_count = 0;
                feature_num = int((int(sheet2.cell(cur_row_index+1,0).value-4))/2);
                temp_feature_valus =  [([0] * feature_num) for p in range(cur_sample_num)]  
                temp_keys = set([]);
                temp_feature_names = set()
                for row in range(cur_row_index+1,cur_row_index+cur_sample_num+1):
                    dis_array.append(float(sheet2.cell(row,1).value))
                    features = {};
                    for j in range(0,feature_num):
                        temp_feature_valus[temp_row_count][j] = float(sheet2.cell(row,4+j*2+1).value);
                        features[str(sheet2.cell(row,4+j*2).value)] = float(sheet2.cell(row,4+j*2+1).value);
                        temp_feature_names.add(str(sheet2.cell(row,4+j*2).value));
                    for f,ori_feat in enumerate(original_features):
                        if ori_feat in temp_feature_names:
                            features[new_exist_feat_names[f]] = 1;
                        else:
                            features[new_exist_feat_names[f]] = 0;
                    temp_row_count = temp_row_count + 1;
                    for key, value in missing_data.items():
                        if key not in features.keys():
                            features[key] = value;
                            temp_keys.add(key);
                    cur_building_features.append(features);
                for t, target_key in enumerate(context_feature):
                    if target_key in temp_keys:
                        context_num[t]+=1;
                        
                """save the samples for each test building """
                test_file_name = test_file_base+str(cur_sample)+'rftest.csv';
                if os.path.exists(test_file_name):
                    os.remove(test_file_name);
                with open(test_file_name,'w') as csvfile:
                    fieldnames = head;
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for dic in cur_building_features:
                        writer.writerow(dic)
                """save test head"""
                candidat_nums[sample_index]=len(dis_array);
                for i, data in enumerate(dis_array):
                    ws_test_head.write(i+cur_line,sample_index,data);
                test_count = test_count + 1;
            cur_row_index = cur_row_index + cur_sample_num + 1;
            cur_sample +=1;
        for i, data in enumerate(entrance_index_list):
            ws_test_head.write(1,i,data);
        for i, data in enumerate(candidat_nums):
            ws_test_head.write(2,i,data);
        for i, data in enumerate(entrace_lat_list):
            ws_test_head.write(3,i,data);
        for i, data in enumerate(entrace_lont_list):
            ws_test_head.write(4,i,data);
        f_test_head.save(test_head_file);
          
if __name__ == "__main__":
     raw_file_name = r'.\\Data\\osmfeatures-test25.xls';
     group_num = 5;
     phy_dis_thres = 24
     fea_dis_thres = 0.04
     real_total_num = 0;
     for i in range(1,group_num+1):
         print("*"*50)
         print(str(i)+"-th test group")
         missing_filename = r'.\\Data\\'+str(i)+'\\missing.xls';
         model = DataExtraction()
         group_file = r'.\\Data\\'+str(i)+'\\test_list.xls'
         test_list_f = list(pd.read_excel(group_file,header=None).values[0])
         test_list = [int(ele) for ele in test_list_f]
         model.load_training_data(test_list,raw_file_name,missing_filename,i,phy_dis_thres,fea_dis_thres);
         model.load_testing_data(test_list,raw_file_name,missing_filename,i)
