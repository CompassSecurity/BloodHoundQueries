# BloodHound Custom Queries

Here is a simple description of the BloodHound queries in [customqueries.json](customqueries.json).

## Installation

On Linux, you can simply install the queries using this curl command:
```bash
curl -o ~/.config/bloodhound/customqueries.json "https://raw.githubusercontent.com/CompassSecurity/BloodHoundQueries/master/BloodHound_Custom_Queries/customqueries.json"
```

On Windows, you can simply install the queries using this PowerShell command:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/CompassSecurity/BloodHoundQueries/master/BloodHound_Custom_Queries/customqueries.json" -OutFile "$env:USERPROFILE\AppData\Roaming\bloodhound\customqueries.json"
```

## Special Queries

### Shortest Paths from no Signing to ...

Return shortest paths from computers without SMB signing to the Domain.

The computers without signing have to be imported manually with [BloodHound Loader](../BloodHound_Loader).
