import requests
from globals import local_host
import test_households_and_members as hm


def create_household_member_tables(url):
    add = "/create_household_member_tables"
    response = requests.post(url + add)
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


def show_household(url, housing_id):
    add = "/show-household"
    params = {"housing_id": housing_id}
    response = requests.get(url + add, params=params)
    return response


def add_member(url, member):
    add = "/add-member"
    response = requests.post(url + add, data=member)
    return response


def list_members(url):
    add = "/list-members"
    response = requests.get(url + add)
    return response


def get_households_eligible_for_grants(url, grant):
    add = "/grants"
    params = {"grant": grant}
    response = requests.get(url + add, params=params)
    return response


def delete_household(url, housing_id):
    add = "/delete-household"
    data = {"housing_id": housing_id}
    response = requests.delete(url + add, data=data)
    return response


def delete_member(url, member_id):
    add = "/delete-member"
    data = {"member_id": member_id}
    response = requests.delete(url + add, data=data)
    return response


def print_separator():
    print("-" * 50)
    return None


def main():

    # creates the database, household and member tables
    print("Create database, household and member tables")
    create_household_member_tables(local_host)
    print_separator()

    # creates households and adds members
    print("Create households and added members")
    response_create_household = create_household(local_host, "HDB")
    housing_id1 = response_create_household.json()

    # test for ALL grants
    father, mother, child = hm.household_1(housing_id1)
    add_member(local_host, father)
    add_member(local_host, mother)
    add_member(local_host, child)

    response_create_household = create_household(local_host, "landed")
    housing_id2 = response_create_household.json()

    # test for NO grant and deletion of sole member of household
    father2 = hm.household_2(housing_id2)
    father2_member_id = add_member(local_host, father2).json()

    response_create_household = create_household(local_host, "Condominium")
    housing_id3 = response_create_household.json()

    # test for wife without husband with child < 18 y/o for Family Togetherness bonus
    mother3, child3 = hm.household_3(housing_id3)
    add_member(local_host, mother3)
    add_member(local_host, child3)

    print_separator()

    # list households to check for the additions
    print("List of all households:")
    response_list_households = list_household(local_host)
    print(response_list_households.text)
    print_separator()

    # list eligible households for specified grant
    print("Student Encouragement Bonus:")
    response_grants = get_households_eligible_for_grants(local_host, "Student Encouragement Bonus")
    print(response_grants.text)
    print_separator()

    print("Family Togetherness Scheme:")
    response_grants = get_households_eligible_for_grants(local_host, "Family Togetherness Scheme")
    print(response_grants.text)
    print_separator()

    print("Elder Bonus:")
    response_grants = get_households_eligible_for_grants(local_host, "Elder Bonus")
    print(response_grants.text)
    print_separator()

    print("Baby Sunshine Grant:")
    response_grants = get_households_eligible_for_grants(local_host, "Baby Sunshine Grant")
    print(response_grants.text)
    print_separator()

    print("YOLO GST Grant:")
    response_grants = get_households_eligible_for_grants(local_host, "YOLO GST Grant")
    print(response_grants.text)
    print_separator()

    # delete household by housing id
    print("Delete household:")
    delete_household(local_host, housing_id1)
    # list household to check
    response_list_households = list_household(local_host)
    print(response_list_households.text)
    print_separator()

    # delete member by member id
    print("Delete member:")
    delete_member(local_host, father2_member_id)
    # show household by housing id
    response_show_household = show_household(local_host, housing_id2)
    print(response_show_household.text)

    return


if __name__ == "__main__":
    main()
