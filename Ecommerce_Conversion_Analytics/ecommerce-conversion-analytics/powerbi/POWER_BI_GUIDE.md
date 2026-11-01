# Rebuild the Power BI report (optional)

This repository includes a **Power BI import guide and DAX measures**, not a `.pbix` file.

1. Run `python -m src.pipeline` to generate **real** results.
2. Open Power BI Desktop → **Get Data → Text/CSV**.
3. Import `reports/real/sessions_clean.csv` and name the table `Sessions`.
4. Ensure `revenue`, `weekend`, `month_order`, `productrelated` are numeric.
5. Create the measures in `measures.dax`, one by one (Power BI's **New measure**).
6. Add three KPI cards: `Sessions`, `Purchases`, `Conversion Rate`.
7. Add a column chart: Axis `visitortype`, Value `Conversion Rate`.
8. Add a line chart: Axis `month`, Value `Conversion Rate`. **Sort Month by month_order** (Column tools).
9. Add a matrix: Rows `traffictype`, Values `Sessions`, `Purchases`, `Conversion Rate`.
10. Add slicers: `month`, `visitortype`, `weekend`. Format conversion as `%`.

**Important:** `Revenue` is a purchase indicator; the dataset has no money amounts. Do not create sales/profit/AOV cards. These metrics are observational and should not be presented as A/B results.
