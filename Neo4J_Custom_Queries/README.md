# Custom Neo4j Queries

## Introduction

The following queries are to be used in Neo4j Browser directly (by default http://localhost:7474/browser/).

## Queries

### LAPS

Show how many computers have LAPS enabled and disabled:
```cypher
MATCH (c:Computer) RETURN c.haslaps, COUNT(*)
```

### Local Administrators

In certain cases, the groups being local administrators are added locally on the computer and not deployed via GPO. In that case, the "AdminTo" edges are not visible in BloodHound.

If the naming convention allows it, it is possible to find which group has access to which computer and to add the corresponding edges.

First of all, search for all the groups containing the name of a computer and lists the mapping:

``cypher
MATCH (g:Group), (c:Computer) WHERE g.name =~ (".*" + replace(c.name, ("." + c.domain), (".*" + "@" + c.domain))) RETURN g.name AS Group, c.name AS Computer
```

If result is similar to this, you might be lucky and be able to add several new edges to your BloodHound:
``cypher
Group                                   Computer
PREFIX_COMPUTER1_SUFFIX@DOMAIN.LOCAL    COMPUTER1.DOMAIN.LOCAL
PREFIX_COMPUTER2_SUFFIX@DOMAIN.LOCAL    COMPUTER2.DOMAIN.LOCAL
PREFIX_COMPUTER3_SUFFIX@DOMAIN.LOCAL    COMPUTER3.DOMAIN.LOCAL
```

In order to create the new the edges according to the naming convention, you can use the following query where you have to replace the "PREFIX_" and "_SUFFIX" according to the results above:
``cypher
MATCH (g:Group), (c:Computer) WHERE g.name =~ ("PREFIX_" + replace(c.name, ("." + c.domain), ("_SUFFIX" + "@" + c.domain))) CREATE (g)-[r:AdminTo]->(c) RETURN g.name AS Group, c.name AS Computer
```
