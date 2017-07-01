# dbfaker
A database faker tool for MySQL/MariaDB.
The purpose of this tool is to fake sensitive data in database. This procedure is done when preparing production databases for development usage.

## Installation
**Note:** Instructions for Ubuntu 16.04

1. `apt install python`
2. `apt install libmysqlclient-dev`
3. `pip install MySQL-python Faker`

## Usage

All available options:

    dbfaker.py -h

Generate sample rules file:

    dbfaker.py -grf

Fake database:

    dbfaker.py -H 127.0.0.1 -u myuser -p 'secret' -d mydatabase

### Faking rules

## Benchmarks
vv bn
