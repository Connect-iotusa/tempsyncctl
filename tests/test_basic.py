from subprocess import run, PIPE
import sys, json

def run_ok(cmd):
    r = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def test_version_cmd():
    out = run_ok([sys.executable, "-m", "tempsyncctl.cli", "version"])
    assert "0.1.0" in out

def test_validate_sample_ok(tmp_path):
    sample = {
        "site": "Embassy Row",
        "units": 10,
        "thermostats": 8,
        "api_base": "https://example.com",
        "api_token": "XYZ"
    }
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps(sample))
    out = run_ok([sys.executable, "-m", "tempsyncctl.cli", "validate", "--path", str(cfg)])
    assert "Config is valid" in out
