param(
  [ValidateSet("setup","test","lint","run:summary")]
  [string]$Task = "setup"
)

switch ($Task) {
  "setup" { pip install -e . pytest; break }
  "test"  { pytest -q; break }
  "lint"  { Write-Host "Add ruff/flake8 if desired"; break }
  "run:summary" { tempsyncctl summary -p .\config.json; break }
}
