def find_star_by_designation(points, designation):
    for star in points:
        if star['designation'] == designation:
            return star
    return None

def find_point_by_id(points, pid):
    for point in points:
        if point['id'] == pid:
            return point
    return None
