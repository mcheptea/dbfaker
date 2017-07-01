#!/usr/bin/env python

import argparse
from faker import Factory
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
defaultFakeValues.add_argument('-fp', '--fakePassword', help='Fake password value, set in the password fields', default='1234qwer')
fakeRules = parser.add_argument_group('Fake rules options.')
fakeRules.add_argument('-irf', '--inputRulesFile', help='The file containing the faking rules.', required=True)
fakeRules.add_argument('-grf', '--generateRulesFile', help='Generate faking rules file.')
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

if args.generateRulesFile is not None:
    with open(args.generateRulesFile, 'w') as file:
        json.dump(tableRules, fp, indent=4, sort_keys=True)
    print "Sample rules written to {}".format(args.generateRulesFile)
    exit(0)

if args.inputRulesFile is not None:
    with open(args.inputRulesFile) as file:
        tableRules = json.load(file)
    print "Rules loaded from {}..\n".format(args.inputRulesFile)

# db connection
db = MySQLdb.connect(host = args.host, user = args.user, passwd = args.password, db = args.database, port = int(args.port))

# Functions
def processTable(table, rules):
    "Iterates over the rules and fakes the associated fields."
    for rule in rules:
        for column in rules[rule]:
            print "    {}.{}..".format(table, column),
            fakeColumnByRule(table, column, rule)

def fakeColumnByRule(table, column, rule):
    "Fakes a speciffic column based on data rule."
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
    "Fakes an email column."
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

def fakeNames(table, column, type = FIRST_NAME):
    "Fakes a name field."
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
    "Fakes a full name field."
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
    "Fakes a company name field."
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

def fakePasswords(table, column, password = FAKE_PASSWORD):
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
    "Fakes a text field."
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
    "Fakes an address field."
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
    "Nullifies/empties a field."
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
    "Sets a field to a field."
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

# run
for table in tableRules:
    print "Faking {}..".format(table)
    processTable(table, tableRules[table])

db.close()
print "\n[ Done ]"
