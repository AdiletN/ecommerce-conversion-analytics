# Power BI Report: Step-by-Step Plan

**Status: Not finished.** The Python analysis, CSV export, and DAX measures are ready. We will make the `.pbix` file together in Power BI Desktop later.

## 1. Prepare the data

Run the Python project with **real** UCI data:

```bash
python -m src.pipeline
```

The file you need is `reports/real/sessions_clean.csv`. Do **not** use the demo CSV: it has fake data.

## 2. Add the file in Power BI Desktop

1. Open Power BI Desktop.
2. Choose **Home → Get data → Text/CSV**.
3. Open `reports/real/sessions_clean.csv`.
4. Select **Load**.
5. Rename the table to **Sessions**.
6. Check types: `revenue`, `weekend`, `month_order`, and `productrelated` should be whole numbers. `month` and `visitortype` are text.
7. For the `month` column, choose **Column tools → Sort by column → month_order**.

## 3. Add the DAX measures

Open `powerbi/measures.dax`. Add each measure using **Modeling → New measure**. Copy only one measure at a time.

We will use:

- Sessions
- Purchase Sessions
- Conversion Rate
- Sessions Without Purchase
- Average Product Pages

`Revenue` means purchase **yes/no**. It is not sales money.

## 4. Make the report page

Suggested title: **Shopping Session Conversion**.

1. Add three **Cards**: Sessions, Purchase Sessions, Conversion Rate.
2. Add a **bar chart**: `visitortype` and Conversion Rate.
3. Add a **column chart**: `product_page_bucket` and Conversion Rate.
4. Add a **column chart**: `month` and Conversion Rate. This is not a year-to-year chart.
5. Add a **table**: `traffictype`, Sessions, Purchase Sessions, Conversion Rate.
6. Add **Slicers**: `month`, `visitortype`, and `weekend`.
7. Format Conversion Rate as a **percentage** with two decimal places.
8. Add a short note: *"These are session patterns, not proof of cause and effect."*

## 5. Check the numbers

With no filters, these are the expected numbers for the real UCI data:

| Measure | Expected value |
| --- | ---: |
| Sessions | 12,330 |
| Purchase Sessions | 1,908 |
| Conversion Rate | 15.47% |

If your numbers do not match, check the CSV path, data types, filters, and measures.

## 6. Save your work

When we finish the report together, save the file as `powerbi/Ecommerce_Conversion_Analytics.pbix` and add a screenshot to the README.

**Do not say that this Power BI report is done before the `.pbix` file has been made and checked.**
