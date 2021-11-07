def parse_seq(sequence):
    if '*' in sequence:
        seq, sequence = sequence.split(')+')
        x, seq = seq.split('*(')
        if '+' in x:
            seq2, x = x.rsplit('+', 1)
            for s in seq2.split('+'):
                yield float(s)
        for _ in range(int(x)):
            for s in seq.split('+'):
                yield float(s)
    for seq in sequence.split('+'):
        yield float(seq)

def to_num(num, ndigits=None):
    num = float(num)
    if ndigits is None:
        if num - int(num * 10) / 10 >= 0.01:
            ndigits = 2
        elif num - int(num) >= 0.1:
            ndigits = 1
        else:
            ndigits = 0
    if ndigits == 0:
        return str(int(round(num)))
    return str(round(num, ndigits))

def to_float(string):
    return float(string)

def to_int(string):
    return int(float(string))

def to_ref(string):
    return str(to_int(string))

def parse_light_sequence(sequence):
    sequence = sequence.replace(',', '.').replace(' ', '')

    if sequence.startswith('-'):
        return {
            'seamark:light:character': 'F',
        }

    sequence, period = sequence.split('=')

    # parse sequence
    sequence = list(parse_seq(sequence))
    iso_char = len(sequence) == 2 and sequence[0] == sequence[1]
    if len(sequence) > 2:
        rate_period = sum(sequence[:-1])
    else:
        rate_period = sum(sequence)

    # combine two last off sequences if seq count is odd number
    if len(sequence) % 2 == 1:
        sequence = sequence[:-2] + [sum(sequence[-2:])]

    # round numbers
    sequence = [to_num(seq) for seq in sequence]
    # add parentheses around off states
    sequence = [ i % 2 and f'({seq})' or f'{seq}' for i, seq in enumerate(sequence)]

    group = int(len(sequence) / 2)

    period = float(period.strip('s'))

    # flashes per minute
    rate = 60  / rate_period * group
    if iso_char:
        character = 'Iso'
    elif rate >= 160:
        character = 'UQ'
    elif rate >= 80:
        character = 'VQ'
    elif rate >= 40:
        character = 'Q'
    else:
        character = 'FI'

    #TODO: lateral, cardinal, etc

    out = {
        'seamark:light:character': character,
        'seamark:light:sequence': '+'.join(sequence),
        'seamark:light:period': to_num(period),
    }

    if group > 1:
        out['seamark:light:group'] = str(group)

    return out

def process_lights(nodes):
    for node in nodes:
        process_light_tags(node.tags)

def process_light_tags(tags):
    keys = []
    light_count = 1
    for k, v in tags.items():
        if 'seamark:light' in k:
            keys.append(k)
        if len(v) > 1:
            print(k, light_count, v)
            if light_count > 1:
                assert light_count == len(v)
            light_count = len(v)

    if light_count == 1:
        return

    for k in keys:
        v = tags[k]
        del tags[k]
        for i in range(light_count):
            key = k.replace(':light:', f':light:{i + 1}:')
            if len(v) == 1:
                value = v[0]
            else:
                value = v[i]
            if value:
                tags[key] = value

    return tags


def append_ref(out, ref):
    if not ref or not out:
        return
    out['ref:vayla'] = ref


def append_name(out, tags):
    if not tags or not out:
        return

    name_fi = tags.get('NIMIS', None)
    if name_fi:
        name_fi = name_fi.replace('  ', ' ')
        out['seamark:name'] = name_fi
