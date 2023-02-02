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
group.add_argument('-m', '--mode', dest = 'mode', help = 'Mode, h = set to high value, o = set to owned, s = set to no SMB signing, u = unmark as owned', choices = ['h', 'o', 's', 'u'])
group.add_argument('-o', '--operation', dest = 'operation', help = 'Operation to perform if the mode is not set, for instance "highvalue = true"')
group.add_argument('-e', '--edge', dest = 'edge', help = 'Create the provided edge, file must contain exactly 2 nodes per line, comma separated')
parser.add_argument('-c', '--comment', dest = 'comment', help = 'Comment for the log', default = '')
parser.add_argument('-v', '--verbose', dest = 'verbose', help = 'Verbose mode', action = 'store_true')
parser.add_argument('-b', '--batchsize', dest = 'batchSize', help = 'Number of element to update simultaneously', type = int, default = 10000)
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
elif arguments.mode == 'u':
    operation = 'owned = false'
elif arguments.mode == 's':
    operation = 'hassigning = false'
elif not arguments.edge is None:
    operation = 'edge'
else:
    operation = arguments.operation

logger.debug('[*] Operation: ' + operation)

def handleStandardOperation(filePath, operation, comment, inputSet):
    log = '(file: ' + filePath + ', comment: ' + comment + ', operation: ' + operation + ')'
    query = 'MATCH (b:Base) WHERE b.name IN $inputSet SET b.' + operation + ', b.BloodHoundLoaderLog = $log RETURN b.name AS name'
    results = session.run(query, inputSet = list(inputSet), log = log)

    modifiedSet = set()
    for result in results:
        modifiedSet.add(result['name'])
    errorSet = inputSet - modifiedSet

    modified = len(modifiedSet)
    errors = len(errorSet)
    total = modified + errors
    logger.info('[*] %s%6i%s%6i%s%6i' % ('Modified:', modified, '  Errors:', errors, '  Total:', total))

    if errors > 0:
        logger.debug('[-] Items in error: ' + str(errorSet))

try:
    driver = GraphDatabase.driver(arguments.databaseUri, auth = Auth(scheme = 'basic', principal = arguments.databaseUser, credentials = arguments.databasePassword))
    with driver.session() as session:
        for filePath in arguments.filePaths:
            with open(filePath) as file:
                logger.info('[*] Opened file: ' + filePath)

                if operation == 'edge':
                    for line in file:
                        item = line.strip().split(',')
                        logger.debug('[*] Current item: ' + item[0] + ' ' + item[1])

                        if item[0] and item[1]:
                            source = item[0].upper()
                            destination = item[1].upper()

                            log = '(file: ' + filePath + ', comment: ' + arguments.comment + ')'
                            query = 'MATCH (s),(d) WHERE s.name = "' + source + '" AND d.name = "' + destination + '" CREATE (s)-[r:' + arguments.edge + ']->(d) SET r.BloodHoundLoaderLog = "' + log + '" RETURN COUNT(*) AS count'
                            logger.debug('[*] Query: ' + query)
                            results = session.run(query)

                            count = results.single()['count']
                            if count > 0:
                                logger.info('[+] Created: ' +  source + ' - ' + arguments.edge + ' -> ' + destination)
                                logger.debug('[*] Number of modified entries: ' + str(count))
                                logger.debug('[*] Stored message: ' + log)
                            else:
                                logger.error('[-] Could not create: ' + source + ' - ' + arguments.edge + ' -> ' + destination)

                else:
                    inputSet = set()
                    for line in file:
                        item = line.strip()
                        if item:
                            name = item.upper()
                            inputSet.add(name)

                        if len(inputSet) >= arguments.batchSize:
                            handleStandardOperation(filePath, operation, arguments.comment, inputSet)
                            inputSet = set()

                    if len(inputSet) > 0:
                        handleStandardOperation(filePath, operation, arguments.comment, inputSet)

except ServiceUnavailable:
    logger.exception('[-] Connection to BloodHound Neo4j database failed')
except Exception:
    logger.exception('[-] Error')
