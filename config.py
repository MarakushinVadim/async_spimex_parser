import re

LINKS_PATTERN: re.Pattern[str] = re.compile(r"^/files/trades/result/upload/reports/oil_xls/oil_xls_202([543]).*")
