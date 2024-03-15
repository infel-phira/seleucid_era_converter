from datetime import datetime
from converter import JulianDate

if __name__ == '__main__':
    today = datetime.now().strftime("%Y-%m-%d CE")
    today = JulianDate(today)  # [New Year] 2335-1-1 SE = 2024-4-11 CE !!

    print("\nCommon Era                         :  {}\t({})"
          .format(today.to_common_era(fmt=0),
                  today.to_common_era()))
    print("Chronological Julian Day Number    :  {}".format(today.cjd))
    print("Seleucid Era (Babylonian Reckoning):  {}\t({})"
          .format(today.to_seleucid_era(fmt=0),
                  today.to_seleucid_era()))
    print("Seleucid Era (Macedonian Reckoning):  {}\t({})"
          .format(today.to_seleucid_era(fmt=0, is_macedon_reckon=True),
                  today.to_seleucid_era(is_macedon_reckon=True)))

    print("\nNote: Inferred lunation after Feb 25th, 76 CE, with possible error of ±1 day.")
