import enum


class Position(enum.Enum):
    engineer = "инженер"
    head_laboratory = "заведующий лабораторией"
    complex_manager = "руководитель отдела"
    director = "директор"


class Status(enum.Enum):
    waiting = "Ожидание голосов"
    decided = "Голосование окончено"


class AcademicDegree(enum.Enum):
    no_degree = "специалист без степени"
    candidate = "кандидат наук"
    phd = "доктор наук"
    academic = "академик"
