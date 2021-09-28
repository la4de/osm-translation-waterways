import ogr2osm

# Debug option can be used to add unhandled items to output osm file
DEBUG = False

class Translation(ogr2osm.TranslationBase):
    def filter_tags(self, tags):
        out = None

        if 'KULKUSYV1' in tags:
            out = parse_fairway(tags)

        elif 'VAYALUE_SY' in tags:
            out = parse_fairway_area(tags)

        elif 'NAVLINJAT' in tags:
            out = parse_navigation_line(tags)

        elif 'TY_JNR' in tags:
            seamark_type = to_int(tags['TY_JNR'])
            if seamark_type in (TY_POIJU, TY_REUNAMERKKI, TY_VIITTA):
                out = parse_buoy(seamark_type, tags)
            else:
                out = parse_seamark(seamark_type, tags)

        # TODO: remove
        if DEBUG and out is None:
            out = tags
            tags['debug'] = '1'

        return out


def to_int(string):
    return int(float(string))

def to_depth(string):
    depth = float(string)
    return f'{depth:0.1f}'


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

def parse_fairway(tags):
    out = {
        'waterway': 'fairway',
    }

    depths = [float(tags[key]) for key in ['KULKUSYV1', 'KULKUSYV2', 'KULKUSYV3'] if tags[key]]
    if depths:
        #TODO: check tag name
        out['seamark:fairway:minimum_depth'] = to_depth(min(depths))

    append_ref(out, to_int(tags['JNRO']))

    return out


def parse_fairway_area(tags):
    out = {
        'seamark:type': 'fairway',
    }

    if tags['VAYALUE_SY']:
        #TODO: check tag name
        out['seamark:fairway:minimum_depth'] = to_depth(tags['VAYALUE_SY'])

    append_ref(out, to_int(tags['GDO_GID']))

    return out


def parse_navigation_line(tags):
    return {
        'seamark:type': 'navigation_line',
    }


def parse_buoy(seamark_type, tags):
    out = None
    buoy_type = to_int(tags['NAVL_TYYP'])
    shape = seamark_type == TY_VIITTA and 'spar' or 'pillar'

    if buoy_type == 1:
        out = {
            'seamark:buoy_lateral:category': 'port',
            'seamark:buoy_lateral:colour': 'red',
            'seamark:buoy_lateral:shape': shape,
            'seamark:buoy_lateral:system': 'iala-a',
            'seamark:type': 'buoy_lateral',
        }
    elif buoy_type == 2:
        out = {
            'seamark:buoy_lateral:category': 'starboard',
            'seamark:buoy_lateral:colour': 'green',
            'seamark:buoy_lateral:shape': shape,
            'seamark:buoy_lateral:system': 'iala-a',
            'seamark:type': 'buoy_lateral',
        }
    elif buoy_type == 3:
        out = {
            'seamark:buoy_cardinal:category': 'north',
            'seamark:buoy_cardinal:colour': 'black;yellow',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 4:
        out = {
            'seamark:buoy_cardinal:category': 'south',
            'seamark:buoy_cardinal:colour': 'yellow;black',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 5:
        out = {
            'seamark:buoy_cardinal:category': 'west',
            'seamark:buoy_cardinal:colour': 'yellow;black;yellow',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 6:
        out = {
            'seamark:buoy_cardinal:category': 'east',
            'seamark:buoy_cardinal:colour': 'black;yellow;black',
            'seamark:buoy_cardinal:colour_pattern': 'horizontal',
            'seamark:buoy_cardinal:shape': shape,
            'seamark:type': 'buoy_cardinal',
        }
    elif buoy_type == 7:
        out = {
            'seamark:buoy_isolated_danger:colour': 'black;red;black',
            'seamark:buoy_isolated_danger:colour_pattern': 'horizontal',
            'seamark:buoy_isolated_danger:shape': shape,
            'seamark:type': 'buoy_isolated_danger',
        }
    elif buoy_type == 8:
        out = {
            'seamark:buoy_safe_water:colour': 'red;white',
            'seamark:buoy_safe_water:colour_pattern': 'vertical',
            'seamark:buoy_safe_water:shape': shape,
            'seamark:type': 'buoy_safe_water',
        }

    elif buoy_type == 9:
        out = {
            'seamark:buoy_special_purpose:shape': shape,
            'seamark:type': 'buoy_special_purpose',
        }

    if out:
        if tags['VALAISTU'] == 'K':
            out['seamark:light:colour'] = out.get('seamark:buoy_lateral:colour', 'white')

    append_ref(out, to_int(tags['TLNUMERO']))

    return out


def parse_seamark(seamark_type, tags):
    out = None

    if seamark_type in (TY_MERIMAJAKKA, TY_SUURVIITTA, TY_SEKTORILOISTO):
        out = {
            'seamark:type': 'light_major',
        }

    elif seamark_type == TY_SUUNTALOISTO:
        out = {
            'seamark:type': 'light_minor',
        }

    elif seamark_type == TY_LINJAMERRKI:
        out = {
            'seamark:beacon_special_purpose:category': 'leading',
            'seamark:type': 'beacon_special_purpose',
        }
        if tags['VALAISTU'] == 'K':
            out['seamark:light:colour'] = 'white'
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

    append_name(out, tags)
    append_ref(out, to_int(tags['TLNUMERO']))

    return out

def append_ref(out, ref):
    if not ref or not out:
        return
    out['ref:source'] = str(ref)

def append_name(out, tags):
    if not tags or not out:
        return

    name_fi = tags.get('NIMIS', None)
    name_sv = tags.get('NIMIR', None)
    if name_fi:
        out['name'] = name_fi
        out['name:fi'] = name_fi
    if name_sv:
        out['name:sv'] = name_sv
