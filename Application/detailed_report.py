import csv
import json
from pathlib import Path
from statistics import mean, median, stdev
from math import isnan

from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
)

EXPORT_DIR = Path(__file__).parent / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("Coin-Afrique", CoinAfriqueAnnouncement),
    ("igoe-immobilier", IgoeAnnouncement),
    ("intendance-tg", IntendanceAnnouncement),
    ("generic", RealEstateAnnouncement),
]

PERCENTILES = [10, 25, 50, 75, 90]


def compute_percentiles(sorted_values, percentiles):
    n = len(sorted_values)
    if n == 0:
        return {p: None for p in percentiles}
    results = {}
    for p in percentiles:
        k = (p / 100) * (n - 1)
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            val = sorted_values[int(k)]
        else:
            d0 = sorted_values[f] * (c - k)
            d1 = sorted_values[c] * (k - f)
            val = d0 + d1
        results[p] = val
    return results


def histogram_bins(values, bins=10):
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if lo == hi:
        # single bucket
        return [(lo, hi, len(values))]
    width = (hi - lo) / bins
    bins_list = [0] * bins
    for v in values:
        # compute bin index
        idx = int((v - lo) / width)
        if idx == bins:
            idx = bins - 1
        bins_list[idx] += 1
    result = []
    for i in range(bins):
        start = lo + i * width
        end = start + width
        result.append((start, end, bins_list[i]))
    return result


def analyze_source(db, model):
    rows = db.query(model).all()
    prices = [r.price_numeric for r in rows if getattr(r, 'price_numeric', None) is not None]
    prices = [float(p) for p in prices]
    prices_sorted = sorted(prices)
    cnt = len(prices)
    if cnt == 0:
        return {
            'count': 0,
            'avg': None,
            'median': None,
            'stdev': None,
            'min': None,
            'max': None,
            'percentiles': {p: None for p in PERCENTILES},
            'histogram': [],
        }
    avg = mean(prices)
    med = median(prices)
    sd = stdev(prices) if cnt > 1 else 0.0
    pcts = compute_percentiles(prices_sorted, PERCENTILES)
    hist = histogram_bins(prices_sorted, bins=10)
    return {
        'count': cnt,
        'avg': avg,
        'median': med,
        'stdev': sd,
        'min': prices_sorted[0],
        'max': prices_sorted[-1],
        'percentiles': pcts,
        'histogram': hist,
    }


def write_summary_csv(summary, path: Path):
    with path.open('w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'source', 'count', 'avg', 'median', 'stdev', 'min', 'max'
        ] + [f'p{p}' for p in PERCENTILES]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for source, data in summary.items():
            row = {
                'source': source,
                'count': data['count'],
                'avg': data['avg'],
                'median': data['median'],
                'stdev': data['stdev'],
                'min': data['min'],
                'max': data['max'],
            }
            for p in PERCENTILES:
                row[f'p{p}'] = data['percentiles'].get(p)
            writer.writerow(row)


def write_histograms(summary, path_dir: Path):
    # CSV histograms and PNG images
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    pdf_path = path_dir / 'histograms.pdf'
    with PdfPages(pdf_path) as pdf:
        for source, data in summary.items():
            hist = data['histogram']
            filename = path_dir / f'histogram_{source.replace(" ", "_")}.csv'
            with filename.open('w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                w.writerow(['bin_start', 'bin_end', 'count'])
                for start, end, cnt in hist:
                    w.writerow([start, end, cnt])

            # draw png and include in pdf
            if hist:
                bins = [ (start+end)/2 for start,end,_ in hist]
                counts = [cnt for _,_,cnt in hist]
                plt.figure()
                plt.bar(bins, counts, width=(hist[0][1]-hist[0][0])*0.9)
                plt.title(f'Histogram of prices - {source}')
                plt.xlabel('Price (CFA)')
                plt.ylabel('Count')
                png_path = path_dir / f'histogram_{source.replace(" ", "_")}.png'
                plt.savefig(png_path)
                pdf.savefig()
                plt.close()
    return pdf_path


def main():
    db = SessionLocal()
    try:
        summary = {}
        for source_name, model in SOURCES:
            analysis = analyze_source(db, model)
            summary[source_name] = analysis

        # Save JSON report
        json_path = EXPORT_DIR / 'detailed_report.json'
        with json_path.open('w', encoding='utf-8') as jf:
            json.dump(summary, jf, ensure_ascii=False, indent=2)

        # Save CSV summary
        csv_path = EXPORT_DIR / 'detailed_report_summary.csv'
        write_summary_csv(summary, csv_path)

        # Save histograms per source
        pdf_path = write_histograms(summary, EXPORT_DIR)

        print('Detailed report generated:')
        print(' -', json_path)
        print(' -', csv_path)
        print(' -', pdf_path)
        for source_name in summary.keys():
            print(' -', EXPORT_DIR / f'histogram_{source_name.replace(" ", "_")}.csv')
            print(' -', EXPORT_DIR / f'histogram_{source_name.replace(" ", "_")}.png')

    finally:
        db.close()


if __name__ == '__main__':
    main()
