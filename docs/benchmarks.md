# NEXUS benchmark harness

The benchmark command measures the existing Python parser against a checked-in fixture:

```powershell
$env:PYTHONPATH = "src"
python -m nexus benchmark --fixture tests/fixtures/python_parser.py --iterations 10
```

The JSON output includes the fixture path, iteration count, extracted symbol/relationship counts, and measured duration for each iteration. The harness is reproducible in workload and output shape, but durations depend on the machine, Python version, background load, and environment.

No benchmark numbers are committed or claimed by the project. Future performance comparisons must record the exact command, environment, fixture revision, and raw observations.
