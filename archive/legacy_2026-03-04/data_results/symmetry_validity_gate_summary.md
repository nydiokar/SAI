# Symmetry Validity Gate Summary

- sample_n: 10000
- alignment_rate: 0.9992
- primary_tolerance: 0.5
- primary_exact_label_match_rate: 0.9020
- primary_order_match_rate: 0.8955
- primary_coarse_label_match_rate: 0.9952
- primary_coarse_order_match_rate: 0.9965
- primary_rho_current: 0.106340
- primary_rho_trusted: 0.095467
- primary_rho_delta: 0.010873
- tol_order_stability_rate: 0.9068
- tol_coarse_stability_rate: 0.9949
- practical_gate_pass: True
- gate_pass: False

## Criteria
- alignment_rate >= 0.98
- order_match_rate >= 0.95
- exact_label_match_rate >= 0.85
- abs(rho_trusted - rho_current) <= 0.02
- direction unchanged (rho_current * rho_trusted >= 0)
- tolerance order stability >= 0.95