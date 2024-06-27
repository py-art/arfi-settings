import sys

import pytest
from pytest_mock import MockFixture

from arfi_settings import ArFiBaseReader, ArFiReader, ArFiSettingsError

try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomli
except ImportError:
    tomli = None


@pytest.fixture
def readers():
    from arfi_settings import readers

    readers.tomli = None
    readers.tomllib = None
    yield readers
    readers.tomli = None
    readers.tomllib = None


@pytest.fixture
def readers_tomli_is_not_none():
    from arfi_settings import readers

    readers.import_toml()
    yield readers
    readers.tomli = None
    readers.tomllib = None


@pytest.mark.readers
@pytest.mark.skipif(sys.version_info < (3, 11), reason="requires python3.11+")
def test_import_tomllib(readers):
    assert readers.tomli is None
    assert readers.tomllib is None
    readers.import_toml()
    assert readers.tomllib
    assert readers.tomli is None

    # readers.tomli = "tomli_test"
    # if readers.tomli is not None:
    #     assert readers.import_toml() is None
    #     assert readers.tomli


# @pytest.mark.skipif(sys.version_info >= (3, 11), reason="not need to use tomli")
@pytest.mark.readers
@pytest.mark.skipif(tomli is None, reason="tomli not installed")
def test_import_tomli_and_tomli_installed(mocker: MockFixture, readers):
    mock_sys = mocker.patch("arfi_settings.readers.sys")
    mock_sys.version_info = (3, 10)
    assert readers.tomli is None
    assert readers.tomllib is None
    readers.import_toml()
    assert readers.tomli
    assert readers.tomllib is None

    result = readers.import_toml()
    assert result is None


# @pytest.mark.skipif(sys.version_info >= (3, 11), reason="not need to use tomli")
@pytest.mark.readers
@pytest.mark.skipif(tomli, reason="tomli installed")
def test_import_tomli_and_tomli_not_installed(mocker: MockFixture, readers):
    mock_sys = mocker.patch("arfi_settings.readers.sys")
    mock_sys.version_info = (3, 10)
    assert readers.tomli is None
    assert readers.tomllib is None
    with pytest.raises(ArFiSettingsError) as excinfo:
        readers.import_toml()
    assert "tomli is not installed" in str(excinfo.value)

    readers.tomli = "tomli_test"
    result = readers.import_toml()
    assert result is None
    assert readers.tomli


@pytest.mark.readers
@pytest.mark.skipif(yaml is None, reason="PyYaml not installed")
def test_yaml_installed(mocker: MockFixture):
    from arfi_settings import readers

    # mocker.patch("arfi_settings.readers.yaml", return_value=None)
    # mocker.patch("readers.yaml", return_value=None)
    # assert readers.yaml is None
    readers.import_yaml()
    assert readers.yaml


@pytest.mark.readers
@pytest.mark.skipif(yaml, reason="PyYaml installed")
def test_yaml_not_installed(mocker: MockFixture):
    from arfi_settings import readers

    assert readers.yaml is None
    with pytest.raises(ArFiSettingsError) as excinfo:
        readers.import_yaml()
    assert "PyYaml not installed" in str(excinfo.value)


@pytest.mark.readers
def test_new_class_reader_without_method_read():
    with pytest.raises(TypeError):

        class DummyReader(ArFiBaseReader):
            def custom_reader(self):
                pass

        _ = DummyReader()


# @pytest.mark.current
@pytest.mark.readers
def test_new_class_reader():
    class DummyReader(ArFiReader):
        def read(self):
            pass

    _ = DummyReader()


@pytest.mark.readers
def test_read_without_params():
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader()
        reader.read()
    assert "No sources provided for the reading." in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
def test_read_toml(empty_config_config_toml):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config/config.toml",
    )

    data = reader.read()
    assert data == {}


# @pytest.mark.current
@pytest.mark.readers
def test_read_data_toml(simple_data_config_config_toml):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config/config.toml",
    )
    data = reader.read()
    assert data
    assert data == {"path_config_file": "config/config.toml"}


@pytest.mark.readers
def test_read_cnf_file_without_reader(simple_data_config_cnf):
    ArFiReader.BASE_DIR = None
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config.cnf",
        )
        reader.read()

    assert "`cnf_reader` is not defined" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
def test_read_cnf_file_with_reader(simple_data_config_cnf):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config.cnf",
        reader="toml",
    )
    data = reader.read()
    assert data
    assert data == {"path_config_file": "config.cnf"}


