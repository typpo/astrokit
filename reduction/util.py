from collections import defaultdict

def average_instrumental_mags_by_desig(analyses, desigs):
    # Map from designation string to list of the star as it appears over
    # multiple images.
    desig_to_stars = defaultdict(list)
    for analysis in analyses:
        for desig in desigs:
            star = find_star_by_designation(analysis.annotated_point_sources, desig)
            desig_to_stars[desig].append(star)

    # Compute average for each starlist and return a star with instrumental mag = avg.
    ret = defaultdict(dict)
    for desig, starlist in desig_to_stars.items():
        avg = np.mean([star['instrumental_mag'] for star in starlist])
        star = dict(starlist[0])
        star['mag_instrumental'] = avg
        desig_to_instrumental_avg[desig] = star
    return ret

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

def get_common_stars(analyses):
    '''Returns a list of reference stars that appear in all ImageAnalyses
    '''
    assert len(analyses) > 0, 'Must have at least 1 analysis to get common stars'
    common_star_desigs = set([x['designation'] for x in analyses[0].catalog_reference_stars])
    for analysis in analyses[1:]:
        common_star_desigs.intersection_update(\
                [x['designation'] for x in analysis.catalog_reference_stars])

    # Build data on each star to return.
    ret = []
    for desig in common_star_desigs:
        star = dict(find_star_by_designation(analyses[0].catalog_reference_stars, desig))
        ret.append(star)
    return ret
