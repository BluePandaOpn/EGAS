class GOSBaseError(Exception):
    def __init__(self, message: str, line: int | None = None, script_path: str | None = None, function_name: str | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.script_path = script_path
        self.function_name = function_name

    def with_context(self, script_path: str | None = None, function_name: str | None = None):
        return self.__class__(
            self.message,
            line=self.line,
            script_path=script_path or self.script_path,
            function_name=function_name or self.function_name,
        )

    def __str__(self) -> str:
        parts = [self.message]
        if self.script_path:
            parts.append(f"archivo={self.script_path}")
        if self.function_name:
            parts.append(f"funcion={self.function_name}")
        if self.line is not None:
            parts.append(f"linea={self.line}")
        return " | ".join(parts)


class GOSLexerError(GOSBaseError):
    pass


class GOSParserError(GOSBaseError):
    pass


class GOSRuntimeError(GOSBaseError):
    pass


class GOSPropertyError(GOSRuntimeError):
    pass
