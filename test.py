import requests


def set_up_database(url):
    response = requests.get(url)
    return response


def create_household(url, housing_type):
    add = "/create-household"
    data = {"housing_type": housing_type}
    response = requests.post(url + add, data=data)
    return response


def list_household(url):
    add = "/list-households"
    response = requests.get(url + add)
    return response


def add_member(url, member):
    add = "/add-member"
    response = requests.post(url + add, data=member)
    return response


def list_members(url):
    add = "/list-members"
    response = requests.get(url + add)
    return response


def main():
    url = "http://127.0.0.1:5000"
    housing_type = 'landed'
    response_database = set_up_database(url)
    """
    response_create_household = create_household(url, housing_type)
    housing_id = response_create_household.json()

    father = {"name": "John",
              "gender": "M",
              "marital_status": "Married",
              "spouse": "Jane",
              "occupation_type": "Engineer",
              "annual_income": 100000,
              "DOB": "10/05/1985",
              "housing_id": housing_id}

    mother = {"name": "Jane",
              "gender": "F",
              "marital_status": "Married",
              "spouse": "John",
              "occupation_type": "UI designer",
              "annual_income": 150000,
              "DOB": "01/01/1989",
              "housing_id": housing_id}

    child = {"name": "Mary",
             "gender": "F",
             "marital_status": "Single",
             "spouse": "NA",
             "occupation_type": "Student",
             "annual_income": 0,
             "DOB": "01/01/2014",
             "housing_id": housing_id}

    response_add_member = add_member(url, father)
    response_add_member = add_member(url, mother)
    response_add_member = add_member(url, child)
    """
    response_list_households = list_household(url)
    response_list_members = list_members(url)

    print(response_list_households.text)
    print(response_list_members.text)


if __name__ == "__main__":
    main()
