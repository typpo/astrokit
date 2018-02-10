def find_star_by_designation(analysis, designation):
    for star in analysis.catalog_reference_stars:
        if star['designation'] == designation:
            return star
    return None
