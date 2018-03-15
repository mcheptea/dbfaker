#!/usr/bin/env python

import argparse
from faker import Factory
from collections import OrderedDict
import json
import MySQLdb

print "[ Database Faker ]\n"

# arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-H', '--host', help='The dababase server host', default='127.0.0.1')
parser.add_argument('-P', '--port', help='The dababase server port', default='3306')
parser.add_argument('-u', '--user', help='The dababase username', default='user')
parser.add_argument('-p', '--password', help='The dababase password', default='userpasswd')
parser.add_argument('-d', '--database', help='The dababase name', default='mydatabase')
defaultFakeValues = parser.add_argument_group('Default fake values.')
defaultFakeValues.add_argument('-fp', '--fakePassword', help='Fake password value, set in the password fields',
                               default='1234qwer')
fakeRules = parser.add_argument_group('Fake rules options.')
fakeRules.add_argument('-irf', '--inputRulesFile', help='The file containing the faking rules.', default="rules.json")
fakeRules.add_argument('-isf', '--inputSynchronizationFile', help='The file containing the synchronization rules.',
                       default="synchronization.json")
fakeRules.add_argument('-grf', '--generateRulesFile', help='Generate faking rules file.')
fakeRules.add_argument('-gsf', '--generateSynchronizationFile', help='Generate synchronization rules file.')
args = parser.parse_args()

# defaults
FAKE_PASSWORD = args.fakePassword

# data types
EMAIL           = "_email"          # fake email
PASSWORD        = "_password"       # set password
FIRST_NAME      = "_first_name"     # fake first name
LAST_NAME       = "_last_name"      # fake last name
FULL_NAME       = "_full_name"      # fake full name
TEXT            = "_text"           # fake lipsum text
ADDRESS         = "_address"        # fake random address
EMPTY_STRING    = "_empty_string"   # empties the field
COMPANY_NAME    = "_company_name"   # fake company name
ZEROED          = "_zeroed"         # sets field to disabled (zero), useful for boolean (tinyint)

# sample table rule set
tableRules = {
    "table_1": {
        PASSWORD: ["password"],
        EMAIL: ["email"]
    },
    "table_2": {
        FULL_NAME: ["name"],
        ADDRESS: ["address"]
    },
}

synchronizationRules = {}

if args.generateRulesFile is not None:
    with open(args.generateRulesFile, 'w') as file:
        json.dump(tableRules, file, indent=4, sort_keys=True)
    print "Sample rules written to: {}".format(args.generateRulesFile)
    exit(0)

if args.generateSynchronizationFile is not None:
    synchronizationRulesExample = {
        "table_1": {
            "table_1_column_name_1": [
                {
                    "table": "table_2",
                    "column": "table_2_column_name_1",
                    "on-this-column": "table_1_column_name_2",
                    "on-sync-column": "table_2_column_name_2"
                },
                {
                    "table": "table_3",
                    "column": "table_3_column_name_1",
                    "on-this-column": "table_1_column_name_2",
                    "on-sync-column": "table_3_column_name_2"
                }
            ]
        },
        "table_4": {
            "table_4_column_name_1": [
                {
                    "table": "table_5",
                    "columns": ["table_5_column_name_1", "table_5_column_name_2"],
                    "on-this-column": "table_4_column_name_2",
                    "on-sync-column": "table_5_column_name_3"
                }
            ]
        },
        "table_6": {
            "table_6_column_name_1": [
                {
                    "table": "table_7",
                    "join": {
                        "column": "table_8_column_name_1",
                        "table": "table_8",
                        "on-this-column": "table_7_column_name_1",
                        "on-sync-column": "table_8_column_name_2"
                    },
                    "on-this-column": "table_6_column_name_2",
                    "on-sync-column": "table_7_column_name_2"
                },
            ]
        }
    }
    with open(args.generateSynchronizationFile, 'w+') as file:
        json.dump(synchronizationRulesExample, file, indent=4, sort_keys=True)
    print "Sample synchronization written to: {}".format(args.generateSynchronizationFile)
    exit(0)

if args.inputRulesFile is not None:
    with open(args.inputRulesFile) as file:
        tableRules = json.load(file)
    print "Rules loaded from: {}..\n".format(args.inputRulesFile)

if args.inputSynchronizationFile is not None:
    with open(args.inputSynchronizationFile) as file:
        synchronizationRules = json.load(file, object_pairs_hook=OrderedDict)
    print "Rules loaded from: {}..\n".format(args.inputSynchronizationFile)

# db connection
db = MySQLdb.connect(host=args.host, user=args.user, passwd=args.password, db=args.database, port=int(args.port))


# Functions
def processTable(table, rules):
    """Iterates over the rules and fakes the associated fields."""
    for rule in rules:
        for column in rules[rule]:
            print "    {}.{}..".format(table, column),
            fakeColumnByRule(table, column, rule)


def fakeColumnByRule(table, column, rule):
    """Fakes a specific column based on data rule."""
    if rule == EMAIL:
        fakeEmails(table, column)
    elif rule == PASSWORD:
        fakePasswords(table, column)
    elif rule == LAST_NAME or rule == FIRST_NAME:
        fakeNames(table, column, rule)
    elif rule == TEXT:
        fakeText(table, column)
    elif rule == FULL_NAME:
        fakeFullNames(table, column)
    elif rule == ADDRESS:
        fakeAddress(table, column)
    elif rule == EMPTY_STRING:
        emptyString(table, column)
    elif rule == COMPANY_NAME:
        fakeCompanyNames(table, column)
    elif rule == ZEROED:
        setToZero(table, column)


