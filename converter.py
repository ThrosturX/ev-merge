# -*- coding: utf-8 -*-
import csv
import itertools
import os
from pprint import pprint
import time

def transpose_mission(misn, amt_misn, amt_syst, amt_govt):
    transpose_keys = [
        'Ship Dude',
        'Aux. Ship Dude',
        'Ship Name',
        'Refuse Button',
        'Accept Button',
        'Available Ship Type',
    ]

    for key, val in misn.items():
        if 'Desc' in key:
            val = int(val)
            if not (-1 <= val <= 0):
                misn[key] = val + amt_misn
        for match in ['Syst', 'Stellar']:
            if match in key:
                val = int(val)
                if (-1 <= val <= 0):
                    continue
                if 0 < val <= 2175:
                    misn[key] = val + amt_syst
                elif val >= 10000:
                    misn[key] = val + amt_govt

    for key in transpose_keys:
        val = misn[key]
        if val == '':
            continue
        val = int(val)
        if not (-1 <= val <= 0) :
            misn[key] = val + amt_govt

    # pay value
    pay_value = int(misn['Pay Value'])
    if pay_value < -1000: 
        misn['Pay Value'] = pay_value - amt_misn
    return misn

def build_used():
    used = {}
    with open('reserved.txt', 'r') as db_file:
        for line in db_file:
            t, i = line.split('\t')
            used[t.strip('"')] = i
    return used

def is_reserved(type_name, res_id):
    # reserved.txt contains nova things
    rid = str(res_id)
    with open('reserved.txt', 'r') as db_file:
        for line in db_file:
            if type_name in line:
                no_part = line[-(len(rid)+1):-1]
                if rid == no_part:
                    return True
    return False

def _example_time():
    ts = time.time()
    for i in range(8010):
        is_reserved('weap', i)

    te = time.time()
    print('took {} seconds'.format(te-ts))

def clean(row):
    bads = [None, 'End-of-resource']
    for bad in bads:
        if bad in row:
            row.pop(bad)

    r_type = row['Resource Type']
    r_id = row['ID']

    return r_type, int(r_id)

def build_file_data(file_name):
    resources = {}
    consume_lines = 4
    with open(file_name, newline='', encoding='latin-1') as csvfile:
        # eat the header
        for _ in range(consume_lines):
            next(csvfile)
        for _group, csvpart in itertools.groupby(csvfile, key=lambda line: bool(line.strip())):
            for row in csv.DictReader(csvpart, delimiter='\t'):
#               print(row)
                try:
                    r_type, r_id = clean(row)
                except:
                    continue
                if not r_type or not r_id:
                    continue
                if r_type not in resources:
                    resources[r_type] = {}
#                   print(r_type, row.keys())
                resources[r_type][r_id] = row
    return resources

