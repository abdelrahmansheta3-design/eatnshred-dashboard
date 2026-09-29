#!/usr/bin/env python3
"""Turn Grubtech "order item sales" exports into the dashboard's encrypted data file.

The repository is public, so sales data is only ever committed encrypted:
gzip -> AES-256-GCM, key from the dashboard password with PBKDF2-SHA256.
The dashboard asks for that password once per device and decrypts in the browser.

Usage
  DASH_PASSWORD='...' python3 tools/build_data.py export1.xlsx [export2.xlsx ...] [--file-password 5555]
  DASH_PASSWORD='...' python3 tools/build_data.py --check

New exports are merged into the data already published: an order that appears in a
new file replaces the old copy, so sending overlapping date ranges is safe.
Use --replace to start from the new files only.

Needs: pip install openpyxl cryptography msoffcrypto-tool
"""
import argparse, base64, datetime as dt, gzip, io, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'sales.enc.json')
ITER = 600_000
COLS = ['Unique Order ID', 'Date', 'Menu Item', 'Qty', 'Total(Receipt Total)', 'Channel',
        'Modifier', 'Item Total Sales Amount', 'Gross Price', 'Discount']
ORDER, DATE = 0, 1


def derive(password, salt):
    import hashlib
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITER, 32)


def encrypt(payload, password, salt):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    iv = os.urandom(12)
    ct = AESGCM(derive(password, salt)).encrypt(iv, gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9), None)
    b = lambda x: base64.b64encode(x).decode()
    return {'v': 1, 'kdf': 'PBKDF2-SHA256', 'iter': ITER, 'salt': b(salt), 'iv': b(iv), 'ct': b(ct),
            'updated': dt.datetime.now(dt.timezone(dt.timedelta(hours=4))).strftime('%Y-%m-%d %H:%M')}


def decrypt(doc, password):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    d = lambda k: base64.b64decode(doc[k])
    try:
        pt = AESGCM(derive(password, d('salt'))).decrypt(d('iv'), d('ct'), None)
    except InvalidTag:
        sys.exit('Wrong dashboard password for the existing data file.')
    return json.loads(gzip.decompress(pt))


def read_export(path, file_password):
    import openpyxl
    raw = open(path, 'rb').read()
    if raw[:4] == b'\xd0\xcf\x11\xe0':
        import msoffcrypto
        f = msoffcrypto.OfficeFile(io.BytesIO(raw))
        if f.is_encrypted():
            if not file_password:
                sys.exit(f'{path} is password-protected: pass --file-password')
            f.load_key(password=file_password)
            buf = io.BytesIO(); f.decrypt(buf); raw = buf.getvalue()
    ws = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True)
    for head in it:
        if head and 'Unique Order ID' in head and 'Menu Item' in head:
            break
    else:
        sys.exit(f'{path}: not a Grubtech order item sales export (no "Unique Order ID" / "Menu Item" columns)')
    idx = [list(head).index(c) if c in head else None for c in COLS]
    rows = []
    for r in it:
        if not r or r[idx[ORDER]] in (None, ''):
            continue
        row = []
        for c, i in zip(COLS, idx):
            v = r[i] if i is not None else None
            if isinstance(v, dt.datetime):
                v = v.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(v, float) and v.is_integer():
                v = int(v)
            row.append('' if v is None else v)
        row[ORDER] = str(row[ORDER])
        rows.append(row)
    return rows


def merge(old_rows, new_rows):
    new_ids = {r[ORDER] for r in new_rows}
    kept = [r for r in old_rows if r[ORDER] not in new_ids]
    return sorted(kept + new_rows, key=lambda r: (str(r[DATE]), r[ORDER]))


def summary(p):
    rows = p['rows']
    orders = {r[ORDER]: r for r in rows}
    dates = sorted(str(r[DATE]) for r in orders.values())
    by_month = Counter(d[:7] for d in dates)
    print(f"{len(orders):,} orders, {len(rows):,} rows, {dates[0][:10]} to {dates[-1][:16]}")
    print('  by month:', ', '.join(f'{m}: {n}' for m, n in sorted(by_month.items())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='*')
    ap.add_argument('--file-password', default=os.environ.get('GRUBTECH_FILE_PASSWORD', ''))
    ap.add_argument('--replace', action='store_true', help='ignore the data already published')
    ap.add_argument('--check', action='store_true', help='decrypt the published file and print a summary')
    a = ap.parse_args()
    pw = os.environ.get('DASH_PASSWORD')
    if not pw:
        sys.exit('Set DASH_PASSWORD (the dashboard password).')
    existing = json.load(open(OUT)) if os.path.exists(OUT) else None
    old = decrypt(existing, pw) if existing and not a.replace else None
    if a.check:
        if not old:
            sys.exit('No data file yet.')
        summary(old); return
    if not a.files:
        sys.exit('Give at least one export file.')
    new_rows = []
    for f in a.files:
        rows = read_export(f, a.file_password)
        print(f'{os.path.basename(f)}: {len(rows):,} rows')
        new_rows += rows
    rows = merge(old['rows'] if old else [], new_rows)
    payload = {'v': 1, 'source': 'Grubtech order item sales', 'headers': COLS, 'rows': rows}
    salt = base64.b64decode(existing['salt']) if existing and not a.replace else os.urandom(16)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = encrypt(payload, pw, salt)
    json.dump(doc, open(OUT, 'w'), separators=(',', ':'))
    summary(payload)
    print(f'wrote {os.path.relpath(OUT)} ({os.path.getsize(OUT) / 1024:.0f} KB)')


if __name__ == '__main__':
    main()
