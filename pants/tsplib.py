# TODO: make this file capable of reading tsplib files
# return distance matrix? or return networkx.Graph?
# import networkx


def read_tsp_file(filename):
    data = {}
    with open(filename) as f:
        for line in f:
            if ':' in line:
                key, value = line.split(':', 1)
            else:
                key = line
                lines = []
                for line in f:
                    if not line.startswith(' '):
                        break
                    lines.append(line)
                value = list(line.strip() for line in lines)
            data[key] = value
    return parse_tsp_file(data)


def parse_tsp_file(data):
    if data['EDGE_WEIGHT_TYPE'] != 'EXPLICIT':
        raise NotImplementedError('wat')
    parser = globals()[f"parse_{data['EDGE_WEIGHT_FORMAT'].lower()}"]
    return parser(data['EDGE_WEIGHT_SECTION'])


def calculate_square_dimension(numbers):
    goal = len(numbers)
    size, n = 0, 1
    while True:
        if size == goal:
            return n - 1
        elif size > goal:
            raise ValueError('non-square set of numbers')
        size += n
        n += 1


def partition(numbers, lengths):
    for length in lengths:
        part, numbers = numbers[:length], numbers[length:]
        yield part


def parse_section_lines_to_numbers(section):
    section = ' '.join(section)
    return list(int(n) for n in section.split())


def parse_upper_diag_row(numbers, dimension=None):
    dimension = dimension or calculate_square_dimension(numbers)
    lengths = range(dimension, 0, -1)
    return list(partition(numbers, lengths))


def parse_lower_diag_row(numbers, dimension=None):
    dimension = dimension or calculate_square_dimension(numbers)
    lengths = range(1, dimension + 1)
    return list(partition(numbers, lengths))


def create_matrix_from_lower_rows(rows):
    size = len(rows[-1])
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(i, size):
            matrix[i][j] = matrix[j][i] = rows[i][j]
    return matrix
