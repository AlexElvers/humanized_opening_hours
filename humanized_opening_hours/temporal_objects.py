from enum import Enum
import datetime
import pytz
from exceptions import SolarHoursNotSetError
from collections import OrderedDict

WEEKDAYS = (
    "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"
)
MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
)

# Equality test codes come from
# https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes

'''
class Year:
    """A year, containing between 365 and 366 days.
    
    Attributes
    ----------
    all_days : list[Day]
        A list of all the days in the year.
        It does NOT contains exceptional_days.
        Use the `get_day()` method to get them.
    always_open : bool
        True if it's always open (24/7), False else.
    exceptional_days : list[Day]
        A list of the exceptional days (e.g. "Dec 25 off").
    year : int
        The year (e.g. 2017).
    
    /!\ Default, the school and public holidays aren't included
    in "all_days" attribute: you must define them first
    (see the OHParser's "set_PH()" and "set_SH()" methods).
    
    This class is not intended to be created by anything other
    than the OHParser.
    """
    
    def __init__(self):
        self.all_days = []
        self.always_open = False
        self.exceptional_days = []
        self.year = None
    
    def get_day(self, dt):
        """Returns a Day from a datetime.
        
        Parameters
        ----------
        datetime.datetime / datetime.date
            The date of the day. /!\ This method will ignore
            the year of the given datetime.
        
        Returns
        -------
        Day : The requested day.
        
        Raises
        ------
        ValueError
            When no datetime is provided.
        """
        if index is None and not dt:
            raise ValueError("A 'datetime' must be given.")
        exceptional_dates = [day.date for day in self.exceptional_days]
        if dt in exceptional_dates:
            return self.exceptional_days[exceptional_dates.index(dt)]
        # TODO : Check and improve.
        if isinstance(dt, datetime.datetime):
            dt = dt.date()
        # TODO : Fix this dirty hack.
        for day in self.all_days:
            if day.date == dt:
                return day
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<Year {}>".format(self.year)

class Day:
    """A day, containing periods.
    
    Attributes
    ----------
    periods : list[Period]
        The opening periods of the day.
    always_open : bool
        True if it's open all the day (24/7), False else.
    date : datetime.date
        The date of the day.
    """
    
    def __init__(self, index):
        self.periods = []
        self.date = None
    
    def opens_today(self) -> bool:
        """Is it open today?
        
        Returns
        -------
        bool
            True if the day contains any opening period. False else.
        """
        return bool(len(self.periods))
    
    def is_open(self, moment):
        """Is it open?
        
        Parameters
        ----------
        moment : datetime.datetime
            The moment for which to check the opening.
        
        Returns
        -------
        bool
            True if it's open, False else.
            /!\ Returns False if the concerned day contains an unset
            solar moment.
        """
        if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
            moment = pytz.UTC.localize(moment)
        for period in self.periods:
            if moment in period:
                return True
        return False
    
    def is_always_open(self):
        """Returns whether it's open the whole day."""
        return all((
            len(self.periods) == 1,
            self.periods[0].beginning.time() == datetime.time.min,
            self.periods[0].end.time() == datetime.time.max
        ))
    
    def _contains_unknown_times(self):
        """Returns whether there are unknown solar hours in the day.
        
        Returns True if so, False else.
        """
        for period in self.periods:
            if not period.beginning.time() or not period.end.time():
                return True
        return False
    
    def _set_always_open(self):
        self.always_open = True
        self.periods = [Period(datetime.time.min, datetime.time.max)]
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<Day '{}' ({} periods)>".format(
            WEEKDAYS[self.index],
            len(self.periods)
        )
'''

class Day:
    def __init__(self, date):
        """A day, containing periods.
        
        Attributes
        ----------
        periods : list[Period]
            The opening periods of the day.
        always_open : bool
            True if it's open all the day (24/7), False else.
        date : datetime.date
            The date of the day.
        """

        self.date = date
        self.periods = []
        self._solar_hours = {
            "sunrise": None, "sunset": None,
            "dawn": None, "dusk": None
        }
    
    def opens_today(self) -> bool:
        """Is it open today?
        
        Returns
        -------
        bool
            True if the day contains any opening period. False else.
        """
        return bool(len(self.periods))
    
    def is_open(self, moment):
        """Is it open?
        
        Parameters
        ----------
        moment : datetime.datetime
            The moment for which to check the opening.
        
        Returns
        -------
        bool
            True if it's open, False else.
            /!\ Returns False if the concerned day contains an unset
            solar moment.
        """
        if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
            moment = pytz.UTC.localize(moment)
        for period in self.periods:
            if moment in period:
                return True
        return False
    
    def is_always_open(self):
        # TODO : Handle closed days.
        """Returns whether it's open the whole day."""
        return all((
            len(self.periods) == 1,
            self.periods[0].beginning.time() == datetime.time.min,
            self.periods[0].end.time() == datetime.time.max
        ))
    
    def _set_solar_hours(self, _solar_hours):
        for period in self.periods:
            period.beginning._solar_hours = _solar_hours
            period.end._solar_hours = _solar_hours
    
    def _contains_unknown_times(self):
        """Returns whether there are unknown solar hours in the day.
        
        Returns True if so, False else.
        """
        for period in self.periods:
            if not period.beginning.time() or not period.end.time():
                return True
        return False
    
    def _set_always_open(self):
        self.always_open = True
        self.periods = [Period(datetime.time.min, datetime.time.max)]
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<Day '{}' ({} periods)>".format(
            WEEKDAYS[self.date.weekday()],
            len(self.periods)
        )

