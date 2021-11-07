import ogr2osm
import lights
import utils
import fairways

# Debug option can be used to add unhandled items to output osm file
DEBUG = False

class Translation(ogr2osm.TranslationBase):
    def filter_tags(self, tags):
        out = None

        if 'NAVLIN_TY' in tags:
            out = fairways.parse_fairway(tags)

        elif 'VAYALUE_SY' in tags:
            out = fairways.parse_fairway_area(tags)

        elif 'NAVLINJAT' in tags:
            out = fairways.parse_navigation_line(tags)

        elif 'MAA_KANTO' in tags:
            lights.collect_light(tags)

        elif 'TY_JNR' in tags:
            seamark_type = utils.to_int(tags['TY_JNR'])
            if seamark_type in (TY_POIJU, TY_REUNAMERKKI, TY_VIITTA):
                out = parse_buoy(seamark_type, tags)
            else:
                out = parse_seamark(seamark_type, tags)

        elif 'ALKUKULMA' in tags:
            lights.collect_sector(tags)

        # TODO: remove
        if DEBUG and out is None:
            out = tags
            tags['debug'] = '1'

        return out

    def process_output(self, osmnodes, osmways, osmrelations):
        fairways.split_recommended_tracks(osmways, osmnodes)

        REFS = []
        for node in osmnodes:
            if not node.tags:
                continue

            ref = node.tags['ref:vayla']
            if ref in REFS:
                print(f'Duplicate ref {ref}')
            REFS.append(ref)

            if 'ref:vayla' not in node.tags:
                raise Exception(f"'ref:vayla' is missing from {node.tags}")
            lights.process_light(node)




TY_MERIMAJAKKA = 1
TY_SEKTORILOISTO = 2
TY_LINJAMERRKI = 3
TY_SUUNTALOISTO = 4
TY_SUURVIITTA = 5
TY_REUNAMERKKI = 7
TY_TUTKAMERKKI = 8
TY_POIJU = 9
TY_VIITTA = 10
TY_TUNNUSMAJAKKA = 11
TY_KUMMELI = 13

RAKT_LEVYKUMMELI = 7



def parse_buoy(seamark_type, tags):
    out = None
    buoy_type = utils.to_int(tags['NAVL_TYYP'])
    shape = seamark_type == TY_VIITTA and 'spar' or 'pillar'

    if buoy_type == 1:
        out = {
            'seamark:buoy_lateral:category': 'port',
            'seamark:buoy_lateral:colour': 'red',
            'seamark:buoy_lateral:shape': shape,
            'seamark:buoy_lateral:system': 'iala-a',
            'seamark:topmark:colour': 'red',
            'seamark:topmark:shape': 'cylinder',
            'seamark:type': 'buoy_lateral',
        }
    elif buoy_type == 2:
        out = {
            'seamark:buoy_lateral:category': 'starboard',
            'seamark:buoy_lateral:colour': 'green',
            'seamark:buoy_lateral:shape': shape,
            'seamark:buoy_lateral:system': 'iala-a',
            'seamark:topmark:colour': 'green',
            'seamark:topmark:shape': 'cone, point up',
            'seamark:type': 'buoy_lateral',
        }
    elif buoy_type == 3:
        out = {
            'seamark:buoy_cardinal:category': 'north',
            'seamark:buoy_cardinal:colour': 'black;yellow',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:topmark:colour': 'black',
            'seamark:topmark:shape': '2 cones up',
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 4:
        out = {
            'seamark:buoy_cardinal:category': 'south',
            'seamark:buoy_cardinal:colour': 'yellow;black',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:topmark:colour': 'black',
            'seamark:topmark:shape': '2 cones down',
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 5:
        out = {
            'seamark:buoy_cardinal:category': 'west',
            'seamark:buoy_cardinal:colour': 'yellow;black;yellow',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:topmark:colour': 'black',
            'seamark:topmark:shape': '2 cones point together',
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 6:
        out = {
            'seamark:buoy_cardinal:category': 'east',
            'seamark:buoy_cardinal:colour': 'black;yellow;black',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:topmark:colour': 'black',
            'seamark:topmark:shape': '2 cones base together',
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 7:
        out = {
            'seamark:buoy_isolated_danger:colour': 'black;red;black',
            'seamark:buoy_isolated_danger:colour_pattern': 'horizontal',
            'seamark:buoy_isolated_danger:shape': shape,
            'seamark:topmark:colour': 'black',
            'seamark:topmark:shape': '2 spheres',
            'seamark:type': 'buoy_isolated_danger',
        }
    elif buoy_type == 8:
        out = {
            'seamark:buoy_safe_water:colour': 'red;white',
            'seamark:buoy_safe_water:colour_pattern': 'vertical',
            'seamark:buoy_safe_water:shape': shape,
            'seamark:topmark:colour': 'red',
            'seamark:topmark:shape': 'sphere',
            'seamark:type': 'buoy_safe_water',
        }

    elif buoy_type == 9:
        out = {
            'seamark:buoy_special_purpose:shape': shape,
            'seamark:type': 'buoy_special_purpose',
        }

    utils.append_ref(out, utils.to_ref(tags['TLNUMERO']))

    return out


def parse_seamark(seamark_type, tags):
    out = None

    if seamark_type == TY_MERIMAJAKKA:
        out = {
            'man_made': 'lighthouse',
            'seamark:type': 'light_major',
        }

    elif seamark_type in (TY_SUURVIITTA, TY_SEKTORILOISTO):
        out = {
            'seamark:type': 'light_major',
        }

    if seamark_type == TY_SUUNTALOISTO:
        out = {
            'seamark:type': 'light_minor',
        }

    #TODO: radar, and parameters
    elif seamark_type == TY_TUTKAMERKKI:
        out = {
            'seamark:type': 'radar_reflector',
        }

    elif seamark_type == TY_LINJAMERRKI:
        out = {
            'seamark:beacon_special_purpose:category': 'leading',
            'seamark:type': 'beacon_special_purpose',
        }
        if tags['VALAISTU'] == 'K':
            if 'ylempi' in tags['NIMIS']:
                out['seamark:light:category'] = 'upper'
            if 'alempi' in tags['NIMIS']:
                out['seamark:light:category'] = 'lower'

    else:
        shape = None
        if seamark_type == TY_KUMMELI:
            if tags['RAKT_TYYP'] == RAKT_LEVYKUMMELI:
                shape = 'lattice'
            else:
                shape = 'cairn'
        elif seamark_type == TY_TUNNUSMAJAKKA:
            shape = 'tower'
        if shape:
            out = {
                'seamark:beacon_special_purpose:shape': shape,
                'seamark:type': 'beacon_special_purpose',
            }

    utils.append_name(out, tags)
    utils.append_ref(out, utils.to_ref(tags['TLNUMERO']))

    return out
