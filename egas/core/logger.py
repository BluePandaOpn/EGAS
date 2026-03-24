import datetime


class Logger:
    """Sistema centralizado de logs del motor."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"

    @classmethod
    def _get_timestamp(cls) -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

    @classmethod
    def info(cls, context: str, message: str):
        print(f"[{cls._get_timestamp()}] {cls.CYAN}[INFO]{cls.RESET} [{context}] {message}")

    @classmethod
    def success(cls, context: str, message: str):
        print(f"[{cls._get_timestamp()}] {cls.GREEN}[SUCCESS]{cls.RESET} [{context}] {message}")

    @classmethod
    def warning(cls, context: str, message: str):
        print(f"[{cls._get_timestamp()}] {cls.YELLOW}[WARNING]{cls.RESET} [{context}] {message}")

    @classmethod
    def error(cls, context: str, message: str):
        print(f"[{cls._get_timestamp()}] {cls.RED}{cls.BOLD}[ERROR]{cls.RESET} [{context}] {message}")

    @classmethod
    def debug(cls, context: str, message: str):
        print(f"[{cls._get_timestamp()}] {cls.MAGENTA}[DEBUG]{cls.RESET} [{context}] {message}")

    @classmethod
    def system(cls, message: str):
        print(f"[{cls._get_timestamp()}] {cls.BOLD}[EGAS SYSTEM]{cls.RESET} {message}")
