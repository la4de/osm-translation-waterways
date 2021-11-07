import utils

SECTORS = {}
LIGHTS = {}

LIGHT_COLORS = {
    'v': 'white',
    'p': 'red',
    'vi': 'green',
    'k': 'yellow',
}

def collect_sector(tags):
    ref = utils.to_ref(tags['TLNUMERO'])
    if not ref in SECTORS:
        SECTORS[ref] = []
    SECTORS[ref].append(tags)

def collect_light(tags):
    ref = tags['JNR']
    assert ref not in LIGHTS
    LIGHTS[ref] = tags

def parse_sector(tags):
    light_tags = LIGHTS[tags['LOISTO']]

    color = LIGHT_COLORS[tags['VARIS']]
    sector_start = utils.to_int(tags['ALKUKULMA'])
    sector_end = utils.to_int(tags['LOPPUKULMA'])

    out = {
        'seamark:light:colour': color,
        **utils.parse_light_sequence(light_tags['TARK_VALOT']),
    }

    if sector_start != 0 or sector_end != 360:
        out.update({
            'seamark:light:sector_start': str(sector_start),
            'seamark:light:sector_end': str(sector_end),
        })

    nom_range = []
    if light_tags['MAA_KANTO']:
        nom_range.append(utils.to_float(light_tags['MAA_KANTO']))
    if light_tags['OPT_KANTO']:
        nom_range.append(utils.to_float(light_tags['OPT_KANTO']))
    if nom_range:
        nom_range = utils.to_num(min(nom_range))
        out['seamark:light:range'] = nom_range

    if light_tags['KORK_VED']:
        out['seamark:light:height'] = utils.to_num(light_tags['KORK_VED'])

    if 'päivä' in light_tags['LAJI'].lower():
        out['seamark:light:exhibition'] = 'day'
    if 'yö' in light_tags['LAJI'].lower():
        out['seamark:light:exhibition'] = 'night'

    return out

def process_light(node):
    ref = node.tags['ref:vayla'][0]
    sectors = SECTORS.get(ref)

    if not sectors:
        return

    for i, sector_tags in enumerate(sectors, 1):
        sector_tags = parse_sector(sector_tags)
        if len(sectors) > 1:
            tags = {}
            for k, v in sector_tags.items():
                k = k.replace(':light:', f':light:{i}:')
                tags[k] = v
            sector_tags = tags
        for k, v in sector_tags.items():
            node.tags[k] = [v]
