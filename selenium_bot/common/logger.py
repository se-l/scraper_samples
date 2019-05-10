import logging

class Logger:
    logger = None

    @staticmethod
    def init_log(output=None):
        """
        Initialise the logger
        """
        Logger.logger = logging.getLogger('patternFinder')
        # Logger.logger.setLevel(logging.ERROR)
        # Logger.logger.setLevel(logging.INFO)
        Logger.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s %(message)s')
        # if output is not None:
        slogger = logging.StreamHandler()
        slogger.setFormatter(formatter)
        Logger.logger.addHandler(slogger)
        # else:
        if output is not None:
            flogger = logging.FileHandler(output)
            flogger.setFormatter(formatter)
            Logger.logger.addHandler(flogger)

    @staticmethod
    def info(str):
        """
        Write info log
        :param method: Method name
        :param str: Log message
        """
        Logger.logger.info('%s' % (str))

    @staticmethod
    def debug(str):
        """
        Write info log
        :param method: Method name
        :param str: Log message
        """
        Logger.logger.debug('%s' % (str))

    @staticmethod
    def error(str):
        """
        Write info log
        :param method: Method name
        :param str: Log message
        """
        Logger.logger.error('%s' % (str))