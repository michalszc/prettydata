"""Read clipping bounds for assertions about composed vector PDF blocks."""

from pypdf import PageObject


def _block_bounds(page: PageObject) -> list[tuple[float, float, float, float]]:
    """Read the actual page-space clipping rectangles of merged vector blocks."""
    contents = page.get_contents()
    assert contents is not None
    operations = contents.operations
    bounds = []
    for index, (matrix, operator) in enumerate(operations[:-2]):
        rectangle, next_operator = operations[index + 1]
        if (
            operator == b"cm"
            and next_operator == b"re"
            and operations[index + 2][1] == b"W"
        ):
            bounds.append(
                (
                    float(matrix[4]),
                    float(matrix[5]),
                    float(matrix[0]) * float(rectangle[2]),
                    float(matrix[3]) * float(rectangle[3]),
                )
            )
    return bounds
