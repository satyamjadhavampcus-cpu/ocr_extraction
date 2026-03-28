def group_by_lines(boxes):

    lines = []

    boxes = sorted(boxes, key=lambda b: b['y'])

    current_line = []
    last_y = -100

    for box in boxes:
        if abs(box['y'] - last_y) < 15:
            current_line.append(box)
        else:
            if current_line:
                lines.append(current_line)

            current_line = [box]

        last_y = box['y']

    if current_line:
        lines.append(current_line)

    return lines


def lines_to_text(lines):
    text_lines = []

    for line in lines:
        sorted_line = sorted(line, key=lambda b: b['x'])
        text = " ".join([w['text'] for w in sorted_line])

        text_lines.append({
            "text": text,
            "y": sorted_line[0]["y"]
        })

    return text_lines
