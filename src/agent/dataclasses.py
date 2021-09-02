from dataclasses import dataclass
from datetime import datetime
from typing import List

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BasicMetric:
    value: float
    total: float
    percent: float


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ContainerSummary:
    id: str
    name: str
    image: str
    status: str
    cpu_usage: BasicMetric
    memory_usage: BasicMetric


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HostSummary:
    timestamp: datetime
    memory_usage: BasicMetric
    disk_usage: BasicMetric
    cpu_usage: BasicMetric
    containers: List[ContainerSummary]
