def household_1(housing_id):
    father = {"name": "John",
              "gender": "M",
              "marital_status": "Married",
              "spouse": "Jane",
              "occupation_type": "Employed",
              "annual_income": 15000,
              "DOB": "10/05/1965",
              "housing_id": housing_id}

    mother = {"name": "Jane",
              "gender": "F",
              "marital_status": "Married",
              "spouse": "John",
              "occupation_type": "Employed",
              "annual_income": 70000,
              "DOB": "01/01/1971",
              "housing_id": housing_id}

    child = {"name": "Mary",
             "gender": "F",
             "marital_status": "Single",
             "spouse": "NA",
             "occupation_type": "Student",
             "annual_income": 0,
             "DOB": "01/01/2018",
             "housing_id": housing_id}
    return father, mother, child


def household_2(housing_id):
    father2 = {"name": "James",
               "gender": "M",
               "marital_status": "Single",
               "spouse": "NA",
               "occupation_type": "Employed",
               "annual_income": 100000,
               "DOB": "10/05/1981",
               "housing_id": housing_id}

    return father2


def household_3(housing_id):
    mother3 = {"name": "Jennifer",
               "gender": "F",
               "marital_status": "Single",
               "spouse": "NA",
               "occupation_type": "Employed",
               "annual_income": 150000,
               "DOB": "10/05/1981",
               "housing_id": housing_id}

    child3 = {"name": "Jan",
              "gender": "M",
              "marital_status": "Single",
              "spouse": "NA",
              "occupation_type": "Student",
              "annual_income": 0,
              "DOB": "10/05/2008",
              "housing_id": housing_id}

    return mother3, child3
