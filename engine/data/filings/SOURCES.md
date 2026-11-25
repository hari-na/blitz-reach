# Where the filings came from

The PDFs themselves are not committed. They are third-party documents and run to
17 MB. Re-download them with the commands below and the citations in
`data/companies/*.yaml` will line up page for page.

All three are FY2025-26 annual reports as filed with BSE.

```bash
cd data/filings
curl -L -o india-cements-fy2026.pdf "https://www.bseindia.com/xml-data/corpfiling/AttachHis/7c127e93-ce6f-45a9-98d5-efee5deb8b54.pdf"
curl -L -o seshasayee-paper-fy2026.pdf "https://www.bseindia.com/xml-data/corpfiling/AttachHis/5d2b7918-7cb1-4e32-8288-1fb4aa72842c.pdf"
curl -L -o lmw-fy2026.pdf "https://www.bseindia.com/xml-data/corpfiling/AttachHis/e099fa0a-ca8f-485e-8721-a19249883779.pdf"
```

| File | Company | BSE scrip | NSE symbol | Pages | Size |
|---|---|---|---|---|---|
| `india-cements-fy2026.pdf` | The India Cements Limited | 530005 | INDIACEM | 266 | 2.4 MB |
| `seshasayee-paper-fy2026.pdf` | Seshasayee Paper and Boards Limited | 502450 | SESHAPAPER | 324 | 5.5 MB |
| `lmw-fy2026.pdf` | LMW Limited (formerly Lakshmi Machine Works) | 500252 | LMW | 152 | 9.3 MB |

If a BSE link has rotated, each company's page on screener.in lists its annual
reports by year with direct links to the same BSE copies.

## A note on page numbers

The company files cite printed page numbers, which are not PDF page numbers.

- India Cements: PDF page is 3 higher than printed, throughout.
- LMW: laid out two printed pages per PDF page, so both are cited.
- Seshasayee: PDF pages only, since the printed numbering restarts by section.

`tools/peek.py` reports PDF pages. Read the printed number off the page itself
when adding a citation.