def fakeEmails(table, column):
    """Fakes an email column."""
    sql = "UPDATE {0} SET {1} = CONCAT(id, OLD_PASSWORD('{0}'), '@da.emailx.net');".format(table, column)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print "x"
        print "      Error: " + str(e)
        db.rollback()
        return
    print "ok"


def fakeNames(table, column, type=FIRST_NAME):
    """Fakes a name field."""
    fake = Factory.create()
    cursor = db.cursor()

    selectSql = "SELECT id FROM {}".format(table)
    try:
        cursor.execute(selectSql)
        ids = cursor.fetchall()
    except Exception, e:
        print "x"
        print "      Can't select ids, error: " + str(e)
        return

    try:
        for id in ids:
            name = fake.first_name() if type == FIRST_NAME else fake.last_name()
            updateSql = "UPDATE {0} SET {1} = '{2}' WHERE id = {3}".format(table, column, name, id[0])
            cursor.execute(updateSql)
            db.commit()
    except Exception, e:
        print "x"
        print "      Can't fake names, error: " + str(e)
        return
    print "ok"


def fakeFullNames(table, column):
    """Fakes a full name field."""
    fake = Factory.create()
    cursor = db.cursor()

    selectSql = "SELECT id FROM {}".format(table)
    try:
        cursor.execute(selectSql)
        ids = cursor.fetchall()
    except Exception, e:
        print "x"
        print "      Can't select ids, error: " + str(e)
        return

    try:
        for id in ids:
            name = fake.name()
            updateSql = "UPDATE {0} SET {1} = '{2}' WHERE id = {3}".format(table, column, name, id[0])
            cursor.execute(updateSql)
            db.commit()
    except Exception, e:
        print "x"
        print "      Can't fake company names, error: " + str(e)
        return
    print "ok"


def fakeCompanyNames(table, column):
    """Fakes a company name field."""
    fake = Factory.create()
    cursor = db.cursor()

    selectSql = "SELECT id FROM {}".format(table)
    try:
        cursor.execute(selectSql)
        ids = cursor.fetchall()
    except Exception, e:
        print "x"
        print "      Can't select ids, error: " + str(e)
        return

    try:
        for id in ids:
            name = fake.company()
            updateSql = "UPDATE {0} SET {1} = '{2}' WHERE id = {3}".format(table, column, name, id[0])
            cursor.execute(updateSql)
            db.commit()
    except Exception, e:
        print "x"
        print "      Can't fake company names, error: " + str(e)
        return
    print "ok"


def fakePasswords(table, column, password=FAKE_PASSWORD):
    sql = "UPDATE {0} SET {1} = '{2}';".format(table, column, password)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print "x"
        print "      Error: " + str(e)
        db.rollback()
        return
    print "ok"


def fakeText(table, column):
    """Fakes a text field."""
    fake = Factory.create()
    text = fake.text()
    sql = "UPDATE {0} SET {1} = '{2}';".format(table, column, text)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print "x"
        print "      Error: " + str(e)
        db.rollback()
        return
    print "ok"


def fakeAddress(table, column):
    """Fakes an address field."""
    fake = Factory.create()
    address = fake.address()
    sql = "UPDATE {0} SET {1} = '{2}';".format(table, column, address)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print "x"
        print "      Error: " + str(e)
        db.rollback()
        return
    print "ok"


def emptyString(table, column):
    """Nullifies/empties a field."""
    sql = "UPDATE {0} SET {1} = '';".format(table, column)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print "x"
        print "      Error: " + str(e)
        db.rollback()
        return
    print "ok"


def setToZero(table, column):
    """Sets a field to a field."""
    sql = "UPDATE {0} SET {1} = 0;".format(table, column)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        print "x"
        print "      Error: " + str(e)
        db.rollback()
        return
    print "ok"


def extract_value_column(joins):
    if 'join' in joins:
        return extract_value_column(joins['join'])
    join_table = joins['table']
    if 'columns' in joins:
        return "CONCAT_WS(' ', {0}.{1})".format(join_table, ", {0}.".format(join_table).join(joins['columns']))
    return "{0}.{1}".format(join_table, joins['column'])


def build_joins(table_for_join, join):
    additional_join_statement = ''
    if 'join' in join:
        additional_join_statement = build_joins(join['table'], join['join'])
    current_join_statement = "INNER JOIN {2} ON {2}.{3} = {0}.{1} ".format(table_for_join, join['on-this-column'],
                                                                           join['table'], join['on-sync-column'])

    return current_join_statement + additional_join_statement


def synchronize_table_column(synchronization_table, synchronization_column, joins_list):
    for joins in joins_list:
        update_table_statement = "UPDATE {} ".format(synchronization_table)
        value_column = extract_value_column(joins)
        set_statement = "SET {0}.{1} = {2} ".format(table, synchronization_column, value_column)
        join_statement = build_joins(synchronization_table, joins)
        sql = update_table_statement + join_statement + set_statement + ';'
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
        except Exception, e:
            print "x"
            print "      Error: " + str(e)
            db.rollback()
            return
        print "        Synchronized from {}".format(value_column)


# run
for table in tableRules:
    print "Faking {}..".format(table)
    processTable(table, tableRules[table])

print "\n\n"

for table in synchronizationRules:
    print "Synchronization of {}".format(table)
    for column in synchronizationRules[table]:
        print "    Synchronize {}".format(column)
        synchronize_table_column(table, column, synchronizationRules[table][column])

db.close()
print "\n[ Done ]"
