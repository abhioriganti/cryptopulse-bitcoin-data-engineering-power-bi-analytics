# CryptoPulse Power BI semantic model

CryptoPulse ships source-controlled semantic-model assets, not a fabricated `.pbix` file. Build the
report in Power BI Desktop after the local platform has loaded Gold/serving data.

## Model source and storage mode

Use PostgreSQL database `cryptopulse` as the local source. Import the dbt relations from schema
`cryptopulse_analytics` and the operational tables from schema `raw`. Import mode is recommended
for the local demonstration; configure scheduled refresh or a gateway only when deploying outside
your workstation.

The central fact table is `cryptopulse_analytics.fact_market_bar`, at provider + asset + interval +
bar-start grain. Use the one-minute interval for near-live charts and `mart_market_hourly` for
longer ranges. See [semantic_model/RELATIONSHIPS.md](semantic_model/RELATIONSHIPS.md) for the
star schema.

## Manual Desktop setup

1. In Power BI Desktop, enable the Power BI Project (`.pbip`) preview feature if it is available in
   your Desktop release, then create and save a new project beneath `powerbi/`.
2. Select **Get data → PostgreSQL database**. Server: `localhost:15432`, database: `cryptopulse`.
   Authenticate using values from your local `.env`; never embed credentials in the report.
3. Import `dim_asset`, `dim_provider`, `dim_date`, `fact_market_bar`, `mart_market_hourly`,
   `mart_data_quality`, `raw.forecasts`, and `raw.anomalies`.
4. Rename imported tables to the display names used in
   [dax/CryptoPulseMeasures.dax](dax/CryptoPulseMeasures.dax), create the relationships listed in
   `semantic_model/RELATIONSHIPS.md`, and mark `Dim Date[Date]` as the date table.
5. Apply [theme/cryptopulse.json](theme/cryptopulse.json). Add the measures from the DAX script to
   a dedicated `Measures` table and place them in the specified display folders.
6. Create the report pages described below. Save the generated `.pbip` project; do not commit a
   `.pbix` export or credentials.

## Report pages

| Page | Primary visuals |
|---|---|
| Executive Market Overview | latest price/returns/volume/freshness cards; price, return and volume trends |
| Real-Time Market Monitor | one-minute bars, VWAP, rolling volatility, anomalies and volume spikes |
| Historical Analysis | moving averages, drawdown, calendar comparisons and period slicers |
| Volatility & Risk | realized volatility, return distribution, drawdown and statistical anomalies |
| Forecasting | actual-vs-predicted, model comparison, MAE/RMSE and forecast error |
| Data Quality & Reliability | reconciliation outcomes, freshness, rejected-record and quality pass indicators |
| Data Engineering Operations | run history, processing lag, records and failures when operational telemetry is modeled |

Use `Dim Date` and `Dim Asset` slicers on analytic pages. Configure drill-through on Date, use a
tooltip page for bar-level OHLC/VWAP, and label anomaly visuals as *statistical anomaly; not
investment advice*.

## TMDL

The DAX and model contract are intentionally separated from a generated PBIP because Desktop GUI
actions cannot be executed here. `tmdl/MEASURES.tmdl` is a source-control-friendly measure
fragment. Paste or adapt it into the PBIP semantic-model definition after completing the manual
source connection. Confirm the generated TMDL with your installed Power BI Desktop version before
committing it.
