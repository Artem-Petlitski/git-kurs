from courseapp.server.enums import AcademicDegree, Position

competency_matrix = [
    [
        0,
        AcademicDegree.no_degree.value,
        AcademicDegree.candidate.value,
        AcademicDegree.phd.value,
        AcademicDegree.academic.value,
    ],
    [Position.engineer.value, 1, 0, 0, 0],
    [Position.head_laboratory.value, 2, 3, 4, 6],
    [Position.complex_manager.value, 3, 4.5, 6, 9],
    [Position.director.value, 4, 6, 8, 12],
]
