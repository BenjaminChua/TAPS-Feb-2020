import flask
from flask import request, jsonify, url_for
import sqlite3
import uuid
import pandas as pd
import globals as gb
from datetime import date

app = flask.Flask(__name__)


def connect_to_database():
    db = gb.db
    conn = sqlite3.connect(db)
    print(f"Connected to database: {db}")
    c = conn.cursor()
    return conn, c


def commit_and_close_database(conn):
    conn.commit()
    conn.close()
    print(f"Connection to database is closed")
    return None


# single execute function
def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    if fetch_one and fetch_all:
        raise AssertionError(f"Please ensure that {query} only contains either fetch_one==True or "
                             f"fetch_all==True or both false.")
    conn, c = connect_to_database()
    result = None
    try:
        if params is None:
            if fetch_one:
                result = c.execute(query).fetchone()
            elif fetch_all:
                result = c.execute(query).fetchall()
            else:  # dont fetch
                c.execute(query)
        else:
            if fetch_one:
                result = c.execute(query, params).fetchone()
            elif fetch_all:
                result = c.execute(query, params).fetchall()
            else:  # dont fetch
                c.execute(query, params)
    except sqlite3.Error as error:
        print("SQL error:", error)
    commit_and_close_database(conn)
    return result


def create_household_table():
    create_household_table_query = "CREATE TABLE household(housing_id TEXT PRIMARY KEY, housing_type TEXT)"
    execute_query(create_household_table_query)
    return True


def create_member_table():
    create_member_table_query = "CREATE TABLE member(member_id TEXT PRIMARY KEY, name TEXT, gender TEXT, " \
                                "marital_status TEXT, spouse TEXT, occupation_type TEXT, annual_income INTEGER" \
                                ", dob TEXT, housing_id TEXT)"
    execute_query(create_member_table_query)
    return True


@app.route('/create_household_member_tables', methods=['POST'])
def home():
    create_household_table()
    create_member_table()
    return """Created household and member table"""


@app.route('/create-household', methods=['POST'])
def create_household():
    housing_type = request.form["housing_type"]

    # create a unique housing id
    housing_id = str(uuid.uuid4())

    # insert household into household table
    insert_house_query = "INSERT INTO household(housing_id, housing_type) VALUES(?, ?)"
    execute_query(insert_house_query, (housing_id, housing_type))

    return jsonify(housing_id)


@app.route('/add-member', methods=['POST'])
def add_member():
    # create a unique member id
    member_id = str(uuid.uuid4())

    # get member details from inputs (requires housing id)
    val_list = [val for val in request.form.values()]
    val_tuple = tuple([member_id] + val_list)

    # insert member into member table
    insert_member_query = "INSERT INTO member VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    execute_query(insert_member_query, val_tuple)
    return jsonify(member_id)


@app.route('/list-households', methods=['GET'])
def list_households():
    # Select all households and members
    select_household_query = "SELECT * FROM household"
    household_results = execute_query(select_household_query, fetch_all=True)
    select_member_query = "SELECT * FROM member"
    member_results = execute_query(select_member_query, fetch_all=True)

    # init output as a list
    output = []

    # Housing id is used as the key and housing type the value
    household_dict = {housing_id: housing_type for housing_id, housing_type in household_results}

    # Members are converted to a data frame and grouped by housing id
    # Each household is a dictionary of family members
    member_df = pd.DataFrame(member_results, columns=gb.member_params)
    member_df_grouped_by_housing_id = member_df.groupby("housing_id")
    for housing_id, group in member_df_grouped_by_housing_id:
        household = {"housing_id": housing_id, "FamilyMembers": group.to_dict(orient="records"),
                     "housing_type": household_dict[housing_id]}
        output.append(household)

    return jsonify(output)


@app.route('/show-household', methods=['GET'])
def show_household():
    housing_id = request.args["housing_id"]

    # select the desired household by housing id
    select_household_query = "SELECT * FROM household WHERE housing_id=?"
    household_result = execute_query(select_household_query, (housing_id,), fetch_one=True)

    # init output as a dict of housing id and housing type
    output = {key: val for key, val in zip(gb.household_params, household_result)}

    # select members from the desired household by housing id
    select_member_query = "SELECT * FROM member WHERE housing_id=?"
    member_results = execute_query(select_member_query, (output["housing_id"],), fetch_all=True)

    # init family members as a list
    family_members = []
    for member_result in member_results:
        member_dict = {key: val for key, val in zip(gb.member_params, member_result)}
        family_members.append(member_dict)
    output["FamilyMembers"] = family_members

    return jsonify(output)


