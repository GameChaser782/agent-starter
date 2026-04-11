from agent_starter.tools.builtin.calculator import calculator
from agent_starter.tools.builtin.file_reader import file_reader
from agent_starter.tools.registry import ToolRegistry


def test_calculator_basic():
    assert calculator.invoke({"expression": "2 + 2"}) == "4.0"


def test_calculator_power():
    assert calculator.invoke({"expression": "2 ** 10"}) == "1024.0"


def test_calculator_complex():
    result = calculator.invoke({"expression": "(3 + 4) * 5"})
    assert result == "35.0"


def test_calculator_division():
    result = calculator.invoke({"expression": "10 / 4"})
    assert result == "2.5"


def test_calculator_invalid():
    result = calculator.invoke({"expression": "import os"})
    assert "Error" in result


def test_file_reader_missing(tmp_path):
    result = file_reader.invoke({"path": str(tmp_path / "nonexistent.txt")})
    assert "Error" in result


def test_file_reader_reads(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("Hello, world!")
    result = file_reader.invoke({"path": str(f)})
    assert result == "Hello, world!"


def test_tool_registry():
    ToolRegistry.load_builtins()
    tools = ToolRegistry.get(["calculator", "file_reader"])
    assert len(tools) == 2
    names = [t.name for t in tools]
    assert "calculator" in names
    assert "file_reader" in names


def test_tool_registry_unknown():
    tools = ToolRegistry.get(["nonexistent_tool"])
    assert tools == []
