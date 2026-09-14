# ADR 0005: Power BI is the BI surface; Fabric is optional

## Status

Accepted.

## Decision

Power BI consumes the documented star schema through source-controlled DAX/theme/relationship
assets. The local platform remains Docker/open-source first. Microsoft Fabric is a separately
documented deployment mapping, not a runtime prerequisite.

## Rationale

This makes the portfolio project accessible without paid cloud access while preserving a credible
enterprise translation to Eventstream, Eventhouse, Lakehouse/OneLake, Direct Lake, and Real-Time
Dashboards. PBIX files are not fabricated; Desktop/PBIP validation is explicitly manual.
