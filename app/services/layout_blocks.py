def group_into_blocks(lines, y_gap=35):

    if not lines:
        return []

    blocks = []
    current_block = [lines[0]]

    for i in range(1, len(lines)):
        prev = lines[i-1]
        curr = lines[i]

        if abs(curr["y"] - prev["y"]) <= y_gap:
            current_block.append(curr)
        else:
            blocks.append(current_block)
            current_block = [curr]

    blocks.append(current_block)

    return blocks


def blocks_to_divs(blocks):

    divs = []

    for i, block in enumerate(blocks):
        content = "\n".join([line["text"] for line in block])

        divs.append({
            "div_id": i,
            "type": "layout_block",
            "content": content
        })

    return divs
