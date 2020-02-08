# TAPS #6 Technical Assessment Q2.

Government Grant Disbursement API: Creating a RESTful API that would help decide on the households eligible for various upcoming government grants.

## Getting Started

Git clone this repository or download ZIP and change into the directory

### Prerequisites

Install the Conda environment using the environment.yml file

```
$ conda env create -f environment.yml
```

### Installing

To specify a database, change the db variable in globals.py file

After which, run the app.py file 

```
$ python app.py
```

Check if the local host is same as that in the globals.py file

```
Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Testing

### The test.py file contains test calls to the API

Run test.py

```
$ python test.py
```

Adjustments to the households and members can be made in test_households_and_members.py. Any additional household or 
member would require amendments in test.py.

## Built With

[Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web application framework used

## Authors

[Benjamin Chua](https://github.com/BenjaminChua)