def age(DOB):
    return (date.today() - DOB.date()).days // 365


def younger_than_age(age, threshold):
    return 1 if age < threshold else 0


def older_than_age(age, threshold):
    return 1 if age > threshold else 0


def is_HDB(housing_type):
    return True if housing_type == "HDB" else False


@app.route('/grants', methods=['GET'])
def list_household_member_for_grants():
    grant = request.args["grant"]
    assert grant in gb.grant_names

    # Select all households and members
    select_household_query = "SELECT * FROM household"
    household_results = execute_query(select_household_query, fetch_all=True)
    select_member_query = "SELECT * FROM member"
    member_results = execute_query(select_member_query, fetch_all=True)

    # convert query results into data frames
    # combine data frames into df
    output = []
    household_dict = {housing_id: housing_type for housing_id, housing_type in household_results}
    household_df = pd.DataFrame(household_results, columns=gb.household_params)
    household_df.set_index("housing_id", inplace=True)
    housing_ids = household_df.index.to_list()
    member_df = pd.DataFrame(member_results, columns=gb.member_params)
    df = household_df.merge(member_df, left_index=True, right_on="housing_id")

    # age
    df["DOB"] = pd.to_datetime(df["DOB"])
    df["age"] = df["DOB"].apply(age)
    df["under_5"] = df["age"].apply(younger_than_age, threshold=5)
    df["under_16"] = df["age"].apply(younger_than_age, threshold=16)
    df["under_18"] = df["age"].apply(younger_than_age, threshold=18)
    df["over_50"] = df["age"].apply(older_than_age, threshold=50)

    # creating filter table
    for housing_id in housing_ids:
        household = df[df["housing_id"] == housing_id]

        # income
        household_df.loc[housing_id, "household_income"] = household["annual_income"].sum()

        # age
        household_df.loc[housing_id, "under_5"] = True if household["under_5"].sum() >= 1 else False
        household_df.loc[housing_id, "under_16"] = True if household["under_16"].sum() >= 1 else False
        household_df.loc[housing_id, "under_18"] = True if household["under_18"].sum() >= 1 else False
        household_df.loc[housing_id, "over_50"] = True if household["over_50"].sum() >= 1 else False

        # spouse
        household_df.loc[housing_id, "husband_wife"] = True if \
            household["name"].isin(household["spouse"]).sum() >= 2 else False

    # HDB or others
    household_df["HDB"] = household_df["housing_type"].apply(is_HDB)

    # get households eligible for specific grant
    if grant == "Student Encouragement Bonus":
        households_with_grant = household_df[(household_df["household_income"] < 150000) & household_df["under_16"]]
    elif grant == "Family Togetherness Scheme":
        households_with_grant = household_df[household_df["husband_wife"] & household_df["under_18"]]
    elif grant == "Elder Bonus":
        households_with_grant = household_df[household_df["HDB"] & household_df["over_50"]]
    elif grant == "Baby Sunshine Grant":
        households_with_grant = household_df[household_df["under_5"]]
    elif grant == "YOLO GST Grant":
        households_with_grant = household_df[household_df["HDB"] & (household_df["household_income"] < 100000)]
    else:
        raise jsonify(f"Grant: {grant} is not a valid grant")

    # format output
    households_with_grant = member_df[member_df["housing_id"].isin(households_with_grant.index)]
    households_with_grant_grouped_by_housing_id = households_with_grant.groupby("housing_id")
    for housing_id, group in households_with_grant_grouped_by_housing_id:
        household = {"housing_id": housing_id, "FamilyMembers": group.to_dict(orient="records"),
                     "housing_type": household_dict[housing_id]}
        output.append(household)
    return jsonify(output)


@app.route('/delete-household', methods=['DELETE'])
def delete_household():
    housing_id = request.form["housing_id"]
    delete_household_query = "DELETE FROM household WHERE housing_id=?"
    execute_query(delete_household_query, (housing_id,))
    delete_members_query = "DELETE FROM member WHERE housing_id=?"
    execute_query(delete_members_query, (housing_id,))
    return """Deleted household"""


@app.route('/delete-member', methods=['DELETE'])
def delete_member():
    member_id = request.form["member_id"]
    delete_member_query = "DELETE FROM member WHERE member_id=?"
    execute_query(delete_member_query, (member_id,))
    return """Deleted member"""


@app.route('/get-members', methods=['GET'])
def get_members():
    # member_id = request.form["member_id"]
    member_query = "SELECT * FROM member"
    response = execute_query(member_query, fetch_all=True)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
