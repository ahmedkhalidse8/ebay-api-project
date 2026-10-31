"""
Synthetic A/B experiment demonstration.
These are simulated data, NOT results from a real eBay experiment.
"""

import numpy as np
from scipy.stats import norm

# Reproducible simulated experiment
rng = np.random.default_rng(42)

visitors_per_group = 10_000
control_rate = 0.020
treatment_rate = 0.025

control_conversions = rng.binomial(
    visitors_per_group, control_rate
)
treatment_conversions = rng.binomial(
    visitors_per_group, treatment_rate
)

# Observed conversion rates
p_control = control_conversions / visitors_per_group
p_treatment = treatment_conversions / visitors_per_group

difference = p_treatment - p_control
relative_lift = (
    difference / p_control if p_control > 0 else float("nan")
)

# Two-proportion z-test under the null hypothesis
pooled_rate = (
    control_conversions + treatment_conversions
) / (2 * visitors_per_group)

standard_error_null = np.sqrt(
    pooled_rate * (1 - pooled_rate)
    * (2 / visitors_per_group)
)

z_score = difference / standard_error_null
p_value = 2 * norm.sf(abs(z_score))

# Approximate 95% confidence interval for the rate difference
standard_error_ci = np.sqrt(
    p_control * (1 - p_control) / visitors_per_group
    + p_treatment * (1 - p_treatment) / visitors_per_group
)

margin = norm.ppf(0.975) * standard_error_ci
ci_lower = difference - margin
ci_upper = difference + margin

print("SYNTHETIC EXPERIMENT — NOT REAL EBAY RESULTS")
print(f"Visitors per group: {visitors_per_group:,}")
print(f"Control conversions: {control_conversions:,}")
print(f"Treatment conversions: {treatment_conversions:,}")
print(f"Control conversion rate: {p_control:.2%}")
print(f"Treatment conversion rate: {p_treatment:.2%}")
print(f"Absolute difference: {difference:.2%}")
print(f"Relative lift: {relative_lift:.2%}")
print(f"95% CI for difference: [{ci_lower:.2%}, {ci_upper:.2%}]")
print(f"Two-sided p-value: {p_value:.6f}")
print(f"Statistically significant at 5%: {p_value < 0.05}")

import csv
from pathlib import Path

output_path = Path("processed/experiment_results.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "data_type",
            "visitors_per_group",
            "control_conversions",
            "treatment_conversions",
            "control_rate",
            "treatment_rate",
            "absolute_difference",
            "relative_lift",
            "ci_95_lower",
            "ci_95_upper",
            "p_value",
            "significant_at_5_pct",
        ],
    )
    writer.writeheader()
    writer.writerow({
        "data_type": "synthetic",
        "visitors_per_group": visitors_per_group,
        "control_conversions": control_conversions,
        "treatment_conversions": treatment_conversions,
        "control_rate": p_control,
        "treatment_rate": p_treatment,
        "absolute_difference": difference,
        "relative_lift": relative_lift,
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "p_value": p_value,
        "significant_at_5_pct": p_value < 0.05,
    })

print(f"Saved synthetic results to {output_path}")