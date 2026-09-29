# EAT N' SHRED dashboard

Sales and customers dashboard for EAT N' SHRED. Upload an orders export from Grubtech (or Talabat, Deliveroo, Careem) and see, for today, this week or the last 30 days:

- **Key numbers:** orders, average order value, new customers, returning customers, customers who ordered 2+ times — each compared with the previous period.
- **Menu:** the most ordered dish, the top 5, and the items that are falling, with a suggested action for each.
- **Customers:** new vs returning over the last 8 weeks, how many new customers come back, and how many regulars stopped ordering.
- **What to do this week:** suggestions built from your own numbers, to grow current customers and attract new ones (download the lapsed-customer list, copy an offer or ad idea).

## Privacy

Everything runs in the browser. Export files are read on your device and are never uploaded to GitHub or anywhere else. The last upload is remembered on that device only. Never commit export files to this repository (`.gitignore` blocks `.csv` and `.xlsx`).

## Using it

1. Open the dashboard link (GitHub Pages, below).
2. Click **Upload export** and choose the Excel or CSV file. You can select several files at once.
3. Check the columns under **Uploads**. They are detected automatically; fix any that are wrong and click **Apply columns**.

For the customer numbers, the export needs a column that identifies the customer (phone or customer ID) and ideally 3 months of orders, so first-time customers can be told apart from returning ones.

**Try it first:** click **Try with sample data**, or download a sample file from the Uploads section to see the expected format.

## Turning on the link (GitHub Pages)

1. In this repository go to **Settings → Pages**.
2. Under **Build and deployment**, set Source to **Deploy from a branch**, Branch to **main**, folder **/ (root)**, then **Save**.
3. After a minute the link appears at the top of that page: `https://abdelrahmansheta3-design.github.io/eatnshred-dashboard/`

## Files

- `index.html` — the whole dashboard (layout, styles and logic in one file). The greeting name is set in `CONFIG` at the top of the script.
