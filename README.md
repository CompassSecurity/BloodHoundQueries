# Advanced BloodHound Usage

This project contains:
* [Custom BloodHound Queries](#custom-bloodhound-queries) we often use to see important things in BloodHound
* [Custom Neo4j Queries](#custom-neo4j-queries) we use to extract data directly from the Neo4j browser console
* [BloodHoundLoader](#bloodhoundloader) script, which allows to make batch modifications to the BloodHound data

## Custom BloodHound Queries
Here is a simple description of the BloodHound queries in [customqueries.json](customqueries.json).

On Linux, you can simply install the queries using this curl command:
```
$ curl -o "~/.config/bloodhound/customqueries.json" "https://raw.githubusercontent.com/CompassSecurity/BloodHoundQueries/master/customqueries.json"
```

On Windows, you can simply install the queries using this PowerShell command:
```
PS C:\> Invoke-WebRequest -Uri "https://raw.githubusercontent.com/CompassSecurity/BloodHoundQueries/master/customqueries.json" -OutFile "$env:USERPROFILE\AppData\Roaming\bloodhound\customqueries.json"
```

### Information Gathering
#### Domains
Return all domains.

#### Domain Controllers
Return members of the Domain Controllers group for a chosen domain.

#### High Value Targets
Return all targets that have been marked as High Value.

#### Computers without LAPS
Return all the computers without LAPS for a chosen domain.

#### Owned Principals
Return all the principals that have been marked as Owned.

#### Sensitive Principals by Keywords
Return all principals whose name or description contains keywords like "admin" or "secret"  for a chosen domain.

### Accounts
#### Users with Password in AD
Return all the users with a password in the AD object for a chosen domain. The password can then be read in the Node Info.

#### Users with "Pass" in AD Description
Return all the users with the string "pass" in their description for a chosen domain. This might indicate a password or password hint.

#### Users with Password not Required
Return all the users with the password not being required and that can therefore be blank for a chosen domain.

#### Users with Password never Expiring
Return all the users with the password never expiring for a chosen domain.

#### Users with with Same Name in Different Domains
Return all the users that have the same name and are in different Domains, the password could be reused.

### Privileged Accounts
#### Protected Users
Return all principals in the "Protected Users" group for a chosen domain. This group protects users against several attacks.

#### AdminTo Relationships
Return all relationships where one object is admin to another for a chosen domain.

#### Administrators
Return all members of the "Administrators" group for a chosen domain.

#### Computers in Administrators
Return all the computers members of "Administrators" for a chosen domain.

This can be exploited by triggering an SMB connection from this computer to the attacker's computer and relaying it to any computer in the domain in order to gain local administrative privileges. The reason is that Domain Admins are local administrators of every computer in the domain.

Requirements:
* Domain account
* Print spooler service on the source computer active, or another way of triggering an outgoing connection
* No SMB signing on the target computer or a working RPC attack
* No firewall blocking the connection from the source computer to the attacker
* No firewall blocking SMB/RPC from the attacker to the target computer

#### Computers Local Admin to Another Computer
Return all the computers for a chosen domain that are local administrators to another computer.

This can be exploited by triggering an SMB connection from the first computer to the attacker's computer and relaying it to the other computer in order to gain local administrative privileges.

Requirements:
* Domain account
* Print spooler service on the source computer active, or another way of triggering an outgoing connection
* No SMB signing on the target computer or a working RPC attack
* No firewall blocking the connection from the source computer to the attacker
* No firewall blocking SMB/RPC from the attacker to the target computer

#### Sessions of Administrators on non DCs Computers
Return sessions of members of the Administrators group on computers which are not member of the Domain Controllers group for a chosen domain.

These session should be investigated as they break the tiering principle and could lead to privilege escalation.

#### DCSync Principals not Administrators
Return principals allowed to perform DCSync and not already being Administrators for a chosen domain.

### Kerberos
#### AS-REP Roastable Principals
Return principals for a chosen domain that don't require pre-authentication. These can be AS-REP-roasted.

#### Kerberoastable Principals
Return principals for a chosen domain that have an SPN. These can be kerberoasted.

#### Kerberoastable Administrators
Return principals in the Administrators group of a chosen domain that have an SPN. These can be kerberoasted.

#### Constrained Delegations
Return principals for a chosen domain allowed to perform Constrained Delegation and their target.

#### Constrained Delegations with Protocol Transition (trustedToAuth)
Return principals for a chosen domain allowed to perform Constrained Delegation with Protocol Transition and their target.

#### Computers Allowed to Delegate for Another Computer
Return computers for a chosen domain allowed to perform Constrained Delegation with their target.

#### Unconstrained Delegation Principals
Return principals for a chosen domain allowed to perform Unconstrained Delegation (source: https://twitter.com/_wald0/status/1108660095800479744).

Similar to the pre-built query "Shortest Paths to Unconstrained Delegation Systems", except that the Domain Controllers and the Administrators are excluded.

In order to exploit it, use the Unconstrained Delegation with the corresponding account:
* https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/
* https://blog.netspi.com/machineaccountquota-is-useful-sometimes/
* https://adsecurity.org/?p=1667
* https://blog.redxorblue.com/2019/12/no-shells-required-using-impacket-to.html

### Group Policies
#### Interesting GPOs by Keyword
Find GPOs with interesting keywords (password, antivirus, etc.).

#### GPO Permissions of Non-Admin Principals
Find principals for a chosen domain with permissions (ACLs) on GPOs, excluding members of the Administrators group.

### DACL Abuse
#### LAPS Passwords Readable by Non-Admin
Return GenericAll rights (also group-delegated) of principals excluding Administrators. This allows reading the LAPS password `ms-Mcs-AdmPwd`.

#### LAPS Passwords Readable by Owned Principals
Return GenericAll rights (also group-delegated) of all owned principals. This allows reading the LAPS password `ms-Mcs-AdmPwd`.

#### ACLs to Computers (excluding High Value Targets)
Return all the users with an ACL to a computer, except the ones marked as High Value.

In order to exploit it, use the Resource-Based Constrained Delegation with the corresponding account:
* https://posts.specterops.io/a-case-study-in-wagging-the-dog-computer-takeover-2bcb7f94c783
* https://www.harmj0y.net/blog/redteaming/another-word-on-delegation/
* https://dirkjanm.io/worst-of-both-worlds-ntlm-relaying-and-kerberos-delegation/

#### Group Delegated Outbound Object Control of Owned Principals
Return Outbound Object Control (also group-delegated) of all owned principals.

#### Dangerous Rights for Groups under Domain Users
Find groups under Domain Users which have dangerous (ACLs) privileges over other objects.

Similar to the pre-built query "Find Dangerous Rights for Domain Users Groups", except that it includes groups nested under Domain Users.

### Adding High-Value Targets
#### Set DCSync Principals as High Value Targets
Mark all the principals with DCSync rights as High Value.

#### Set Unconstrained Delegation Principals as High Value Targets
Mark all the principals with Unconstrained Delegation privileges as High Value.

#### Set Local Admin or Reset Password Principals as High Value Targets
Mark all the principals that are local administrators or that can reset passwords as High Value.

#### Set Principals with Privileges on Computers as High Value Targets
Mark all the principals with certain privileges on computers as High Value.

#### Set Principals with Privileges on Cert Publishers as High Value Targets
Mark all the principals with certain privileges on the Cert Publishers group as High Value.

#### Set Members of High Value Targets Groups as High Value Targets
Mark all the members of High Value groups as High Value.

#### Remove Inactive Users and Computers from High Value Targets
Unmark the inactive users (disabled) and computers (disabled or no login during the last 6 months) as High Value.

### Shortest Paths
#### Shortest Paths to Domain (including Computers)
Return all the shortest paths to the Domain, including the Computers.

Similar to the pre-built query "Find Shortest Paths to Domain Admins", except that it includes not only the users but the computers as start nodes and targets the Domain instead of Domain Admins.

#### Shortest Paths to no LAPS
Return all the shortest paths to computers without LAPS installed.

Handy in environments where LAPS is deployed on almost every computer in order to find the ones without it, attack them and possibly reuse local administrator passwords.

#### Shortest Paths from Kerberoastable Users to Computers
Return all the shortest paths from the kerberoastable users to computers.

Similar to the pre-built query "Shortest Paths from Kerberoastable Users", except that the user doesn't have to be selected individually.

#### Shortest Paths from Kerberoastable Users to High Value Targets
Return all the shortest paths from the kerberoastable users to targets marked as High Value.

#### Shortest Paths from Owned Principals (including everything)
Return all the shortest paths from any principal marked as Owned to anything (users, computers, groups...).

Similar to the pre-built query "Shortest Path from Owned Principals", except that the user doesn't have to be selected individually and displays the paths to everything, not every to computers.

#### Shortest Paths from Owned Principals to Domain
Return all the shortest paths from any principal marked as Owned to the Domain.

#### Shortest Paths from Owned Principals to High Value Targets
Return all the shortest paths from any principal marked as Owned to targets marked as High Value.

#### Shortest Paths from Owned Principals to no LAPS
Return all the shortest paths from any principal marked as Owned to computers without LAPS.

Handy in environments where LAPS is deployed on almost every computer in order to find the ones without it, attack them and possibly reuse local administrator passwords.

#### Shortest Paths from no Signing to Domain
Return all the shortest paths from computers without SMB signing to the Domain.

Handy in environments where SMB signing is enforced on almost every computer in order to find the ones without it, attack them and possibly reuse local administrator passwords.

The computers without signing have to be imported manually with [BloodHoundLoader.py](BloodHoundLoader.py).

#### Shortest Paths from no Signing to High Value Targets
Return all the shortest paths from computers without SMB signing to targets marked as High Value.

Handy in environments where SMB signing is enforced on almost every computer in order to target them specifically.

The computers without signing have to be imported manually with [BloodHoundLoader.py](BloodHoundLoader.py).

#### Shortest Paths from Domain Users and Domain Computers (including everything)
Return all the shortest paths from the Domain Users and Domain Computers to anything (users, computers, groups...).

### Active Directory Certificate Services (AD CS)
The AD CS queries come from [ly4k](https://github.com/ly4k/Certipy/blob/main/customqueries.json) and are to be used in conjunction with [Certipy](https://github.com/ly4k/Certipy).

### Azure
The Azure queries come from [haus3c](https://hausec.com/2020/11/23/azurehound-cypher-cheatsheet/) and are to be used in conjuction with [AzureHound](https://github.com/BloodHoundAD/AzureHound)

## Custom Neo4j Queries
The following queries are to be used in Neo4j Browser directly (by default http://localhost:7474/browser/).

### LAPS
Show how many computers have LAPS enabled and disabled:
```
MATCH (c:Computer) RETURN c.haslaps, COUNT(*)
```

### Local Administrators
In certain cases, the groups being local administrators are added locally on the computer and not deployed via GPO. In that case, the "AdminTo" edges are not visible in BloodHound.

If the naming convention allows it, it is possible to find which group has access to which computer and to add the corresponding edges.

First of all, search for all the groups containing the name of a computer and lists the mapping:
```
MATCH (g:Group), (c:Computer) WHERE g.name =~ (".*" + replace(c.name, ("." + c.domain), (".*" + "@" + c.domain))) RETURN g.name AS Group, c.name AS Computer
```

If result is similar to this, you might be lucky and be able to add several new edges to your BloodHound:
```
Group                                   Computer
PREFIX_COMPUTER1_SUFFIX@DOMAIN.LOCAL    COMPUTER1.DOMAIN.LOCAL
PREFIX_COMPUTER2_SUFFIX@DOMAIN.LOCAL    COMPUTER2.DOMAIN.LOCAL
PREFIX_COMPUTER3_SUFFIX@DOMAIN.LOCAL    COMPUTER3.DOMAIN.LOCAL
```

In order to create the new the edges according to the naming convention, you can use the following query where you have to replace the "PREFIX_" and "_SUFFIX" according to the results above:
```
MATCH (g:Group), (c:Computer) WHERE g.name =~ ("PREFIX_" + replace(c.name, ("." + c.domain), ("_SUFFIX" + "@" + c.domain))) CREATE (g)-[r:AdminTo]->(c) RETURN g.name AS Group, c.name AS Computer
```

## BloodHoundLoader
[BloodHoundLoader.py](BloodHoundLoader.py) is a tool to set the value of an attribute in BloodHound (e.g. high value, owned...) for all the items contained in a file.

It should be used with Python 3 and with the Neo4j module installed since it is run directly against the Neo4j database:
```
pip3 install --upgrade neo4j
```

Set all the computers in the file "high_value.txt" to high value targets:
```
python3 BloodHoundLoader.py --dburi bolt://localhost:7687 --dbuser neo4j --dbpassword BloodHound --mode h high_value.txt
```

Set all the computers in the file "owned.txt" to owned principals:
```
python3 BloodHoundLoader.py --mode o owned.txt
```

Set all the computers in the file "no_smb_signing.txt" to "hassigning = false", in order to use them with the queries "All Shortest Paths from no Signing to *":
```
python3 BloodHoundLoader.py --mode s no_smb_signing.txt
```

The names of users and computers in the text file should correspond to the text shown on the GUI, e.g.:
```
DC.ACME.COM
COMPUTER.ACME.COM
GUEST@ACME.COM
```

Create new AdminTo edges based on the tuples in the file "adminto.txt":
```
python3 BloodHoundLoader.py --edge AdminTo adminto.txt
```

The names tuples in the text file must be comma separated and ordered (source,destination):
```
DOMAIN ADMINS@ACME.COM,DC.ACME.COM
SERVER ADMINS@ACME.COM,COMPUTER1.ACME.COM
EDWARD.NIGMA@ACME.COM,RIDDLE.ACME.COM
```

Full help:
```
python3 BloodHoundLoader.py --help
usage: BloodHoundLoader.py [-h] [--dburi DATABASEURI] [--dbuser DATABASEUSER] [--dbpassword DATABASEPASSWORD] (-m {h,o,s} | -o OPERATION) [-c COMMENT] [-v] filePaths [filePaths ...]

BloodHoundLoader, tool to set attributes in BloodHound for all the items contained in files

positional arguments:
  filePaths             Paths of files the to import

optional arguments:
  -h, --help            show this help message and exit
  --dburi DATABASEURI   Database URI (default: bolt://localhost:7687)
  --dbuser DATABASEUSER
                        Database user (default: neo4j)
  --dbpassword DATABASEPASSWORD
                        Database password (default: BloodHound)
  -m {h,o,s}, --mode {h,o,s}
                        Mode, h = set to high value, o = set to owned, s = set to no SMB signing, u = umark as owned (default: None)
  -o OPERATION, --operation OPERATION
                        Operation to perform if the mode is not set, for instance "highvalue = true" (default: None)
  -e EDGE, --edge EDGE
                        Create the provided edge, file must contain exactly 2 nodes per line, comma separated (default: None)
  -c COMMENT, --comment COMMENT
                        Comment for the log (default: )
  -v, --verbose         Verbose mode (default: False)
```

## References
BloodHound pre-built queries:
* https://github.com/BloodHoundAD/BloodHound/blob/master/src/components/SearchContainer/Tabs/PrebuiltQueries.json

Introduction to Cypher query language:
* https://blog.cptjesus.com/posts/introtocypher

Cypher cheat sheet:
* https://github.com/SadProcessor/Cheats/blob/master/DogWhispererV2.md

Cypher queries collection:
* https://hausec.com/2019/09/09/bloodhound-cypher-cheatsheet/
* https://github.com/mgeeky/Penetration-Testing-Tools/blob/master/red-teaming/bloodhound/Handy-BloodHound-Cypher-Queries.md
