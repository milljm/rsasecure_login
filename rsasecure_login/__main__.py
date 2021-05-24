#!/usr/bin/env python3
import os
import sys
import getpass
import argparse
import requests
import urllib3
import re
import pickle
import json
from urllib.parse import urlparse
import logging
logging.getLogger(requests.packages.urllib3.__package__).setLevel(logging.ERROR)

try:
    import conda.cli.python_api as conda_api
except:
    print('Unable to import Conda API. Please install conda: `conda install conda`')
    sys.exit(1)

class Client:
    def __init__(self, args):
        self.__args = args
        self.session = requests.Session()

    def _saveCookie(self):
        cookie_file = '%s' % (os.path.sep).join([os.path.expanduser("~"),
                                                 '.RSASecureID_login',
                                                 self.__args.fqdn])
        if not os.path.exists(os.path.dirname(cookie_file)):
            try:
                os.makedirs(os.path.dirname(cookie_file))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        with open(cookie_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def _addChannel(self):
        channels = conda_api.run_command('config',
                                         '--show',
                                         'channels',
                                         '--json')
        jsond = json.loads(channels[0])
        if 'channels' in jsond and not self.__args.server in jsond['channels']:
            conda_api.run_command('config',
                                  '--add',
                                  'channels', self.__args.uri,
                                  stdout=sys.stdout,
                                  stderr=sys.stderr)

        if self.__args.insecure:
            conda_api.run_command('config',
                                  '--set',
                                  'ssl_verify', '%s' % (not self.__args.insecure),
                                  stdout=sys.stdout,
                                  stderr=sys.stderr)

    def _getCredentials(self):
        try:
            username = input('Username: ')
            passcode = getpass.getpass('PIN+TOKEN: ')
        except KeyboardInterrupt:
            sys.exit(1)
        return (username, passcode)

    def createConnection(self):
        try:
            response = self.session.get('https://%s' % (self.__args.fqdn), verify=not self.__args.insecure)
            if response.status_code != 200:
                print('ERROR connecting to %s' % (self.__args.fqdn))
                sys.exit(1)
            token = re.findall('name="csrftoken" value="(\w+)', response.text)
            (username, passcode) = self._getCredentials()
            response = self.session.post('https://%s/webauthentication' % (self.__args.fqdn),
                                         verify=not self.__args.insecure,
                                         data={'csrftoken' : token[0],
                                               'username'  : username,
                                               'passcode'  : passcode})
            if response.status_code != 200:
                print('ERROR authenticating to %s' % (self.__args.fqdn))
                sys.exit(1)
            elif not re.search('Authentication Succeeded', response.text):
                print('ERROR authenticating, credentials invalid.')
                sys.exit(1)
            self._saveCookie()
            self._addChannel()
            return

        except requests.exceptions.ConnectTimeout:
            print('Unable to establish a connection to: https://%s' % (self.__args.fqdn))
        except (requests.exceptions.ProxyError,
                urllib3.exceptions.ProxySchemeUnknown,
                urllib3.exceptions.NewConnectionError):
            print('Proxy information incorrect: %s' % (os.getenv('https_proxy')))
        except requests.exceptions.SSLError:
            print('Unable to establish a secure connection.',
                  'If you trust this server, you can use --insecure')
        except ValueError:
            print('Unable to determine SOCKS version from https_proxy',
                  'environment variable')
        except requests.exceptions.ConnectionError as e:
            print('General error connecting to server: https://%s' % (self.__args.fqdn))
        sys.exit(1)

def verifyArgs(args, parser):
    if not args.server:
        print('You must specify a URI to secure Conda channel')
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif '//' in args.server or len(args.server.split('/')) != 2:
        print('Invalid URI prefix. Please provide only a hostname/channel',
              '\nExample:\n\tserver.com/channel')
        sys.exit(1)

    if args.insecure:
        from urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    args.fqdn = urlparse('https://%s' % (args.server)).hostname
    args.uri = 'rsa://%s' % (args.server)
    return args

def parseArgs(argv=None):
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=22, width=90)
    parser = argparse.ArgumentParser(description='Create/Update RSA Tokens to specified server',
                                     formatter_class=formatter)
    parser.add_argument('-s', '--server', nargs="?",
                        help=('RSA protected server URI containing Conda packages.'
                              ' Example: server.com/channel'))
    parser.add_argument('-k', '--insecure', action="store_true", default=False,
                        help=('Allow untrusted connections. Note: Due to conda channel'
                              ' limitation, all channels will be untrusted.'))
    args = parser.parse_args(argv)
    return verifyArgs(args, parser)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parseArgs(argv)
    rsaclient = Client(args)
    rsaclient.createConnection()

if __name__ == '__main__':
    main()
