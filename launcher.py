# Description: This is the main file that will be used to launch the application
from api import ParrotAPI
from web.web import ParrotWeb
if __name__ == '__main__':
    PA = ParrotAPI()
    PA.run()
    PW = ParrotWeb()
    PW.run()
    print('API and Web servers started.')