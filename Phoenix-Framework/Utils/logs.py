import logging
logging.basicConfig(filename='phoenix.log',
                    encoding='utf-8', level=logging.ERROR)
# disable flask logging
logging.getLogger('werkzeug').disabled = True
