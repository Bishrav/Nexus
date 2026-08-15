# NEXUS load-test harness

NEXUS includes a sequential parser load-test command:

```powershell
$env:PYTHONPATH = "src"
python -m nexus load-test --fixture tests/fixtures/python_parser.py --operations 100
```

The command reports raw operation count, successes, failures, and one measured duration per operation. It is a local correctness and repeatability harness, not a concurrency test or a production capacity benchmark.

No throughput, latency target, scalability, or deployment claim is made from this harness. Future comparisons must record the machine, Python version, fixture revision, command, and raw output.
