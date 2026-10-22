"""Print a one-line Markdown summary of a pytest JUnit XML report."""

import os
import sys
import xml.etree.ElementTree as ET

title, path = sys.argv[1], sys.argv[2]
if not os.path.exists(path):
    print(f"### {title}: no report (tests did not run)")
    sys.exit(0)
root = ET.parse(path).getroot()
suite = root if root.tag == "testsuite" else root.find("testsuite")
print(
    f"### {title}: {suite.get('tests')} run, {suite.get('failures')} failed, "
    f"{suite.get('errors')} errors, {suite.get('skipped')} skipped"
)
