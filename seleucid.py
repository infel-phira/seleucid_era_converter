import juliandate as jd
import re
from lunation_predictor import analyze


def calc_seleucid_on_data(cjd, fname='data/babylonian_chronology_pd_1971.dat'):
    with open(fname, 'r') as file:
        data = file.readlines()

    data = [re.findall('-?\d+b?', d)[:5] for d in data]
    data = [(*d[:2], int(round(jd.from_julian(*map(int, d[2:])) + .5))) for d in data]

    for cur, nxt in zip(data, data[1:]):
        if cur[2] <= cjd < nxt[2]:
            return 'SE', int(cur[0]), cur[1], cjd - cur[2] + 1

    raise ValueError("Unable to find valid month!")


def next_month(year, month):
    if year % 19 == 18 and month == '6':
        return year, '6b'
    if year % 19 in [1, 4, 7, 9, 12, 15] and month == '12':
        return year, '12b'
    month = int(month.strip('b')) + 1
    if month > 12:
        year, month = year + 1, month - 12
    return year, str(month)


def calc_seleucid_on_prediction(cjd, start=8584):
    predictor = analyze()

    year, month = 380, '1'
    cur, nxt = predictor(start), None

    while True:
        nxt = predictor(start + 19 * 12 + 7)
        if nxt <= cjd:
            start += 19 * 12 + 7
            year += 19
            cur = nxt
            continue

        nxt = predictor(start + 1)
        if nxt <= cjd:
            start += 1
            year, month = next_month(year, month)
            cur = nxt
            continue

        return 'SE', year, month, cjd - cur + 1
