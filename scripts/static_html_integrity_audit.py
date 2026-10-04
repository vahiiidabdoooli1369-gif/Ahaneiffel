from pathlib import Path
import re
import sys

errors=[]
checked=0
for path in Path(".").rglob("*.html"):
    if ".git" in path.parts: continue
    text=path.read_text(encoding="utf-8",errors="ignore")
    checked+=1
    if len(re.findall(r"<html\\b",text,re.I))!=1: errors.append(f"{path}: expected exactly one <html> element")
    if len(re.findall(r"<head\\b",text,re.I))!=1: errors.append(f"{path}: expected exactly one <head> element")
    if len(re.findall(r"<body\\b",text,re.I))!=1: errors.append(f"{path}: expected exactly one <body> element")
    end=re.search(r"</html\\s*>",text,re.I)
    if end and text[end.end():].strip(): errors.append(f"{path}: content exists after </html>")
    if "<head" in text.lower() and not re.search(r'<link[^>]+rel=["\\\']canonical["\\\']',text,re.I): errors.append(f"{path}: missing canonical link")
print(f"HTML integrity audit: {checked} HTML files checked")
if errors:
    for error in errors[:300]: print("ERROR",error)
    sys.exit(1)
print("PASS: no structural HTML integrity errors detected.")
