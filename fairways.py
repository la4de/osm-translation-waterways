import utils

NAVLIN_TY_SUORA = 1
NAVLIN_TY_MURTOVIIVA = 2
NAVLIN_TY_KAARRE_PAKOLLINEN = 3
NAVLIN_TY_KAARRE_TEOREETTINEN = 4

VAYLALUE_TY_NAVIGOINTI = 1
VAYLALUE_TY_ANKKUROINTI = 2
VAYLALUE_TY_KOHTAAMIS = 3
VAYLALUE_TY_SATAMA = 4
VAYLALUE_TY_KAANTO = 5
VAYLALUE_TY_LISA = 11

CURVE_LIST = []

def parse_fairway(tags):
    type_id = utils.to_int(tags['NAVLIN_TY'])
    if type_id not in (NAVLIN_TY_SUORA, NAVLIN_TY_MURTOVIIVA, NAVLIN_TY_KAARRE_PAKOLLINEN):
        return

    out = {
        'seamark:type': 'recommended_track',
    }

    if tags['NAVLIN_SYV']:
        out['seamark:recommended_track:minimum_depth'] = utils.to_num(tags['NAVLIN_SYV'])

    if tags['TOSISUUNTA']:
        out['seamark:recommended_track:orientation'] = utils.to_num(tags['TOSISUUNTA'])

    ref = utils.to_ref(tags['GDO_GID'])
    if type_id == NAVLIN_TY_KAARRE_PAKOLLINEN:
        CURVE_LIST.append(ref)
    utils.append_ref(out, ref)

    return out


def parse_fairway_area(tags):
    type_id = utils.to_int(tags['VAYALUE_TY'])
    #TODO: ohitusalue?
    if type_id in (VAYLALUE_TY_NAVIGOINTI, VAYLALUE_TY_KOHTAAMIS, VAYLALUE_TY_LISA):
        seamark_type ='fairway'
    elif type_id == VAYLALUE_TY_ANKKUROINTI:
        seamark_type ='anchorage'
    elif type_id == VAYLALUE_TY_SATAMA:
        seamark_type = 'harbour'
    elif type_id == VAYLALUE_TY_KAANTO:
        seamark_type = 'turning_basin'
    else:
        #print(f'unknown {type_id}')
        return

    out = {
        'seamark:type': seamark_type,
    }

    if tags['VAYALUE_SY']:
        out[f'seamark:{seamark_type}:minimum_depth'] = utils.to_num(tags['VAYALUE_SY'])

    utils.append_ref(out, utils.to_ref(tags['GDO_GID']))

    return out


def parse_navigation_line(tags):
    return {
        'seamark:type': 'navigation_line',
    }

def simplify_curve(way, osmnodes):
    nodes = way.nodes
    if len(nodes) <= 10:
        way.nodes = [way.nodes[0], way.nodes[-1]]
    else:
        way.nodes = [way.nodes[0], way.nodes[int(len(nodes)/2)], way.nodes[-1]]
    for node in nodes:
        if node in way.nodes:
            continue
        node.removeparent(way)
        if not node.get_parents() and not node.tags:
            osmnodes.remove(node)

def split_recommended_tracks(osmways, osmnodes):
    newways = []
    for way in osmways:
        if way.tags.get('seamark:type') != ['recommended_track']:
            continue
        if way.tags['ref:vayla'][0] in CURVE_LIST:
            simplify_curve(way, osmnodes)
        if len(way.nodes) <= 2:
            continue
        nodes = way.nodes
        way.nodes = nodes[:2]

        Way = type(way)
        prev_node = nodes[1]
        for node in nodes[2:]:

            newway = Way(way.tags)
            newway.nodes = [prev_node, node]

            prev_node.addparent(newway)
            node.addparent(newway)
            node.removeparent(node)

            prev_node = node
            newways.append(newway)

    osmways.extend(newways)

