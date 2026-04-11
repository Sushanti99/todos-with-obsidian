from brain.init_vault import initialize_vault


def test_initialize_vault_creates_expected_structure(tmp_path):
    vault_path = tmp_path / "vault"

    result = initialize_vault(vault_path, agent="claude-code")

    assert (vault_path / "daily").exists()
    assert (vault_path / "core").exists()
    assert (vault_path / "references").exists()
    assert (vault_path / "thoughts").exists()
    assert (vault_path / "system" / "brain.config.yaml").exists()
    assert (vault_path / "system" / "CLAUDE.md").exists()
    assert result.folder_mappings["daily_folder"] == "daily"


def test_initialize_vault_preserves_existing_daily_folder_name(tmp_path):
    vault_path = tmp_path / "vault"
    (vault_path / "Daily").mkdir(parents=True)

    result = initialize_vault(vault_path, agent="codex")

    assert result.folder_mappings["daily_folder"] == "Daily"
    assert (vault_path / "Daily").exists()
    assert (vault_path / "system" / "brain.config.yaml").read_text(encoding="utf-8").find("daily_folder: Daily") != -1
