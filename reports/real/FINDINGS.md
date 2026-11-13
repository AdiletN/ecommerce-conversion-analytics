# Business Findings: E-commerce Conversion

**Data:** UCI Online Shoppers Purchasing Intention Dataset, 12,330 sessions.

## 1. Business question

An online store wants more people to finish a purchase. I studied session data to find groups with different conversion rates and suggest what the store should check next.

A **conversion** means that a session ended in a purchase. We do not have order prices or total sales.

## 2. Main numbers

| Metric | Value |
| --- | ---: |
| All sessions | 12,330 |
| Purchase sessions | 1,908 |
| Sessions without a purchase | 10,422 |
| Purchase conversion rate | 15.47% |

Conversion rate = purchase sessions / all sessions × 100.

## 3. What I found

### Finding A: New and returning visitors are different

| Visitor group | Sessions | Conversion |
| --- | ---: | ---: |
| New visitors | 1,694 | 24.91% |
| Returning visitors | 10,551 | 13.93% |
| Other | 85 | 18.82% |

New visitors had a **10.98 percentage-point higher** conversion rate. Returning visitors made up about **85.6%** of all sessions.

**Why it matters:** The returning group is large. A small improvement here could matter, but the dataset cannot tell us what would cause that improvement.

**What to check:** Compare traffic sources within each visitor group. The new SQL query `sql/06_visitor_traffic.sql` helps with this first step. Next, ask for data about product search, carts, and checkout steps.

### Finding B: More product pages are linked with more purchases

- Sessions with **30 or more** product pages: about **23%** conversion.
- Sessions with **1–4** product pages: about **4%** conversion.

**Why it matters:** People who look at more products may be more interested in buying. It does not mean that making people open more pages will increase sales.

**What to check:** Product search, filters, and navigation. Look at users' needs before choosing a change.

### Finding C: Traffic groups have different results

- Traffic Type 2: about **21.6%** conversion.
- Traffic Type 3: about **8.8%** conversion.

**Why it matters:** Some traffic groups may bring more interested visitors. The dataset gives traffic type numbers, not the names of marketing channels.

**What to check:** Find out what each traffic type means before making marketing changes. Compare sample sizes. Small groups can give unreliable rates.

### Finding D: Month differences need care

November had about **25%** conversion in the saved analysis. But the data gives month names without years. We cannot call this annual growth or a long-term trend.

## 4. Statistics

I used a **chi-square test** to compare new and returning visitor sessions.

- **p-value:** 3.87 × 10⁻³¹.
- **Conversion gap:** 10.98 percentage points (new minus returning).
- **Approximate 95% confidence interval** for returning minus new: **[-13.14, -8.82] percentage points**.

The p-value is much smaller than 0.05. This supports a link between visitor type and conversion in this data. It **does not** explain the reason. No users were randomly assigned to groups, so this was **not an A/B test**.

## 5. What the business can do next

| Step | Action | What to measure |
| --- | --- | --- |
| 1 | Check which traffic types returning visitors use | Sessions, conversion by visitor and traffic type |
| 2 | Get more data about search, cart, and checkout steps | Drop-off at each shopping step |
| 3 | Choose one simple change based on the new data | One main goal: purchase conversion |
| 4 | Test the change with randomly assigned users | Conversion for test group vs control group |

**Example hypothesis (not a proven result):** Better product search could help returning visitors find products faster. A future A/B test could check this.

I prepared code to estimate the sample size of a future A/B test. The project did **not** run an actual experiment.

## 6. Limits

- `Revenue` is a yes/no purchase flag, not money. I cannot find profit or order value.
- There are no full dates or order IDs. I cannot calculate customer retention or repeat-purchase value.
- Months do not include years.
- Visitor type, page views, and traffic may be linked with purchases, but a link is not proof of cause.
- Some traffic groups are small. They need more data for a stable comparison.
- Checkout events are not in this dataset. I cannot say that checkout problems caused the visitor gap.

## 7. Data source

Sakar, C. & Kastro, Y. (2018). [Online Shoppers Purchasing Intention Dataset](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset), UCI Machine Learning Repository. [DOI 10.24432/C5F88Q](https://doi.org/10.24432/C5F88Q). CC BY 4.0.

*This is my analysis of a public education dataset, not a report from a real company.*