def build_plugin(data, out_file_name):
    with open(out_file_name, 'w', newline='', encoding='latin-1') as csvfile:
        for resource_type, resources in data.items():
            if not resources:
                continue
            print("writing {} of {} resources".format(resource_type, len(resources)))
            field_names = list(next(iter(resources.values())))
            print(field_names)
            writer = csv.DictWriter(csvfile, field_names, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for resource in resources.values():
                writer.writerow(resource)
            print("", file=csvfile)

class Transposer():
    def __init__(self, gd):
        self.original_data = gd
        self.allocated = self.build_used()
        self.maps = {}
        self.game_data = {}
        for key in self.original_data:
            self.game_data[key] = {}

    def data(self):
        return self.game_data

    def build_used(self):
        used = {}
        with open('reserved.txt', 'r') as db_file:
            for line in db_file:
                t, i = line.split('\t')
                tt = t.strip('"')
                ii = int(i)
                print(tt, ii)
                ut = used.get(tt, [])
                ut.append(ii)
                used[tt] = ut
        print("ok")
        return used

    def used(self, r_type, r_id):
        if r_id in self.allocated.get(r_type, {}):
            return True

        return False

    def get_avail_id(self, r_type, max_resources=128):
        used_gd_ids = [r_id for r_id in self.game_data[r_type]]
        used_al_ids = self.allocated[r_type]
        used_ids = used_gd_ids + used_al_ids
        for n_id in range(128, max_resources + 128):
            if n_id in used_ids:
                continue
            return n_id
        raise Exception("No available ID for {} (assuming maximum {} {}s)".format(r_type, max_resources, r_type))

    def transpose(self, r_type, r_id, n_id):
        # first! check if we already allocated r_id
        old = self.maps.get(r_type, {}).get(r_id)
        if old:
            type_map = self.maps.get(r_type, {})
            p_id = 0
            for previous in type_map:
                if type_map[previous] == r_id:
                    p_id = previous
                    break
            print("WARNING! NOT REALLOCATING {} (was {})".format(r_id, p_id))
            return old
        target = self.maps.get(r_type, {})
        target[r_id] = n_id
        self.allocated[r_type].append(n_id)
        skip_prints = ['desc']
        if r_type not in skip_prints:
            print('transpose {}: {}->{}'.format(r_type, r_id, n_id))
        self.maps[r_type] = target
        return n_id

    def update_resource(self, resource, r_id):
        r_type = resource['Resource Type']
        o_id = resource['ID']
        resource['ID'] = r_id
        resource['End-of-resource'] = "EOR"
        n_id = self.transpose(r_type, o_id, r_id)
        self.game_data[r_type][n_id] = resource

    def get_updated(self, resource_type, old_id):
        new_id = self.game_data[resource_type][old_id]
        return new_id

    def get_reallocated(self, resource_type, old_id):
        if int(old_id) == -1:
            return '-1'
        re_id = self.maps[resource_type][old_id]
        return re_id

    def reallocate_govt(self, resources):
        # Note: We don't change classes at all
        # In fact, we merely reassign IDs and update the PICT
        resource_type = 'govt'

        for r_id, rsc in resources.items():
            # update NewsPic (funny, unused in EVO)
            news = int(rsc['News Picture'])
            if news >= 128 and news != 9000:
                new_id = self.get_updated(resource_type, news)
                rsc['News Picture'] = new_id

            if not is_reserved(resource_type, r_id):
                self.update_resource(rsc, r_id)
                continue

            for n_id in range(r_id + 1, 32760):
                if not self.used(resource_type, n_id):
                    self.update_resource(rsc, n_id)
                    break

    def reallocate_outf(self, resources):
        resource_type = 'outf'

        for r_id, rsc in resources.items():
            # get a new id
            n_id = self.get_avail_id('outf', 512)

            # we have to change the mod values
            num_mods = [1, 2, 3, 4]

            for mod_number in num_mods:
                key = 'Mod Type {}'.format(mod_number)
                mod_type = rsc[key]
                if mod_type == '1':
                    # It's a weapon, update the weapon ID
                    key = 'Mod Value {}'.format(mod_number)
                    weap = rsc[key]
                    rsc[key] = self.get_reallocated('weap', weap)
                   #print("updated weapon on outf {}: {} -> {}".format(r_id, weap, rsc[key]))

            # TODO: update the available govt thing too...
        
            # assign the new id
            if not is_reserved(resource_type, r_id):
                self.update_resource(rsc, r_id)
                continue
    
            self.update_resource(rsc, n_id)

    def reallocate_desc(self, resources):
        resource_type = 'desc'

        for r_id, rsc in resources.items():
            if not is_reserved(resource_type, r_id):
                self.update_resource(rsc, r_id)
                continue

            if 4000 <= r_id <= 4999:
                for n_id in range(r_id + 1, 5000):
                    if not self.used(resource_type, n_id):
                        self.update_resource(rsc, n_id)
                        break
            else:
                for n_id in range(r_id + 1, 32760):
                    if 4000 <= n_id <= 4999:
                        continue
                    if not self.used(resource_type, n_id):
                        self.update_resource(rsc, n_id)
                        break

    def reallocate_weap(self, resources, spins):
        resource_type = 'weap'

        for r_id, rsc in resources.items():
            # get the spin resource
            gfx_off = int(rsc['Graphics'])
            spin_id = gfx_off + 3000
            spin_rsc = spins.get(spin_id, None)
            if not is_reserved(resource_type, r_id):
                self.update_resource(rsc, r_id)
                self.update_resource(spin_rsc, r_id + 3000)
                continue

            for n_id in range(r_id + 1, 256 + 128):
                if not self.used(resource_type, n_id):
                    self.update_resource(rsc, n_id)
                    # don't update invalid graphics
                    if gfx_off >= 0:
                        self.update_resource(spin_rsc, n_id + 3000 + gfx_off)
                    break

    # TODO: Stuck here because reserved.txt didn't have all the picts and such
    def reallocate_graphics(self, game_data):
        spin = game_data['spin']
        rle8 = game_data['rle8']
        rled = game_data['rleD']
        pict = game_data['pict']

        # each one of the resource type needs to have the ID transposed, but NOT the file path

        skip_spins = [x for x in range(500,816)] + [900]

        # weap updates the spin ID, so just update the resources used by the spin here
        # update the spin resource with new sprite numbers
        for r_id, rsc in spin.items():
            if int(r_id) in skip_spins:
                continue
            old_sprite = int(rsc['Sprite'])
            # transpose the rle8 and rleD based on old_sprite
            rle_id = self.get_avail_id('rleD', 512)
            try:
                self.update_resource(rle8[old_sprite], rle_id)
                self.update_resource(rled[old_sprite], rle_id)
            except KeyError:
                # update the pict instead
                rle_id = old_sprite + 66
                if self.used('pict', rle_id):
                    raise Exception("CAN'T OVERRIDE PICT {}".format(old_sprite))
                self.update_resource(pict[old_sprite], rle_id)
                # Since this wasn't a RLE, we need a mask
                # also work on the old mask
                old_mask = int(rsc['Mask'])
                new_mask = self.get_avail_id('rleD', 512)
                try:
                    self.update_resource(rle8[old_mask], new_mask)
                    self.update_resource(rled[old_mask], new_mask)
                except KeyError:
                    # update the pict instead
                    new_mask = old_mask + 66
                    if self.used('pict', new_mask):
                        print("(warning) {} (mask) already assigned".format(old_mask))
                    self.update_resource(pict[old_mask], new_mask)
            rsc['Sprite'] = rle_id
            rsc['Mask'] = rle_id + 1
            time.sleep(0.1)

    def reallocate_ship(self, resources, shans):
        # update the shan ID identicaly with the ship
        # reset the availability
        # update the government
        resource_type = 'ship'

        for r_id, rsc in resources.items():
            # pretty much guaranteed that we need to find a new ID here
            if int(r_id) == 191:
                continue # ignore the escape pod
            n_id = self.get_avail_id('ship', 768)
            rsc['Availability'] = ''
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            self.update_resource(rsc, n_id)
            self.update_resource(shans[r_id], n_id)

    def reallocate_dude(self, resources):
        resource_type = 'dude'

        for r_id, rsc in resources.items():
            n_id = self.get_avail_id('dude', 512)
            # update the govt and ship
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            for ship_type_no in [x for x in range(1, 16)]:
                label = 'Ship {}'.format(ship_type_no)
                rsc[label] = self.get_reallocated('ship', rsc[label])
            self.update_resource(rsc, n_id)

    def reallocate_flet(self, resources):
        resource_type ='flet'

        for r_id, rsc in resources.items():
            n_id = self.get_avail_id('flet', 512)
            # update the govt
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            # update the system (we are lucky because we haven't updated systems yet
            # but we have updated governments and EVO fleets use 10000+)
            prev_govt = int(rsc['System']) - 10000 + 128
            print("Finding new govt {} of flet {}".format(prev_govt, r_id))
            try:
                new_govt = self.get_reallocated('govt', str(prev_govt))
                rsc['System'] = str(int(new_govt) + 10000 - 128)
            except KeyError:
                print("Couldn't change system for flet {} ({})".format(r_id, rsc['Name']))

            # need to update all the escort types
            for ship_type_no in [x for x in range(1, 4)]:
                label = 'Escort Type {}'.format(ship_type_no)
                rsc[label] = self.get_reallocated('ship', rsc[label])

            self.update_resource(rsc, n_id)

    def reallocate_spob(self, resources):
        resource_type = 'spob'

        for r_id, rsc in resources.items():
            n_id = self.get_avail_id('spob', 2048)
            # update the govt
            # update the landspace (pict)
            # we are ignoring sounds TODO NOTE
            # SHOULD BE no need to update the graphics!
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            try:
                rsc['Defense Dude'] = self.get_reallocated('dude', rsc['Defense Dude'])
            except:
                print("Couldn't reallocate defense dude {} for {}".format(rsc['Defense Dude'], rsc['Name']))
            try:
                rsc['Graphics'] = self.get_reallocated('pict', str(int(rsc['Graphics']) + 1000)) - 100
            except:
                # we don't care about landscape graphics problems
                pass
            self.update_resource(rsc, n_id)

    def reallocate_syst(self, resources, nebu):
        resource_type = 'syst'

        SYS_Y_OFF = 600

        # first reallocate the systems
        for r_id, rsc in resources.items():
            n_id = self.get_avail_id('syst', 2048)
            # also transpose the systems
            y_pos = rsc["Y Position"]
            rsc["Y Position"] = str(int(y_pos) - SYS_Y_OFF)
            self.update_resource(rsc, n_id)

        # second reallocate the jumps
        for r_id, rsc in resources.items():
            # reallocate connections (up to 16)
            for conn_id in [x for x in range(1, 16)]:
                label = "Hyperlink {}".format(conn_id)
                rsc[label] = self.get_reallocated('syst', rsc[label])

        # third, move the nebulae
        for r_id, rsc in nebu.items():
            n_id = self.get_avail_id('nebu', 32)
            rsc['Y Position'] = str(int(rsc['Y Position']) - SYS_Y_OFF)
            self.update_resource(rsc, n_id)

        # finally, connect the new universe with the old universe
        # IDEA: Connect SCHEROS to DSN-5651
        # TODO! (done manually?)

def debug_func(gd, tp):
    tp.reallocate_graphics(gd)
    raise Exception("stop")

def update_gd_with_fd(gd, fd):
    pre_exist = False
    for rt in fd:
        if rt in gd:
            pre_exist = True
            break

    print(pre_exist)

    if pre_exist:
        for rt in fd:
            inner = gd.get(rt, {})
            inner.update(fd[rt])
            gd[rt] = inner
    else:
        gd.update(fd)

    return gd

def transpose_stuff():
#   file_name = 'EV Override - Copy/Nova Files/Override Data 1.txt'
    file_dir = os.path.join('EV Override - Copy', 'Nova Files')
    files = os.listdir(file_dir)
    gd = {}
    for f_name in files:
        if f_name.endswith('.txt'):
            fd = build_file_data(os.path.join(file_dir, f_name))
            # NOTE HERE: I used to just gd.update(fd) but this overwrites the last group of this resource type from another file -- FIX IT
            update_gd_with_fd(gd, fd)

    for key in gd:
        print(key, len(gd[key]))

    time.sleep(1)
    transposer = Transposer(gd)

#   debug_func(gd, transposer)

    # GOVT depends on PICT
    transposer.reallocate_govt(gd['govt'])

    # DESC dependencies? (other than PICT)
    transposer.reallocate_desc(gd['desc'])

    # TODO: I am here... I think!

    transposer.reallocate_graphics(gd)

    # WEAP depends on GOVT and SPIN!!
    transposer.reallocate_weap(gd['weap'], gd['spin'])

    # OUTF depends on GOVT and WEAP
    transposer.reallocate_outf(gd['outf'])

    # SHIP depends on GOVT and WEAP and OUTF
    transposer.reallocate_ship(gd['ship'], gd['shan'])

    # DUDE depends on SHIP and GOVT
    transposer.reallocate_dude(gd['dude'])

    # SPOB depends on GOVT and DUDE
    transposer.reallocate_spob(gd['spob'])

    # FLET depends on SHIP
    transposer.reallocate_flet(gd['flet'])

    # SYST depends on SPOB, DUDE and FLET
    transposer.reallocate_syst(gd['syst'], gd['nebu'])

    # Others?


    # TODO: Write transposer.data() to new plugin
    build_plugin(transposer.data(), "plugin.rez.txt")

if __name__ == '__main__':
    transpose_stuff()

def old():
    file_name = 'EV Override - Copy/Nova Files/Override Data 1.txt'
    fd = build_file_data(file_name)
    for key in fd:
        print(key, len(fd[key]))

    missions = fd['misn']
    for misn in missions.values():
        print(misn)
        transpose_mission(misn, 100, 100, 100)
        for key, value in misn.items():
            print(key, value)
        import sys
        sys.exit()
