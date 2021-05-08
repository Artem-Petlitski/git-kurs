from courseapp.server.matrix import competency_matrix


def find_competence_assessment(user):
    for line in competency_matrix:
        if line[0] == user.position:
            for k, column in enumerate(line):
                if competency_matrix[0][k] == user.academic_degree:
                    return column
