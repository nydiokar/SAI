# Symmetry Validity Gate Summary

- sample_n: 126792
- alignment_rate: 0.9992
- primary_tolerance: 0.5
- primary_exact_label_match_rate: 0.9027
- primary_order_match_rate: 0.8934
- primary_coarse_label_match_rate: 0.9964
- primary_coarse_order_match_rate: 0.9975
- primary_rho_current: 0.104221
- primary_rho_trusted: 0.094325
- primary_rho_delta: 0.009896
- tol_order_stability_rate: 1.0000
- tol_coarse_stability_rate: 1.0000
- practical_gate_pass: True
- gate_pass: False

## Criteria
- alignment_rate >= 0.98
- order_match_rate >= 0.95
- exact_label_match_rate >= 0.85
- abs(rho_trusted - rho_current) <= 0.02
- direction unchanged (rho_current * rho_trusted >= 0)
- tolerance order stability >= 0.95