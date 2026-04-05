import csv

clean_rows = []
with open('crops_data.csv', 'r', encoding='utf-8', errors='ignore') as infile:
    reader = csv.reader(infile)
    for row in reader:
        if len(row) >= 7:  
            clean_rows.append(row[:7])

with open('clean_crops.csv', 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(clean_rows)
