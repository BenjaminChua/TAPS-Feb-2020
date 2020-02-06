import flask
from flask import request, jsonify
import sqlite3
import uuid

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


# def create_database_table(c):
#     try:
#         create_database_table_query = "CREATE TABLE database(housing_id INT PRIMARY KEY, housing_type TEXT," \
#                                       "name TEXT, gender TEXT, marital_status TEXT, spouse TEXT, occupation_type TEXT," \
#                                       "annual_income INTEGER, dob TEXT)"
#         c.execute(create_database_table_query)
#     except sqlite3.Error as error:
#         print("SQL error:", error)
#     return None


def create_household_table(c):
    try:
        create_household_table_query = "CREATE TABLE household(housing_id TEXT PRIMARY KEY, housing_type TEXT)"
        c.execute(create_household_table_query)
    except sqlite3.Error as error:
        print("SQL error:", error)
    return None


def create_member_table(c):
    try:
        create_member_table_query = "CREATE TABLE member(member id TEXT PRIMARY KEY, name TEXT, gender TEXT, marital_status TEXT, " \
                                    "spouse TEXT, occupation_type TEXT, annual_income INTEGER, dob TEXT, housing_id TEXT)"
        c.execute(create_member_table_query)
    except sqlite3.Error as error:
        print("SQL error:", error)
    return None


@app.route('/', methods=['GET'])
def home():
    conn, c = connect_to_database()
    # create_database_table(c)
    create_household_table(c)
    create_member_table(c)
    commit_and_close_database(conn)
    return """<h1> Hello World </h1>"""


@app.route('/create-household', methods=['POST'])
def create_household():
    housing_type = request.form["housing_type"]
    housing_id = str(uuid.uuid4())
    conn, c = connect_to_database()
    insert_house_query = "INSERT INTO household(housing_id, housing_type) VALUES(?, ?)"
    c.execute(insert_house_query, (housing_id, housing_type))
    commit_and_close_database(conn)
    return jsonify(housing_id)


@app.route('/add-member', methods=['POST'])
def add_member():
    conn, c = connect_to_database()
    member_id = str(uuid.uuid4())
    val_list = [val for val in request.form.values()]
    val_tuple = tuple([member_id] + val_list)
    print(val_tuple)
    insert_member_query = "INSERT INTO member VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    c.execute(insert_member_query, val_tuple)
    commit_and_close_database(conn)
    return """Added member"""


@app.route('/list-households', methods=['GET'])
def list_households():
    conn, c = connect_to_database()
    select_household_query = "SELECT * FROM household"
    household_results = c.execute(select_household_query).fetchall()
    output = {}
    household_params = ["housing_id", "housing_type"]
    member_params = ["member_id", "name", "gender", "marital_status", "spouse", "occupation_type", "annual_income", "DOB",
                     "housing_id"]
    for i, household_result in enumerate(household_results):
        household_dict = {key: val for key, val in zip(household_params, household_result)}
        select_member_query = "SELECT * FROM member WHERE housing_id=?"
        member_results = c.execute(select_member_query, (household_dict["housing_id"],)).fetchall()
        for j, member_result in enumerate(member_results):
            member_dict = {key: val for key, val in zip(member_params, member_result)
                           if key != "member_id" and key != "housing_id"}
            household_dict[str(j)] = member_dict
        output[str(i)] = household_dict

    commit_and_close_database(conn)
    return jsonify(output)


@app.route('/list-members', methods=['GET'])
def list_members():
    conn, c = connect_to_database()
    query = "SELECT * FROM member"
    results = c.execute(query).fetchall()
    commit_and_close_database(conn)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
