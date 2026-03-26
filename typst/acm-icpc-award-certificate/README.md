# ACM-ICPC Award Certificate Template

Files:
- `template.typ`: reusable certificate template
- `example.typ`: example usage with the CCNU logo

Usage:
1. Install Typst locally.
2. Render the example:
   `typst compile example.typ`
3. Or import `award-certificate` from `template.typ` in your own file.

Notes:
- The current design targets landscape A4.
- The visual language follows the classic ACM-ICPC award certificate style: serif typography, red/gold palette, double border, centered hierarchy.
- `logo-path` is optional. Set it to `none` if you do not want a logo.
