# Decision memo: retail margin

**Scope:** 12,000 synthetic, single-line orders across 2024–2025. Currency: USD. All return outcomes have a full 30-day observation window as of 2026-02-01. These are simulated findings, not employer results.

## What changed

Net revenue was $1,046,442 in 2024 and $974,092 in 2025. Contribution margin moved from 29.5% to 26.3%. The weakest sufficiently populated 2025 cell was **Electronics at 30% discount**: -5.7% margin across 609 orders.

## Proposed decision

Review discount approval rules for negative-contribution category/tier combinations. Run a limited randomized discount test before changing pricing broadly; this observational comparison does not identify price elasticity or causal uplift. Monitor conversion, units, contribution per visitor and 30-day returns together.

## Method

Contribution = gross sales − discounts − refunds − net COGS − shipping − return handling. Returned inventory is assumed fully recoverable at unit cost; markdowns, damaged inventory, advertising, tax and overhead are excluded. This is contribution, not net profit. Rates are ratios of sums, not averages of group percentages. Orders have exactly one product line, so row count equals order count.

The 90-day repeat metric requires a later calendar-date order within 90 days. Customers with incomplete follow-up are excluded; same-day multiple orders do not count as repeat. Acquisition months with small eligible counts are unstable.

## Quality and reconciliation

Raw 12,132 rows → remove 120 exact duplicate order IDs → quarantine 12 negative-quantity rows → 12,000 valid orders. Normalize 24 channel labels. Both dimension joins are many-to-one; orphan counts and the revenue bridge residual equal zero. Quarantine and machine-readable QA are committed.

## Limits and next questions

Patterns are intentionally encoded in a seeded synthetic generator. They demonstrate workflow, not external business evidence. No claim of realized savings is supported. A production study would need payment timing, return dates, inventory recovery, customer acquisition costs and a pricing experiment.