@pytest.mark.readers
def test_custom_reader(simple_data_config_cnf):
    ArFiReader.BASE_DIR = None

    class DummyReader(ArFiReader):
        def cnf_reader(self):
            return self.toml_reader()

    reader = DummyReader(
        file_path="config.cnf",
        reader="cnf",
    )
    data = reader.read()
    assert data
    assert data == {"path_config_file": "config.cnf"}


@pytest.mark.readers
def test_custom_reader_name_without_reader(simple_data_config_cnf):
    ArFiReader.BASE_DIR = None
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config.cnf",
            reader="custom",
        )
        reader.read()
    assert "`custom_reader` is not defined" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
def test_ignore_missing(mocker: MockFixture):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config.toml",
        ignore_missing=True,
    )
    data = reader.read()
    assert data == {}

    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config.toml",
        )
        _ = reader.toml_reader()
    assert "File not found" in str(excinfo.value)

    mock_sys = mocker.patch("arfi_settings.readers.sys")
    mock_sys.version_info = (3, 10)
    reader = ArFiReader(
        file_path="config.toml",
        ignore_missing=True,
    )
    data = reader.toml_reader()
    assert data == {}

    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config.toml",
        )
        _ = reader.toml_reader()
    assert "File not found" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
def test_yaml_reader(simple_data_config_config_yaml):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config/config.yaml",
    )
    data = reader.read()
    assert data
    assert data == {"path_config_file": "config/config.yaml"}


# @pytest.mark.current
@pytest.mark.readers
def test_non_exist_file_yaml_reader():
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config/config.yaml",
        )
        _ = reader.read()
    assert "File not found" in str(excinfo.value)

    reader = ArFiReader(
        file_path="config/config.yaml",
        ignore_missing=True,
    )
    data = reader.read()
    assert data == {}


@pytest.mark.readers
def test_yml_reader(simple_data_config_config_yml):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config/config.yml",
    )
    data = reader.read()
    assert data
    assert data == {"path_config_file": "config/config.yml"}


@pytest.mark.readers
def test_non_exist_file_yml_reader():
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config/config.yml",
        )
        _ = reader.read()

    assert "File not found" in str(excinfo.value)

    reader = ArFiReader(
        file_path="config/config.yml",
        ignore_missing=True,
    )
    data = reader.read()
    assert data == {}


@pytest.mark.readers
def test_json_reader(simple_data_config_config_json):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="config/config.json",
    )
    data = reader.read()
    assert data
    assert data == {"path_config_file": "config/config.json"}


@pytest.mark.readers
def test_non_exist_file_json_reader():
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="config/config.json",
        )
        _ = reader.read()

    assert "File not found" in str(excinfo.value)

    reader = ArFiReader(
        file_path="config/config.json",
        ignore_missing=True,
    )
    data = reader.read()
    assert data == {}


# @pytest.mark.current
@pytest.mark.readers
def test_read_env_file_non_exist(cwd_to_tmp, path_base_dir):
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path=".env",
            is_env_file=True,
        )
        _ = reader.read()
    assert "File not found" in str(excinfo.value)

    reader = ArFiReader(
        file_path=".env",
        is_env_file=True,
        ignore_missing=True,
    )
    data = reader.read()
    assert data == {}


@pytest.mark.readers
def test_read_env_file(simple_data_env_file):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path=".env",
        is_env_file=True,
    )
    data = reader.read()
    assert data
    assert data == {"PATH_CONFIG_FILE": ".env"}


@pytest.mark.readers
def test_read_env(monkeypatch):
    monkeypatch.setenv("PATH_CONFIG_FILE", ".env.prod")
    reader = ArFiReader(
        is_env=True,
    )
    data = reader.read()
    assert data
    assert data["PATH_CONFIG_FILE"] == ".env.prod"


@pytest.mark.readers
@pytest.mark.parametrize(
    "reader_name, error_message",
    [
        (12, "Reader `name` must be not empty string"),
        ("_test_reader", "Reader `name` must not start with `_`"),
    ],
)
def test_normolize_reader_name(reader_name, error_message):
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path=".env",
            is_env_file=True,
            reader=reader_name,
        )
        _ = reader.read()
    assert error_message in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
@pytest.mark.parametrize(
    "bad_file_path",
    ["", 12, ".", "./", "/", "\\\\", {"path"}],
)
def test_validate_file_path(bad_file_path):
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path=bad_file_path,
        )
        _ = reader.read()
    assert "File path is not set or invalid" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
