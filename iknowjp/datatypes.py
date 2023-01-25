from dataclasses import dataclass


@dataclass
class FrontView:
    pass


@dataclass
class BackView:
    pass


@dataclass
class Card:
    frontview: FrontView
    backview: BackView
