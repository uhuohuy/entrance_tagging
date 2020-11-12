
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

### Data Preparation
[osmfeatures-test25.xls]( data/osmfeatures-test25.xls) is the raw data set extracted from OSM, which should be put under the Data floder. However it is too large that cannot be uploaded here. Thus, it is shared through google drive. (https://drive.google.com/file/d/1lVG3zhWKvR1SVVN3QgLGAyxmc0c97QXJ/view?usp=sharing) It contains the samples of 320 builidings extracted from OSM. For the samples in each building, the starting row is the 'head' (index position 1) row that provides the  latitude (index position 3)  and longitude (index position 4) coordinates of the main entrance of current building and the sample index (index position 2) of th true entrance. The following rows represent the samples in the building, with each row representing the feature vector of a sample. In each row, the first coloum denotes the total number of samples in the building, the second column denotes the linear distance from current sample to the next samples. The thrid and fourth column denote the X-Y coordiante of current sample.

test_list.xls: In  each test group, there is a file, named'test_list.xls', which contains the index of test buildings in each group. 


### Data Preprocessing
First, the extracted data of the total buildings, which is saved in [test_list.xls]( data/test_list.xls)， is divided into five test groups (five fold cross validation). During this procedure, the missing data issue will also be handled.

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

The script processes the [astronauts data set]( data/astronauts.json) and stores the plots in the directory `results`.
The directory will be created by the script.
Existing result plots will be overwritten.



extraction.py: the code used to process 'osmfeatures-test25.xls'. It divides the total buildings into five test groups (five fold cross validation) based on file 'test_list.xls', and deal with the missing data issue.

training_tagging.py: 

smote.py: SmoteBoost classifer, originally from (https://github.com/dialnd/imbalanced-algorithms/blob/master/smote.py)


### Astronaut Data

The data set has been generated from the following SPARQL query [[1]] (retrieval date: 2018-10-25).

You can replace the data set as follows:
- Run the SPARQL query
- Download the resulting data formatted as JSON
- Replace the file `data/astronauts.json`

[1]: https://query.wikidata.org/#%23Birthplaces%20of%20astronauts%0ASELECT%20DISTINCT%20%3Fastronaut%20%3FastronautLabel%20%3Fbirthdate%20%3FbirthplaceLabel%20%3Fsex_or_genderLabel%20%3Ftime_in_space%20%3Fdate_of_death%20WHERE%20%7B%0A%20%20%3Fastronaut%20%3Fx1%20wd%3AQ11631.%0A%20%20%3Fastronaut%20wdt%3AP569%20%3Fbirthdate.%0A%20%20%3Fastronaut%20wdt%3AP19%20%3Fbirthplace.%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22.%20%7D%0A%20%20OPTIONAL%20%7B%20%3Fastronaut%20wdt%3AP21%20%3Fsex_or_gender.%20%7D%0A%20%20OPTIONAL%20%7B%20%3Fastronaut%20wdt%3AP2873%20%3Ftime_in_space.%20%7D%0A%20%20OPTIONAL%20%7B%20%3Fastronaut%20wdt%3AP570%20%3Fdate_of_death.%20%7D%0A%7D%0AORDER%20BY%20DESC%28%3Ftime_in_space%29


## Citation

If you use this work in a research publication,
please cite the specific version that you used using the citation metadata on Zenodo [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.ZENODO-DOI.svg)](https://doi.org/10.5281/zenodo.ZENODO-DOI).

You can find an overview about the different versions in the [changelog](CHANGELOG.md).

## Contributors

Here you find the main contributors to the material:

- Martin Stoffers
- Tobias Schlauch
- Katrin Leinweber

## License

Please see the file [LICENSE.md](LICENSE.md) for further information about how the content is licensed.
