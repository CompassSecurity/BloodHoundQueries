#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from importlib import util

if util.find_spec('neo4j') is None:
    print('[-] Neo4j library is not installed, please execute the following before: pip3 install --upgrade neo4j')
    exit()

from neo4j import Auth, GraphDatabase
from neo4j.exceptions import ServiceUnavailable

parser = ArgumentParser(description = 'BloodHoundLoader, tool to set attributes in BloodHound for all the items contained in files', formatter_class = ArgumentDefaultsHelpFormatter)
parser.add_argument('--dburi', dest = 'databaseUri', help = 'Database URI', default = 'bolt://localhost:7687')
parser.add_argument('--dbuser', dest = 'databaseUser', help = 'Database user', default = 'neo4j')
parser.add_argument('--dbpassword', dest = 'databasePassword', help = 'Database password', default = 'BloodHound')
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument('-m', '--mode', dest = 'mode', help = 'Mode, h = set to high value, o = set to owned, s = set to no SMB signing', choices = ['h', 'o', 's'])
group.add_argument('-o', '--operation', dest = 'operation', help = 'Operation to perform if the mode is not set, for instance "highvalue = true"')
parser.add_argument('-c', '--comment', dest = 'comment', help = 'Comment for the log', default = '')
parser.add_argument('-v', '--verbose', dest = 'verbose', help = 'Verbose mode', action = 'store_true')
parser.add_argument('filePaths', nargs = '+', help = 'Paths of files the to import')
arguments = parser.parse_args()

loggingLevel = (logging.DEBUG if arguments.verbose else logging.INFO)

logger = logging.getLogger('BloodHoundLoader')
logger.setLevel(loggingLevel)

consoleLogger = logging.StreamHandler()
consoleLogger.setLevel(loggingLevel)
logger.addHandler(consoleLogger)

logger.debug('[*] Arguments: ' + str(arguments))

if arguments.mode == 'h':
    operation = 'highvalue = true'
elif arguments.mode == 'o':
    operation = 'owned = true'
elif arguments.mode == 's':
    operation = 'hassigning = false'
else:
    operation = arguments.operation

logger.debug('[*] Operation: ' + operation)

try:
    driver = GraphDatabase.driver(arguments.databaseUri, auth = Auth(scheme = 'basic', principal = arguments.databaseUser, credentials = arguments.databasePassword))
    with driver.session() as session:
        for filePath in arguments.filePaths:
            with open(filePath) as file:
                logger.info('[*] Opened file: ' + filePath)

                for line in file:
                    item = line.strip()
                    logger.debug('[*] Current item: ' + item)

                    if item:
                        name = item.upper()

                        log = '(file: ' + filePath + ', comment: ' + arguments.comment + ')'
                        query = 'MATCH (a {name: $name}) SET a.' + operation + ', a.BloodHoundLoaderLog = $log RETURN COUNT(*) AS count'
                        results = session.run(query, name = name, log = log)

                        count = results.single()['count']
                        if count > 0:
                            logger.info('[+] Modified: ' + item)
                            logger.debug('[*] Number of modified entries: ' + str(count))
                            logger.debug('[*] Stored message: ' + log)
                        else:
                            logger.error('[-] Could not modify: ' + item)

except ServiceUnavailable:
    logger.exception('[-] Connection to BloodHound Neo4j database failed')
except Exception:
    logger.exception('[-] Error')
