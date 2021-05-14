#!/usr/bin/env python3
import os, sys, getpass, argparse, requests, urllib3, re, pickle, json
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
        self.__fqdn = urlparse(args.server).hostname
        self.session = requests.Session()

    def _saveCookie(self):
        cookie_file = '%s' % (os.path.sep).join([os.path.expanduser("~"),
                                                 '.RSASecureID_login',
                                                 self.__fqn])
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
        if 'channels' in jsond and not 'rsa://%s' % (self.__args.server) in jsond['channels']:
            conda_api.run_command('config',
                                  '--add',
                                  'channels', 'rsa://%s' % (self.__args.server),
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
        response = self.session.get('https://%s' % (self.__fqdn),
                                    verify=not self.__args.insecure)
        if response.status_code != 200:
            print('ERROR connecting to %s' % (self.__fqdn))
        token = re.findall('name="csrftoken" value="(\w+)', response.text)
        (username, passcode) = self._getCredentials()
        response = self.session.post('https://%s/webauthentication' % (self.__fqdn),
                                     verify=not self.__args.insecure,
                                     data={'csrftoken' : token[0],
                                           'username'  : username,
                                           'passcode'  : passcode})
        if response.status_code != 200:
            print('ERROR authenticating to %s' (self.__args.server))
            sys.exit(1)
        elif not re.search('Authentication Succeeded', response.text):
            print('ERROR authenticating, credentials invalid.')
            sys.exit(1)
        self._saveCookie()
        self._addChannel()

def verifyArgs(parser):
    args = parser.parse_args()
    if not args.server:
        print('You must specify a server to connect to')
        sys.exit(1)
    if args.insecure:
        from urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    return args

def parseArgs():
    parser = argparse.ArgumentParser(description='Create/Update RSA Tokens to specified server')
    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=22, width=90)
    parser.add_argument('-s', '--server', nargs="?",
                        help='RSA protected server containing Conda packages')
    parser.add_argument('-k', '--insecure', action="store_true", default=False,
                        help="Allow untrusted SSL certificates (default: %(default))")
    return verifyArgs(parser)

if __name__ == '__main__':
    args = parseArgs()
    rsaclient = Client(args)
    rsaclient.createConnection()
    sys.exit(0)
