import flask
from flask import request, jsonify, url_for
import sqlite3
import uuid
import pandas as pd
import globals as gb
from datetime import date

app = flask.Flask(__name__)


def connect_to_database():
    db = "grant_disbursement.db"
    conn = sqlite3.connect(db)
    print(f"Connected to database: {db}")
    c = conn.cursor()
    return conn, c


def commit_and_close_database(conn):
    conn.commit()
    conn.close()
    print(f"Connection to database is closed")
    return None


### single execute function
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


@app.route('/', methods=['GET'])
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
    return """Added member"""


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


def less_than_age(age, threshold):
    if age < threshold:
        return 1
    else:
        return 0


@app.route('/grants', methods=['GET'])
def list_household_member_for_grants():
    grant = request.args["grant"]
    assert grant in gb.grant_names

    # Select all households and members
    select_household_query = "SELECT * FROM household"
    household_results = execute_query(select_household_query, fetch_all=True)
    select_member_query = "SELECT * FROM member"
    member_results = execute_query(select_member_query, fetch_all=True)

    output = []
    household_dict = {housing_id: housing_type for housing_id, housing_type in household_results}
    household_df = pd.DataFrame(household_results, columns=gb.household_params)
    member_df = pd.DataFrame(member_results, columns=gb.member_params)
    df = household_df.merge(member_df, on="housing_id")
    df["DOB"] = pd.to_datetime(df["DOB"])
    df["age"] = df["DOB"].apply(age)
    df["under_16"] = df["age"].apply(less_than_age, threshold=16)
    df_grouped_by_housing_id = df.groupby("housing_id").sum()
    household_for_student_bonus = df_grouped_by_housing_id[(df_grouped_by_housing_id["annual_income"] < 150000) |
                                                           (df_grouped_by_housing_id["under_16"] >= 1)]
    if ~household_for_student_bonus.empty:
        grant_df = member_df[member_df["housing_id"].isin(household_for_student_bonus.index)]
        grant_df_grouped_by_housing_id = grant_df.groupby("housing_id")
        for housing_id, group in grant_df_grouped_by_housing_id:
            household = {"housing_id": housing_id, "FamilyMembers": group.to_dict(orient="records"),
                         "housing_type": household_dict[housing_id]}
            output.append(household)
    return jsonify(output)



if __name__ == "__main__":
    app.run(debug=True)