class HolidayDay(Day):  # Not used yet.
    def __init__(self, weekday):
        """An holiday day, containing periods.
        
        Attributes
        ----------
        periods : list[Period]
            The opening periods of the day.
        always_open : bool
            True if it's open all the day (24/7), False else.
        date : datetime.date
            The date of the day.
        """
        self.weekday = weekday
        self.periods = []
    
    def __str__(self):
        return "<HolidayDay '{}' ({} periods)>".format(
            WEEKDAYS[self.weekday],
            len(self.periods)
        )

class Period:
    """An opening period, containing a beginning and an end.
    
    Attributes
    ----------
    beginning : Moment
        A Moment representing the beginning of the period.
    end : Moment
        A Moment representing the end of the period.
    """
    
    def __init__(self, beginning, end):
        self.beginning = beginning
        self.end = end
    
    def is_variable(self):
        """Returns whether the period is variable.
        
        Returns
        -------
        bool
            True if the period contains a non-normal moment, False else.
        """
        return self.beginning.kind.requires_parsing() or self.end.kind.requires_parsing()
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __contains__(self, moment):
        """Returns whether a moment is included in the period.
        
        Parameters
        ----------
        datetime.datetime / datetime.time / Moment
            The moment for which to check. Must be timezone aware.
        """
        if not self.beginning.time() or not self.end.time():
            raise SolarHoursNotSetError("This period contains an unset solar moment.")
        if type(moment) is Moment:
            return self.beginning.time() <= moment.time() <= self.end.time()
        elif type(moment) is datetime.time:
            moment = moment.replace(tzinfo=pytz.UTC)
            return self.beginning.time() <= moment <= self.end.time()
        elif type(moment) is datetime.datetime:
            moment = moment.timetz().replace(tzinfo=pytz.UTC)
            return self.beginning.time() <= moment <= self.end.time()
        else:
            return NotImplemented
    
    def __repr__(self):
        return "<Period from {} to {}>".format(str(self.beginning), str(self.end))
    
    def __str__(self):
        return "{} - {}".format(str(self.beginning), str(self.end))

class MomentKind(Enum):
    """The kinds of moments, as defined in the OSM's doc."""
    
    NORMAL = 0
    SUNRISE = 1
    SUNSET = 2
    DAWN = 3
    DUSK = 4
    
    def requires_parsing(self) -> bool:
        """Returns whether a MomentKind requires a solar hours parsing."""
        return bool(self.value)

class Moment:
    """A moment in the time, which defines the beginning or the end
    of a period.
    
    Attributes
    ----------
    kind : MomentKind
        The kind of the moment.
    
    Parameters
    ----------
    MomentKind
        The kind of the moment.
    time : datetime.time, optional
        The time, if kind is "normal".
    delta : datetime.timedelta
        A timedelta from a specific moment, if kind is not "normal".
        For example, if kind is "sunrise", delta must be a timedelta
        between the moment itself and the sunrise. It may be 0 seconds.
    """
    
    def __init__(self, kind, time=None, delta=None):
        self.kind = kind
        if self.kind == MomentKind.NORMAL and not time:
            raise ValueError("A time must be given when kind is 'normal'.")
        self._time = time
        if self.kind != MomentKind.NORMAL and delta is None:
            raise ValueError("A delta must be given when kind is solar (e.g. 'sunrise', 'sunset', etc).")
        self._delta = delta
        self._solar_hours = {
            "sunrise": None, "sunset": None,
            "dawn": None, "dusk": None
        }
    
    def time(self):
        """The time of the moment.
        
        Raises
        ------
        humanized_opening_hours.exceptions.SolarHoursNotSetError
            When the kind of the moment is not "normal" and solar
            hours have not been set.
        
        Returns
        -------
        datetime.time
            A datetime.time on UTC timezone.
        """
        if not self.kind.requires_parsing():
            return self._time.replace(tzinfo=pytz.UTC)
        try:
            return (
                datetime.datetime.combine(
                    datetime.date(2000, 1, 1),
                    self._solar_hours.get(self.kind.name.lower()).replace(tzinfo=pytz.UTC)
                ) + self._delta
            ).timetz()
        except AttributeError:
            raise SolarHoursNotSetError("This moment is not of 'normal' kind and solar hours have not been set.")
    
    def _has_offset(self):
        """Returns whether the moment has an offset.
        
        Returns
        -------
        bool
            True if `self._delta.seconds` is not 0. False else.
        """
        if not self._delta:
            return False
        return self._delta.seconds != 0
    
    def __repr__(self):
        # TODO : Be more precise.
        return "<Moment ('{}')>".format(self.__str__())
    
    def __str__(self):
        if self.kind == MomentKind.NORMAL:
            return self.time().strftime("%H:%M")
        else:
            word = self.kind.name.lower()
            if not self._delta.seconds:
                return word
            else:
                delta = (
                    datetime.datetime(2000, 1, 1, 0) +
                    self._delta
                ).time().strftime("%H:%M")
                return "{word} {sign} {delta}".format(
                    word=word,
                    sign='-' if self._delta.days == -1 else '+',
                    delta=delta
                )
