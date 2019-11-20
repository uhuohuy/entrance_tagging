# entrance_tagging
OpenStreetMap based Main Entrance Tagging by Using Binary Imbalanced Learning

'osmfeatures-test25.xls' is the raw data set extracted from OSM, which should be put under the Data floder. However it is too large that cannot be uploaded here. Thus, it is shared through google drive. (https://drive.google.com/file/d/1lVG3zhWKvR1SVVN3QgLGAyxmc0c97QXJ/view?usp=sharing) It contains the samples of 320 builidings. For the samples in each building, the starting row is the 'head' (index position 1) row that provides the  latitude (index position 3)  and longitude (index position 4) coordinates of the main entrance of current building and the sample index (index position 2) of th true entrance. The following rows represent the samples in the building, with each row representing the feature vector of a sample. In each row, the first coloum denotes the total number of samples in the building, the second column denotes the linear distance from current sample to the next samples. The thrid and fourth column denote the X-Y coordiante of current sample.

test_list.xls: In  each test group, there is a file, named'test_list.xls', which contains the index of test buildings in each group. 

extraction.py: the code used to process 'osmfeatures-test25.xls'. It divides the total buildings into five test groups (five fold cross validation) based on file 'test_list.xls', and deal with the missing data issue.

training_tagging.py: Conduct the training and tagging procedure based on the grouped training and test data set.
