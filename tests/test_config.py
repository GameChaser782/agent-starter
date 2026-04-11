from agent_starter.config import AgentConfig, load_config


def test_defaults():
    cfg = AgentConfig()
    assert cfg.model_provider == "ollama"
    assert cfg.model_name == "llama3.2"
    assert cfg.long_term_memory is True


def test_load_config_defaults(tmp_path):
    """load_config with no YAML file returns sane defaults."""
    cfg = load_config("nonexistent", config_dir=str(tmp_path))
    assert cfg.name == "nonexistent"
    assert cfg.model_provider == "ollama"


def test_load_config_yaml(tmp_path):
    yaml_content = """
name: test
model:
  provider: openai
  name: gpt-4o
  temperature: 0.3
tools:
  - calculator
"""
    (tmp_path / "test.yaml").write_text(yaml_content)
    cfg = load_config("test", config_dir=str(tmp_path))
    assert cfg.name == "test"
    assert cfg.model_provider == "openai"
    assert cfg.model_name == "gpt-4o"
    assert cfg.temperature == 0.3
    assert "calculator" in cfg.tools


def test_load_config_persona(tmp_path):
    (tmp_path / "test.yaml").write_text("name: test\npersona: test_persona.md\n")
    (tmp_path / "test_persona.md").write_text("You are a test agent.")
    cfg = load_config("test", config_dir=str(tmp_path))
    assert cfg.persona_text == "You are a test agent."
