import juliandate as jd
import re
from seleucid import calc_seleucid_on_data, calc_seleucid_on_prediction


month_names = {
    'CE': {  # start of a year: Jan
        '1': "Jan", '2': "Feb", '3': "Mar",
        '4': "Apr", '5': "May", '6': "Jun",
        '7': "Jul", '8': "Aug", '9': "Sep",
        '10': "Oct", '11': "Nov", '12': "Dec"
    },
    'SE': {  # Macedonian, start of a year: Dîos (Oct)
        '7': "Dîos [I]", '8': "Apellaîos [II]", '9': "Audunaîos [III]",
        '10': "Perítios [IV]", '11':"Dústros [V]", '12': "Xandikós [VI]",
        '1': "Artemī́sios [VII]", '2': "Daísios [VIII]", '3': "Pánēmos [IX]",
        '4': "Lôios [X]", '5': "Gorpiaîos [XI]", '6': "Hyperberetaîos [XII]",
        '12b': "Xandikós Embόlimos [VIb]", '6b': "Hyperberetaîos Embόlimos [XIIb]"
    },
    'SE_': {  # Babylonian, start of a year: Nīsannu (Apr)
        '1': "Nīsannu [I]", '2': "Ayyāru [II]", '3': "Sīmannu [III]",
        '4': "Duʾūzu [IV]", '5': "Ābu [V]", '6': "Ulūlū [VI]",
        '7': "Tašrītu [VII]", '8': "Araḫsamna [VIII]", '9': "Kisilīmu [IX]",
        '10': "Ṭebētu [X]", '11': "Šabāṭu [XI]", '12': "Addāru [XII]",
        '6b': "Ulūlu II [VIb]", '12b': "Addāru II [XIIb]"
    }
}

class JulianDate:
    """
    Chronological Julian Day Number
    """
    def __init__(self, date):
        self.date = None
        if isinstance(date, int):
            self.cjd = date
        elif isinstance(date, str):
            date = self.parse(date)
            self.from_common_era(*date)
        else:
            raise ValueError("Invalid data type for `date`!")

    @staticmethod
    def parse(date):
        date = date.strip().upper()
        is_before_era = re.search('B', date) is not None

        date = re.findall('\d+b?', date)
        assert len(date) in [1, 3], "Invalid date!"
        year, month, day = map(int, date) if len(date) == 3 \
            else map(int, [date[0][:-4], date[0][-4:-2], date[0][-2:]])

        if is_before_era:
            year = 1 - year
        return year, month, day

    @staticmethod
    def ordinal(num):
        if (num - 1) % 10 >= 3 or num // 10 == 1:
            return str(num) + 'th'
        return str(num) + ['st', 'nd', 'rd'][(num - 1) % 10]

    @staticmethod
    def is_prior(date1, date2):
        (year1, month1, day1), (year2, month2, day2) = date1, date2
        if year1 != year2:
            return year1 < year2
        if month1 != month2:
            if isinstance(month1, int):
                return month1 < month2
            elif isinstance(month1, str):
                mark1, mark2 = month1.endswith('b'), month2.endswith('b')
                month1, month2 = int(month1.strip('b')), int(month2.strip('b'))
                if month1 != month2:
                    return month1 < month2
                return not mark1 and mark2
        return day1 < day2

    @classmethod
    def format(cls, date, fmt, month_shift=0):
        if isinstance(fmt, int):
            if fmt == 0:
                fmt = "%Y-%M-%D %E"
            elif fmt == 1:
                fmt = "%M^ %D^, %Y %E"
            elif fmt == 2:
                fmt = "%D^ of %M^, %Y %E"
            else:
                raise ValueError("Invalid preset number!")

        era, year, month, day = date
        month_name = month_names[era][str(month)]
        day_ord = cls.ordinal(day)
        if year <= 0:
            era, year = 'B' + era, 1 - year

        if isinstance(month, int):
            month += month_shift
            while month <= 0:
                year, month = year - 1, month + 12
            while month > 12:
                year, month = year + 1, month - 12
        elif isinstance(month, str):
            mark = 'b' if month.endswith('b') else ''
            month = int(month.strip('b')) + month_shift
            while month <= 0:
                year, month = year - 1, month + 12
            while month > 12:
                year, month = year + 1, month - 12
            month = str(month) + mark

        return fmt.replace("%E", era.strip('_'))\
                  .replace("%M^", month_name) \
                  .replace("%D^", day_ord) \
                  .replace("%Y", str(year))  \
                  .replace("%M", str(month)) \
                  .replace("%D", str(day))

    def from_common_era(self, year, month, day, is_gregorian=None):
        if is_gregorian is None:
            is_gregorian = not self.is_prior((year, month, day), (1582, 10, 15))

        self.cjd = jd.from_gregorian(year, month, day) if is_gregorian \
              else jd.from_julian(year, month, day)
        self.cjd = int(round(self.cjd + .5))

    def to_common_era(self, is_gregorian=None, fmt=None):
        if is_gregorian is None:
            is_gregorian = self.cjd > 2299160  # start from Oct 15th, 1582
        if fmt is None:
            fmt = 1

        self.date = ('CE', *jd.to_gregorian(self.cjd)[:3]) if is_gregorian \
               else ('CE', *jd.to_julian(self.cjd)[:3])
        return self.format(self.date, fmt=fmt)

    def to_seleucid_era(self, fmt=None, is_macedon_reckon=False):
        if fmt is None:
            fmt = 2

        if 1492871 <= self.cjd < 1748872:
            self.date = calc_seleucid_on_data(self.cjd)
        elif self.cjd >= 1748872:
            self.date = calc_seleucid_on_prediction(self.cjd)
        else:
            raise ValueError("Do not support date before Apr 5th, 626 BCE!")

        month_shift = 6 if is_macedon_reckon else 0
        if not is_macedon_reckon:
            self.date = (self.date[0] + '_', *self.date[1:])  # use Babylonian month names
        return self.format(self.date, fmt=fmt, month_shift=month_shift)


if __name__ == '__main__':
    print(JulianDate(1721423).to_common_era())
    print(JulianDate(1721424).to_common_era())
    print(JulianDate(2299160).to_common_era())
    print(JulianDate(2299161).to_common_era())
    print(JulianDate("311-9-25 BCE").to_seleucid_era())
    print(JulianDate("311-9-26 BCE").to_seleucid_era())
    print(JulianDate("311-9-26 BCE").to_seleucid_era(is_macedon_reckon=True))
    print(JulianDate("781-2-4 CE").to_seleucid_era(fmt=0, is_macedon_reckon=True))
