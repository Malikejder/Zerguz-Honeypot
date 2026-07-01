# main.py

from core.engine import ZerguzEngine


def main() -> None:
    """
    Application entry point.
    """

    engine = ZerguzEngine()
    engine.run()


if __name__ == "__main__":
    main()

