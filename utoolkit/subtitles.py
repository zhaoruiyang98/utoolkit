"""
adapted from https://github.com/Adoliin/vtt-to-ass
"""

from __future__ import annotations
from dataclasses import dataclass
import re
import pysubs2
from pathlib import Path
from pysubs2 import FormatAutodetectionError
from pysubs2 import SSAEvent
from pysubs2 import SSAFile
from pysubs2 import UnknownFPSError
from pysubs2 import UnknownFormatIdentifierError
from utoolkit.log import HasLogger
from utoolkit.log import LoggedError


def fix_weird_chars(ssa: SSAFile) -> SSAFile:
    for event in ssa.events:
        event.text = event.text.replace('&amp;', '&')
    return ssa


def remove_short_events(ssa: SSAFile, duration: int = 100) -> SSAFile:
    new_events: list[SSAEvent] = []
    for event in ssa.events:
        if event.duration >= duration:
            new_events.append(event)
    ssa.events = new_events
    return ssa


class RegularText:
    pattern = re.compile(r"(<c>)|(</c>)|(<\d\d:\d\d:\d\d.\d\d\d>)")
    space = re.compile(r'\x20+')
    empty = re.compile(r"\s+")

    def __init__(self, text: str):
        text = self.pattern.sub(" ", text)
        self.text = self.space.sub(" ", text)
        self.noamp = self.empty.sub("", self.text)
        self.len = len(self.noamp)

    def __eq__(self, other) -> bool:
        if self.len < 5 or other.len < 5:
            return self.noamp == other.noamp
        else:
            shorter, longer = self.noamp, other.noamp
            if self.len >= other.len:
                shorter, longer = longer, shorter
            return longer.startswith(shorter)


def merge_duplicates(ssa: SSAFile) -> SSAFile:
    new_events: list[SSAEvent] = []
    event_pool: list[SSAEvent] = []
    text_pool: list[RegularText] = []
    for event in ssa.events:
        text = event.plaintext
        if not text_pool:
            text_pool.append(RegularText(text))
            event_pool.append(event)
        else:
            reg = RegularText(text)
            if text_pool[-1] == reg:
                text_pool.append(reg)
                event_pool.append(event)
            else:
                mini, minlen = 0, 100000000
                for i, v in enumerate(text_pool):
                    if v.len < minlen:
                        mini, minlen = i, v.len
                assert minlen != 100000000
                new_event = event_pool[mini]
                new_event.plaintext = text_pool[mini].text
                new_event.start = event_pool[0].start
                new_event.end = event_pool[-1].end
                if '\n' in text_pool[-1].text:
                    event.start = event_pool[-1].start
                    new_event.end = event_pool[-1].start
                new_events.append(new_event)
                text_pool = [reg]
                event_pool = [event]
    if text_pool:
        new_events.append(event_pool[0])
    ssa.events = new_events
    return ssa


@dataclass
class VTTConvertor(HasLogger):
    file: str
    output: str = ""
    force: bool = False
    duration: int = 100

    def __post_init__(self):
        self.set_logger(self.__class__.__name__)
        if not self.output:
            self.output = str(Path(self.file).with_suffix(".ass"))
        if Path(self.output).exists() and not self.force:
            raise LoggedError(self.log, "%s already exists", self.output)

    def load(self) -> SSAFile:
        try:
            subs = pysubs2.load(self.file)
        except IOError as err:
            raise LoggedError(
                self.log, "%s is not a valid file", self.file) from err
        except UnicodeDecodeError as err:
            raise LoggedError(self.log, "Decode error in %s",
                              self.file) from err
        except (UnknownFPSError, UnknownFormatIdentifierError, FormatAutodetectionError) as err:
            raise LoggedError(self.log, "pysubs2 load error") from err
        return subs

    def run(self) -> None:
        ssa = self.load()
        ssa = fix_weird_chars(ssa)
        ssa = merge_duplicates(ssa)
        ssa = remove_short_events(ssa, self.duration)
        ssa.save(self.output)
