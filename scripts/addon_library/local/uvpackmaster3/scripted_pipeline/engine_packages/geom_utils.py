from uvpm_core import IslandSet


def islands_inside_box(islands, box, fully_inside):

    islands_inside = IslandSet()

    if fully_inside:
        def inside_check(island):
            island_bbox = island.bbox()
            return island_bbox.within(box)
    else:
        def inside_check(island):
            return island.overlaps(box)
    
    for island in islands:
        if inside_check(island):
            islands_inside.append(island)

    return islands_inside
