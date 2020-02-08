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

## End-Points

### Create household and member tables
* Method: POST
* Url: localhost/create_household_member_tables
* Parameters: None
* Response: None

Example code in test.py
```
create_household_member_tables(local_host)
```

### Create household
* Method: POST
* Url: localhost/create-household
* Data: housing_type (string)
* Housing type can be one of "Landed", "Condominium", "HDB"
* Response: housing_id in json string format

Example code in test.py
```
response_create_household = create_household(local_host, "HDB")
housing_id = response_create_household.json()
```

### Add member
* Method: POST
* Url: localhost/add-member
* Data: name, gender, marital_status, spouse, occupation_type, DOB, housing_id (string) and annual_income (int)
* Spouse can be one of name or member id of spouse
* Occupation_type can be one of "Unemployed", "Student", "Employed"
* DOB is in the format "DD/MM/YYYY"
* Response: member_id in json string format

Example code in test.py
```
father = hm.household(housing_id)
father_member_id = add_member(local_host, father).json()
```
where father is a dictionary of input data

### List households
* Method: GET
* Url: localhost/list-households
* Parameters: None
* Response: List of households in the database in json format

Example code in test.py
```
response_list_households = list_household(local_host)
print(response_list_households.text)
```

### Show household by housing_id
* Method: GET
* Url: localhost/show-household
* Parameters: housing_id (string)
* Response: Household in the database with given housing_id in json format

Example code in test.py
```
response_show_household = show_household(local_host, housing_id)
print(response_show_household.text)
```

### List households available for specified grant
* Method: GET
* Url: localhost/grants
* Parameters: grant (string)
* Grant can be one of "Student Encouragement Bonus", "Family Togetherness Scheme", "Elder Bonus", "Baby Sunshine Grant", 
"YOLO GST Grant"
* Response: Households in the database eligible for specified grant in json format

Example code in test.py
```
response_grants = get_households_eligible_for_grants(local_host, "Student Encouragement Bonus")
print(response_grants.text)
```

### Delete household by housing_id
* Method: DELETE
* Url: localhost/delete-household
* Parameters: housing_id (string)
* Response: None
* Note: Deletes all members in that household as well

Example code in test.py
```
delete_household(local_host, housing_id)
```

### Delete member by member_id
* Method: DELETE
* Url: localhost/delete-member
* Parameters: member_id (string)
* Response: None

Example code in test.py
```
delete_member(local_host, father_member_id)
```

## Notes
The three households in test_households_and_members.py was chosen to specifically test for the grants API. Household 1
should meet ALL grant criteria, household 2 should meet NONE of the grant criteria and household 3 is a special case to 
test if single parent households meet the "Family Togetherness Scheme" grant.

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web application framework used
* [SQLite](https://www.sqlite.org/index.html) - The database used

## Authors

[Benjamin Chua](https://github.com/BenjaminChua)
