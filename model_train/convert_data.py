import re

headers = "mpg,cylinders,displacement,horsepower,weight,acceleration,model year,origin,car name"
lines = [headers]

with open("dataset/auto-mpg.data", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        match = re.match(
            r'([\d.?]+)\s+([\d.?]+)\s+([\d.?]+)\s+([\d.?]+)\s+([\d.?]+)\s+([\d.?]+)\s+([\d.?]+)\s+([\d.?]+)\s+(.+)',
            line,
        )
        if match:
            vals = list(match.groups())
            vals[-1] = vals[-1].strip('"')
            lines.append(",".join(vals))

with open("dataset/auto-mpg.csv", "w") as f:
    f.write("\n".join(lines))

print(f"Wrote {len(lines)-1} records to dataset/auto-mpg.csv")
