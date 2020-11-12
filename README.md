
# Entrance Detection 
This project is to detect the main entrance of publich buildings based only on the available geospatial data on OpenStreetMap (OSM).


## Install

The script requires Python >= 3.6.1 and uses maiunly the libraries [imblearn](https://imbalanced-learn.readthedocs.io/en/stable/index.html) and [sklearn](https://scikit-learn.org/stable/).

> The scripts run successfully on windows 8, ubuntu 16.4, and ubuntu 18.4 with Python 3.6.2.

Please clone this repository and install the [required dependencies](requirements.txt) as follows:

```bash
git clone ...
cd entrance_tagging
pip install -r requirements.txt
```

## Usage



### Data Preprocessing
The extracted data of the total buildings, [osmfeatures-test25.xls](https://drive.google.com/file/d/1lVG3zhWKvR1SVVN3QgLGAyxmc0c97QXJ/view?usp=sharing)，should be put under the [Data](Data/)  folder. The raw data is then processed (missing data issue) and divided into five groups (five fold cross validation). The building index of each group is saved in [test_list.xls](Data/1/test_list.xls) , which is put under each group folder.

You can run the script as follows:

```bash
python extraction.py
```

### Trainging and Predicting
Then, we will conduct the training and predicting tasks based on the grouped training and test data set.
You can run the script as follows:

```bash
python training_tagging.py
```




## Citation

missing now

## License

missing now