@pytest.mark.parametrize(
    "file_path, resp",
    [
        (123, False),
        ("config/config.toml", True),
        ("config", False),
        (None, False),
        ("config/config.yaml", False),
        ({"asd", 123}, False),
    ],
)
def test_is_exist_file(empty_config_config_toml, file_path, resp):
    ArFiReader.BASE_DIR = None
    result = ArFiReader.is_exist_file(file_path)
    assert result == resp


# @pytest.mark.current
@pytest.mark.readers
def test_empty_param():
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(ignore_missing=False)
        _ = reader.read()
    assert "No sources provided for the reading" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.readers
def test_file_without_ext_and_without_reader():
    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(file_path="config", ignore_missing=True)
        _ = reader.read()
    assert "No reader provided for file" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.secret
@pytest.mark.readers
def test_non_exist_secret_file(secrets_dir):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="secrets/path_config_file",
        ignore_missing=True,
        is_secret_file=True,
    )
    data = reader.read()
    assert data == {}

    with pytest.raises(ArFiSettingsError) as excinfo:
        reader = ArFiReader(
            file_path="secrets/path_config_file",
            is_secret_file=True,
        )
        _ = reader.read()
    assert "File not found" in str(excinfo.value)


# @pytest.mark.current
@pytest.mark.secret
@pytest.mark.readers
def test_empty_secret_file(empty_secret_path_config_file):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="secrets/path_config_file",
        is_secret_file=True,
    )
    data = reader.read()
    assert data == {"path_config_file": ""}


# @pytest.mark.current
@pytest.mark.secret
@pytest.mark.readers
def test_secret_file_with_data(simple_data_secret_path_config_file):
    ArFiReader.BASE_DIR = None
    reader = ArFiReader(
        file_path="secrets/path_config_file",
        is_secret_file=True,
    )
    data = reader.read()
    assert data == {"path_config_file": "secrets/path_config_file"}


# @pytest.mark.current
@pytest.mark.cli
@pytest.mark.readers
def test_setup_cli_reader():
    def parse_args():
        return ["test_key", "test_value"]

    with pytest.raises(ArFiSettingsError) as excinfo:
        ArFiReader.setup_cli_reader(parse_args)
        reader = ArFiReader(is_cli=True)
        _ = reader.read()
    assert "CLI reader must return a dict" in str(excinfo.value)

    def parse_args():
        return {"test_key": "test_value"}

    with pytest.raises(ArFiSettingsError) as excinfo:
        cli_reader = parse_args()
        ArFiReader.setup_cli_reader(cli_reader)
    assert "`cli_reader` must be callable" in str(excinfo.value)

    ArFiReader.setup_cli_reader(parse_args)
    reader = ArFiReader(is_cli=True)
    data = reader.read()
    assert data == {"test_key": "test_value"}

    def parse_args(*args):
        return {"test_key": "test_value"}

    ArFiReader.setup_cli_reader(parse_args)
    reader = ArFiReader(is_cli=True)
    data = reader.read()
    assert data == {"test_key": "test_value"}

    def parse_args(*args, **kwargs):
        return {"test_key": "test_value"}

    ArFiReader.setup_cli_reader(parse_args)
    reader = ArFiReader(is_cli=True)
    data = reader.read()
    assert data == {"test_key": "test_value"}

    def parse_args(test_value=25, asd=38):
        assert test_value == 25
        assert asd == 38
        return {"test_key": "test_value"}

    ArFiReader.setup_cli_reader(parse_args)
    reader = ArFiReader(is_cli=True)
    data = reader.read()
    assert data == {"test_key": "test_value"}

    class ParseArgs:
        def __call__(self):
            return {"test_key": "test_value"}

    cli_reader = ParseArgs()
    ArFiReader.setup_cli_reader(cli_reader)
    assert isinstance(ArFiReader.default_cli_reader, ParseArgs)
    reader = ArFiReader(is_cli=True)
    data = reader.read()
    assert data == {"test_key": "test_value"}


# @pytest.mark.current
@pytest.mark.cli
@pytest.mark.readers
def test_reader_whithout_default(monkeypatch):
    monkeypatch.setattr(ArFiReader, "default_cli_reader", None)
    reader = ArFiReader(is_cli=True)
    data = reader.read()
    assert data == {}
