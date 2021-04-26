from lemur_conf import JsonFormatter, LOG_CONFIG_DICT
from logging.config import dictConfig
from flower.command import FlowerCommand
from flower.utils import bugreport


def main():
    dictConfig(LOG_CONFIG_DICT)
    try:
        flower = FlowerCommand()
        flower.execute_from_commandline()
    except Exception:
        import sys
        print(bugreport(app=flower.app), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
