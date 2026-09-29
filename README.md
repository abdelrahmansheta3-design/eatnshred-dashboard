# EAT N' SHRED dashboard

Sales and customers dashboard for EAT N' SHRED. Upload an orders export from Grubtech (or Talabat, Deliveroo, Careem) and see, for today, this week or the last 30 days:

- **Key numbers:** orders, average order value, new customers, returning customers, customers who ordered 2+ times — each compared with the previous period.
- **Menu:** the most ordered dish, the top 5, and the items that are falling, with a suggested action for each.
- **Customers:** new vs returning over the last 8 weeks, how many new customers come back, and how many regulars stopped ordering.
- **What to do this week:** suggestions built from your own numbers, to grow current customers and attract new ones (download the lapsed-customer list, copy an offer or ad idea).

## Privacy

This repository is public, so sales data is only ever committed **encrypted**: `data/sales.enc.json` is gzip + AES-256-GCM, with the key derived from the dashboard password (PBKDF2-SHA256, 600,000 rounds). The password is never stored in the repository. The dashboard asks for it once per device, decrypts in the browser, and remembers the key on that device ("Lock this device" under Uploads forgets it).

Files opened with **Upload export** are read on that device only and never leave it. Never commit export files or customer lists (`.gitignore` blocks `.csv` and `.xlsx`).

## Updating the shared data

Send the new Grubtech *order item sales* export (any date range; overlapping ranges are fine) and run:

```
pip install openpyxl cryptography msoffcrypto-tool
DASH_PASSWORD='<dashboard password>' python3 tools/build_data.py path/to/export.xlsx --file-password <export password>
git add data/sales.enc.json && git commit -m "Update sales data" && git push
```

New orders are merged into the published data; an order that appears again replaces its old copy. `--check` prints what the published file contains, `--replace` rebuilds it from the given files only. Keep the same dashboard password so devices stay unlocked.

## Using it

1. Open the dashboard link (GitHub Pages, below).
2. Click **Upload export** and choose the Excel or CSV file. You can select several files at once.
3. Check the columns under **Uploads**. They are detected automatically; fix any that are wrong and click **Apply columns**.

**Grubtech:** use Sales → Orders → download, the *order item sales* export. It's recognised automatically, including add-ons and discounts. Password-protected exports open in the browser: enter the export password once and it's remembered on that device.

For the customer numbers, the export needs a column that identifies the customer (phone or customer ID) and ideally 3 months of orders, so first-time customers can be told apart from returning ones. Grubtech's export for app orders has no customer column, so the dashboard shows a platform breakdown instead.

**Try it first:** click **Try with sample data**, or download a sample file from the Uploads section to see the expected format.

## Turning on the link (GitHub Pages)

1. In this repository go to **Settings → Pages**.
2. Under **Build and deployment**, set Source to **Deploy from a branch**, Branch to **main**, folder **/ (root)**, then **Save**.
3. After a minute the link appears at the top of that page: `https://abdelrahmansheta3-design.github.io/eatnshred-dashboard/`

## Files

- `index.html` — the whole dashboard (layout, styles and logic in one file). The greeting name is set in `CONFIG` at the top of the script.
