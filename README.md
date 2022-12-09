# Advanced BloodHound Usage

This project contains:
* [Custom BloodHound Queries](#custom-bloodhound-queries) we often use to see important things in BloodHound
* [Custom Neo4j Queries](#custom-neo4j-queries) we use to extract data directly from the Neo4j browser console
* [BloodHoundLoader](#bloodhoundloader) script, which allows to make batch modifications to the BloodHound data

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
