# NEXUS parser evaluation

The evaluation runner compares normalized Python parser output with checked-in golden data:

```powershell
$env:PYTHONPATH = "src"
python -m nexus evaluate `
  --fixture tests/evaluation/python_basic.py `
  --expected tests/evaluation/python_basic.json
```

The command emits JSON and returns exit code `0` only when status, symbols, and relationships match the expected case. A mismatch returns exit code `1` and identifies the differing sections.

Golden cases are correctness evidence for the specific fixtures they contain. They are not a claim of language completeness, parser accuracy across all Python projects, or production coverage.
