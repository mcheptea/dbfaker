# dbfaker
A database faker tool for MySQL/MariaDB.
The purpose of this tool is to fake sensitive data in database. This procedure is done when preparing production databases for development usage.

## Installation
**Note:** Instructions for Ubuntu 16.04

1. `apt install python`
2. `apt install libmysqlclient-dev`
3. `apt install python-pip`
4. `pip install MySQL-python Faker`

## Usage

All available options:

    dbfaker.py -h

Generate sample rules file:

    dbfaker.py -grf

Fake database:

    dbfaker.py -H 127.0.0.1 -u myuser -p 'secret' -d mydatabase -irf rules.json

### Faking rules
The tool uses a json `rules` file to fake the database. The rules file contains a list of tables, columns and faking rules for them.
The json hierarchy is the following `table -> rule -> columns`.

You can generate a sample rules file using the `-grf` option. Example:

    dbfaker.py -grf

**Supported Rules:**

* `_email` - replaces the column value with a uniquely generated e-mail address
* `_password` - replaces the values with a default password (*default: 1234qwer*). Note: All rows get the same value
* `_first_name` - replaces the value with generated first names
* `_last_name`- replaces the value with a generated last names
* `_full_name`- replaces the value with a generated full names
* `_text`- replaces the value with a generated lipsum text. Note: All rows get the same value
* `_address` - replaces the value with a generated address. Note: All rows get the same value
* `_empty_string` - empties the column (*sets an empty string*)
* `_company_name` - replaces the value with generated company names
* `_zeroed` - sets column to disabled (zero), useful for boolean columns (tinyint)

**Example:**

    {
      "table_1": {
          "_email": [
              "emailColumn"
          ],
          "_password": [
              "passwordColumn"
          ]
      },
      "table_2": {
          "_address": [
              "addressColumn"
          ],
          "_full_name": [
              "nameColumn"
          ]
      }
    }


### Synchronize rules
The tool uses a jon `synchronize` file to keep some fields synchronized in the database.
The synchronize file contains list of tables, list of columns and synchronization tables with their columns.

You can generate a sample synchronize file using the `-grs` option. Example:

    dbfaker.py -grs
    
**Supported cases**

* Single INNER Join - Can be used to synchronize fields in different tables that have column with common value
* Multiple INNER Joins - Can be used to synchronize fields in 2 or more table that can be joined and should have synchronized single column with base table
* Concatenated Column - For case of the generated values, columns from one table can be concatenated with space character

**Example:**

    {
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
