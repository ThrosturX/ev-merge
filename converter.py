# -*- coding: utf-8 -*-
import collections
import csv
import itertools
import os
from pprint import pprint
import time

def _generate_foroth(siqwe_id):
    return {
        'Resource Type': 'syst',
        'ID': 471,
        'Name': "Foroth",
        'X Position': '74',
        'Y Position': '-276',
        'Hyperlink 1': 557,
        'Hyperlink 2': 470,
        'Hyperlink 3': 459,
        'Hyperlink 4': '651',
        'Hyperlink 5': siqwe_id,
        'Hyperlink 6': '-1',
        'Hyperlink 7': '-1',
        'Hyperlink 8': '-1',
        'Hyperlink 9': '-1',
        'Hyperlink 10': '-1',
        'Hyperlink 11': '-1',
        'Hyperlink 12': '-1',
        'Hyperlink 13': '-1',
        'Hyperlink 14': '-1',
        'Hyperlink 15': '-1',
        'Hyperlink 16': '-1',
        'Stellar 1': 753,
        'Stellar 2': '-1',
        'Stellar 3': '-1',
        'Stellar 4': '-1',
        'Stellar 5': '-1',
        'Stellar 6': '-1',
        'Stellar 7': '-1',
        'Stellar 8': '-1',
        'Stellar 9': '-1',
        'Stellar 10': '-1',
        'Stellar 11': '-1',
        'Stellar 12': '-1',
        'Stellar 13': '-1',
        'Stellar 14': '-1',
        'Stellar 15': '-1',
        'Stellar 16': '-1',
        'Dude 1': 144,
        'Dude 2': 144,
        'Dude 3': 147,
        'Dude 4': 147,
        'Dude 5': '-1',
        'Dude 6': '-1',
        'Dude 7': '-1',
        'Dude 8': '-1',
        'Dude Probability 1': '0',
        'Dude Probability 2': '0',
        'Dude Probability 3': '0',
        'Dude Probability 4': '0',
        'Dude Probability 5': '0',
        'Dude Probability 6': '0',
        'Dude Probability 7': '0',
        'Dude Probability 8': '0',
        'Num Ships': '0',
        'Government': -1,
        'Message Buoy': '-1',
        'Num Asteroids': '1',
        'Interference': '1',
        'Person 1': '-1',
        'Person 2': '-1',
        'Person 3': '-1',
        'Person 4': '-1',
        'Person 5': '-1',
        'Person 6': '-1',
        'Person 7': '-1',
        'Person 8': '-1',
        'Person Probability 1': '0',
        'Person Probability 2': '0',
        'Person Probability 3': '0',
        'Person Probability 4': '0',
        'Person Probability 5': '0',
        'Person Probability 6': '0',
        'Person Probability 7': '0',
        'Person Probability 8': '0',
        'Visibility': '',
        'Background Color': '0',
        'Murkiness': '0',
        'Reinforcement Fleet': '0',
        'Reinforcement Time': '0',
        'Reinforcement Interval': '0',
        'Asteroid Types': '0x0300',
        'End-of-resource': 'EOR'
    }

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

def make_writeable(resource):
    new_resource = collections.OrderedDict()
    for key, value in resource.items():
        ival = value
        try:
            ival = int(value)
        except:
            if not ival.startswith('0'):
                ival = '"{0}"'.format(value)

        new_resource[key] = ival
    
    return new_resource

def build_plugin_manually(data, out_file_name):
    num_resources = 0
    for resource_type, resources in data.items():
        num_resources += len(resources)

    # modify this line to skip graphics
    skip_types = [] # ['pict', 'rle8', 'rleD', 'shan', 'spin']

    with open(out_file_name, 'w', newline='', encoding='latin-1') as csvfile:
#        print(""""Format"\t"EVNEW text 1.0.1"
#"Created by"\t"EVNEW 1.0.4"
#"Number of resources"\t{}
#""".format(num_resources), file=csvfile, end='\r\n')
        print('"Format"\t"EVNEW text 1.0.1"', file=csvfile, end='\r\n')
        print('"Created by"\t"EVNEW 1.0.4"', file=csvfile, end='\r\n')
        print('"Number of resources"\t{}'.format(num_resources), file=csvfile, end='\r\n')
        for resource_type, resources in data.items():
            if not resources:
                continue
            if resource_type in skip_types:
                print("skipping type {}".format(resource_type))
                continue
            print("writing {} of {} resources".format(resource_type, len(resources)))
            field_names = list(next(iter(resources.values())))
            header = ['"{}"'.format(x) for x in field_names]
            writer = csv.DictWriter(csvfile, field_names, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\r\n', quotechar='~', escapechar='=')
            print('\t'.join(header), file=csvfile, end='\r\n')
#           writer.writeheader()
            for resource in resources.values():
                n_r = make_writeable(resource)
                writer.writerow(n_r)
            print("", file=csvfile, end='\r\n')

def build_plugin_manually_multifile(data, out_file_name):
    for resource_type, resources in data.items():
        if not resources:
            continue
        num_resources = len(resources)
        with open(resource_type + '_' + out_file_name, 'w', newline='', encoding='latin-1') as csvfile:
            print('"Format"\t"EVNEW text 1.0.1"', file=csvfile, end='\r\n')
            print('"Created by"\t"EVNEW 1.0.4"', file=csvfile, end='\r\n')
            print('"Number of resources"\t{}'.format(num_resources), file=csvfile, end='\r\n')
            print("writing {} of {} resources".format(resource_type, len(resources)))
            field_names = list(next(iter(resources.values())))
            header = ['"{}"'.format(x) for x in field_names]
            writer = csv.DictWriter(csvfile, field_names, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\r\n', quotechar='~', escapechar='=')
            print('\t'.join(header), file=csvfile, end='\r\n')
#           writer.writeheader()
            for resource in resources.values():
                n_r = make_writeable(resource)
                writer.writerow(n_r)
            print("", file=csvfile, end='\r\n')

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

    def get_avail_id(self, r_type, max_resources=128, start_index=128, even_only=False):
        used_gd_ids = [r_id for r_id in self.game_data[r_type]]
        used_al_ids = self.allocated[r_type]
        used_ids = used_gd_ids + used_al_ids
        for n_id in range(start_index, max_resources + start_index):
            if even_only and n_id % 2 == 1:
                continue
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
        n_id = r_id
        n_id = self.transpose(r_type, o_id, r_id)
        self.game_data[r_type][n_id] = resource

    def get_updated(self, resource_type, old_id):
        new_id = self.game_data[resource_type][old_id]
        return new_id

    def is_transposed(self, resource_type, resource_id):
        return self.maps[resource_type].get(resource_id, False)

    def get_reallocated(self, resource_type, old_id):
        if int(old_id) == -1:
            return '-1'
        if resource_type == 'rleD' and int(old_id) == 2000:
            print("searching for reassigned rled 2000")
            print(self.maps['rleD'])
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

    def reallocate_outf(self, resources, desc, pict):
        resource_type = 'outf'

        for r_id, rsc in resources.items():
            # get a new id
            n_id = self.get_avail_id('outf', 512)

            # we have to change the mod values
            num_mods = [1, 2, 3, 4]

            for mod_number in num_mods:
                key = 'Mod Type {}'.format(mod_number)
                mod_type = rsc[key]
                weapon_types = ['1', '3']
                if mod_type in weapon_types:
                    # It's a weapon (or ammunition), update the weapon ID
                    key = 'Mod Value {}'.format(mod_number)
                    weap = rsc[key]
                    rsc[key] = self.get_reallocated('weap', weap)
                   #print("updated weapon on outf {}: {} -> {}".format(r_id, weap, rsc[key]))


            # TODO: update the available govt thing too...
            rsc['Availability'] = ""
            if rsc['Tech Level'] == "32767":
                rsc['Tech Level'] = "-1"

            # update the pict and desc
            old_desc_id = int(r_id) + 3000 - 128
            old_pict_id = int(r_id) + 6000 - 128

            try:
                self.update_resource(desc[old_desc_id], n_id + 3000 - 128)
            except KeyError:
                print("no desc found for outfit {}".format(rsc['Name']))
            try:
                self.update_resource(pict[old_pict_id], n_id + 6000 - 128)
            except KeyError:
                print("no pict found for outfit {}".format(rsc['Name']))
        
            # assign the new id
            self.update_resource(rsc, n_id)

    # TODO: This probably needs to get done on the resources that use them
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

    def reallocate_snd(self, resources):
        resource_type = 'snd'

        for r_id, rsc in resources.items():
            print(r_id)
            if 200 <= r_id  <= 263:
                n_id = self.get_avail_id('snd', 63, 200) # weapon sounds are 200 + (0-63)
                self.update_resource(rsc, n_id)

    def reallocate_weap(self, resources, spins, snd):
        resource_type = 'weap'

        for r_id, rsc in resources.items():
            # get the spin resource
            gfx_off = int(rsc['Graphics'])
            old_spin_id = gfx_off + 3000
            # find a new ID
            n_id = self.get_avail_id('weap', 256)
            # don't update invalid graphics
            if gfx_off >= 0:
                # we don't need to change the spin, we just need to calculate the offset
                print("GET OLD SPIN {}".format(old_spin_id))
                new_spin_id = self.get_reallocated('spin', str(old_spin_id))
                rsc['Graphics'] = str(int(new_spin_id) - 3000)

            # update the ammo type for non-bays
            ammo_exceptions = ['99']
            ammo_needs_transpose = ['1', '6', '7']
            if rsc['Guidance'] not in ammo_exceptions:
                if int(rsc['Ammo Type']) != -1:
                    rsc['Ammo Type'] = n_id - 128

            # update the sound
            os_id = int(rsc['Sound']) + 200
            if os_id >= 0:
                ns_id = self.get_reallocated('snd', str(os_id)) - 200
                rsc['Sound'] = str(ns_id)

            # TODO: I can also update ['Explosion Type'] but this requires bööm reassignment

            # finally we can update this resource
            self.update_resource(rsc, n_id)

    def reallocate_weap_bays(self, resources):
        resource_type = 'weap'

        for rsc in resources.values():
            r_id = rsc['ID']
            # if this is a bay, put the right ship type
            if rsc['Guidance'] == '99':
                rsc['Ammo Type'] = self.get_reallocated('ship', str(rsc['Ammo Type']))
                self.update_resource(rsc, r_id)

    # TODO: Problem with planet masks on spins
    def reallocate_graphics(self, game_data):
        spin = game_data['spin']
#       rle8 = game_data['rle8']
        rled = game_data['rleD']
        pict = game_data['pict']
        shan = game_data['shan']

        # each one of the resource type needs to have the ID transposed, but NOT the file path

        skip_spins = [x for x in range(500,816)] + [900]

        # update the spin resource with new sprite numbers
        # also give the spin a new available ID
        for r_id, rsc in spin.items():
            if int(r_id) in skip_spins:
                continue
            old_sprite = int(rsc['Sprite'])
            print(type(rsc['Sprite']))
            # transpose the rle8 and rleD based on old_sprite
            rle_id = self.get_avail_id('rleD', 255, 200, even_only=True)
            mask_id = rle_id + 1
            if 2000 <= old_sprite <= 2255:
                rle_id = self.get_avail_id('rleD', 255, 2000, even_only=True)
            try:
#               self.update_resource(rle8[old_sprite], rle_id)
                self.update_resource(rled[old_sprite], rle_id)
            except KeyError as exc:
                # update the pict instead
                rle_id = old_sprite + 66
                if self.used('pict', rle_id):
                    raise Exception("CAN'T OVERRIDE PICT {}".format(old_sprite))
                self.update_resource(pict[old_sprite], rle_id)
                # Since this wasn't a RLE, we need a mask
                # also work on the old mask
                old_mask = int(rsc['Mask'])
                new_mask = self.get_avail_id('rleD', 512, even_only=True)
                try:
#                   self.update_resource(rle8[old_mask], new_mask)
                    self.update_resource(rled[old_mask], new_mask)
                except KeyError:
                    # update the pict instead
                    mask_id = old_mask + 66
                    # see if the mask has been updated
                    try:
                        mask_id = self.get_reallocated('pict', old_mask)
                    except KeyError:
                        if self.used('pict', new_mask):
                            print("(warning) {} (mask) already assigned".format(old_mask))
                    self.update_resource(pict[old_mask], mask_id)
            rsc['Sprite'] = rle_id
            rsc['Mask'] = mask_id
            # currently only updating weapon and spob spins...
            # TODO
            if 1000 <= r_id <= 1255:
                n_id = self.get_avail_id('spin', 256, 1000)
                self.update_resource(rsc, n_id)
            if 3000 <= r_id <= 3255:
                n_id = self.get_avail_id('spin', 256, 3000)
                self.update_resource(rsc, n_id)

        # update the shans that use the spins
        # mask probably ignored!! 
        shan_updaters = ['Base Image']#, 'Base Mask', 'Alternate Image', 'Alternate Mask']
        for r_id, rsc in shan.items():
            for label in shan_updaters:
                # update the rleDs that are used by shan
                old_rled = int(rsc[label])
                # check if old_rled is a "new rled"
                if self.is_transposed('rleD', old_rled):
                    print("{} is already a new ID".format(r_id['Name']))
                    rsc[label] = str(old_rled)
                    raise Exception('unexpected')
                    continue
                # also check if we already transposed this rled
                try:
                    reassigned = self.get_reallocated('rleD', str(old_rled))
                    rsc[label] = str(reassigned)
                    print("{} was already assigned to {}".format(rsc['Name'], reassigned))
                    continue
                except KeyError:
                    #print("{} has not been reassigned assigned from {}".format(rsc['Name'], old_rled))
                    pass
                rle_id = self.get_avail_id('rleD', 200, 1130, even_only=True)
                print("{}: {}->{}".format(rsc['Name'], old_rled, rle_id))
                self.update_resource(rled[old_rled], rle_id)
                rsc[label] = str(rle_id)


        

    def reallocate_ship(self, resources, shans, picts, descs):
        # TODO: Escort upgrade to (second pass)
        # update the shan ID identicaly with the ship
        # reset the availability
        # update the government
        resource_type = 'ship'

        for r_id, rsc in resources.items():
            # pretty much guaranteed that we need to find a new ID here
            if int(r_id) == 191:
                continue # ignore the escape pod
            n_id = self.get_avail_id('ship', 768)
            # reset availability
            rsc['Availability'] = ''
            # reallocate government
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            for num in [x for x in range(1, 8)]:
                # reallocate weapons
                label = 'Weapon {}'.format(num)
                rsc[label] = self.get_reallocated('weap', rsc[label])
                # reallocate outfits
                label = 'Outfit {}'.format(num)
                rsc[label] = self.get_reallocated('outf', rsc[label])

            p1_old = int(r_id) + 2872
            p2_old = int(r_id) + 4872
            d1_old = int(r_id) + 12872
            d2_old = int(r_id) + 13872

            p1_new = n_id + 2872
            p2_new = n_id + 4872
            d1_new = n_id + 12872
            d2_new = n_id + 13872

            self.update_resource(rsc, n_id)
            self.update_resource(shans[r_id], n_id)

            try:
                self.update_resource(picts[p1_old], p1_new)
            except KeyError:
                print("Ship {} has no targeting picture".format(rsc['Name']))
            try:
                self.update_resource(picts[p2_old], p2_new)
            except KeyError:
                print("Ship {} has no shipyard picture".format(rsc['Name']))
            try:
                self.update_resource(descs[d1_old], d1_new)
            except KeyError:
                print("Ship {} has no shipyard description".format(rsc['Name']))
            try:
                self.update_resource(descs[d2_old], d2_new)
            except KeyError:
                print("Ship {} has no escort description".format(rsc['Name']))

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

    def reallocate_spob(self, resources, desc, pict, snd):
        resource_type = 'spob'

        for r_id, rsc in resources.items():
            n_id = self.get_avail_id('spob', 2048)
            # update the govt
            # update the landspace (pict)
            # we are ignoring sounds TODO NOTE
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            try:
                rsc['Defense Dude'] = self.get_reallocated('dude', rsc['Defense Dude'])
            except:
                #print("Couldn't reallocate defense dude {} for {}".format(rsc['Defense Dude'], rsc['Name']))
                pass
            # Update the graphics! very important actually
            gfx_off = int(rsc['Graphics'])
            old_spin_id = gfx_off + 1000
            # maybe we don't need to change the spin, we just need to calculate the offset
            print("GET OLD SPIN {}".format(old_spin_id))
            try:
                new_spin_id = self.get_reallocated('spin', str(old_spin_id))
                rsc['Graphics'] = str(int(new_spin_id) - 1000)
            except KeyError:
                # well, okay, we need to move it ourselves
                print("WARNING WARNING NO UPDATE FOR SPIN {}".format(old_spin_id))
                raise Exception("NO MOVED SPOB GRAPHIC")

            # update the landing and bar descs
            try:
                # update the landing description
                land_desc = desc[r_id]
                self.update_resource(land_desc, n_id)
            except KeyError:
                #print("No landing desc found for {}".format(rsc['Name']))
                pass
            try:
                # update the bar description
                old_bar_desc_id = r_id + 9872
                bar_desc_id = n_id + 9872
                bar_desc = desc[old_bar_desc_id]
                self.update_resource(bar_desc, bar_desc_id)
            except KeyError:
                #print("No bar desc found for {}".format(rsc['Name']))
                pass

            # update the custom fields
            custSnd = rsc['Custom Count']
            os_id = int(custSnd)
            if os_id >= 360:
                ns_id = self.get_avail_id('snd', 2000, os_id)
                s_rsc = snd[os_id]
                self.update_resource(s_rsc, ns_id)
                rsc['Custom Count'] = ns_id
                print('sound ', os_id, ' -> ', ns_id)
                input()

            custPic = rsc['Custom Landscape']
            op_id = int(custPic)
            if op_id >= 128:
                np_id = self.get_avail_id('pict', 2000, op_id)
                p_rsc = pict[op_id]
                self.update_resource(p_rsc, np_id)
                rsc['Custom Landscape'] = np_id

            self.update_resource(rsc, n_id)

    def reallocate_syst(self, resources, nebu, pict):
        resource_type = 'syst'

        SYS_Y_OFF = 700

        siqwe_id = -1
        siqwe_od = -1 
        novas_id = 471

        # first reallocate the systems
        for r_id, rsc in resources.items():
            n_id = self.get_avail_id('syst', 2048)
            if rsc['Name'] == 'Siqwe':
                siqwe_id = n_id
                siqwe_od = r_id
            # also transpose the systems
            y_pos = rsc["Y Position"]
            rsc["Y Position"] = str(int(y_pos) - SYS_Y_OFF)
            # also reallocate the spobs!
            for spob_no in [x for x in range(1, 16)]:
                label = 'Stellar {}'.format(spob_no)
                rsc[label] = self.get_reallocated('spob', rsc[label])
            # reallocate dude types
            for dude_no in [x for x in range(1, 8)]:
                label = "Dude {}".format(dude_no)
                try:
                    rsc[label] = self.get_reallocated('dude', rsc[label])
                except KeyError:
                    # no dude, no problem
                    pass
            # reallocate tother stuff? reiforcement fleet? government?
            rsc['Government'] = self.get_reallocated('govt', rsc['Government'])
            rsc['Reinforcement Fleet'] = self.get_reallocated('flet', rsc['Reinforcement Fleet'])
            self.update_resource(rsc, n_id)

        # second reallocate the jumps
        for r_id, rsc in resources.items():
            # reallocate connections (up to 16)
            for conn_id in [x for x in range(1, 16)]:
                label = "Hyperlink {}".format(conn_id)
                rsc[label] = self.get_reallocated('syst', rsc[label])
                if r_id == siqwe_od and conn_id == 3:
                    rsc[label] = novas_id
                    print("Assigning {} from system {} to {}".format(label, siqwe_id, rsc[label]))

        def calc_nebu_picts(old_id, new_id):
            o_id_off = old_id - 128
            n_id_off = new_id - 128
            base_off = 9500 - 128
            num_picts = 3
            o_pict_id_1 = old_id + base_off + o_id_off * 6
            n_pict_id_1 = new_id + base_off + n_id_off * 6
            picts = {}
            for i in range(num_picts):
                picts[o_pict_id_1 + i] = n_pict_id_1 + i
            return picts

        # third, move the nebulae
        for r_id, rsc in nebu.items():
            n_id = self.get_avail_id('nebu', 32)
            rsc['Y Position'] = str(int(rsc['Y Position']) - SYS_Y_OFF)
            # Move the nebu PICTs
            picts = calc_nebu_picts(r_id, n_id)
            for on_id, nn_id in picts.items():
                p_rsc = pict[on_id]
                self.update_resource(p_rsc, nn_id)

            self.update_resource(rsc, n_id)

        # finally, connect the new universe with the old universe
        # we already connected Siqwe to Foroth, now we need to connect the way back
        # Connect Foroth (471) to Siqwe (siqwe_id ~> 943)
        foroth = _generate_foroth(siqwe_id)
        self.game_data['syst'][novas_id] = foroth

def debug_func(gd, tp):
    tp.reallocate_graphics(gd)
    tp.reallocate_weap(gd['weap'], gd['spin'])
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
#   transposer.reallocate_desc(gd['desc'])

    # TODO: I am here... I think!


    transposer.reallocate_graphics(gd)

    # sounds depend on nothing? I think they do...
    transposer.reallocate_snd(gd['snd'])

    # WEAP depends on GOVT and SPIN!!
    transposer.reallocate_weap(gd['weap'], gd['spin'], gd['snd'])

    # OUTF depends on GOVT and WEAP
    transposer.reallocate_outf(gd['outf'], gd['desc'], gd['pict'])

    # SHIP depends on GOVT and WEAP and OUTF
    transposer.reallocate_ship(gd['ship'], gd['shan'], gd['pict'], gd['desc'])

    # reallocate WEAPS that have SHIP dependencies
    transposer.reallocate_weap_bays(gd['weap'])

    # DUDE depends on SHIP and GOVT
    transposer.reallocate_dude(gd['dude'])

    # SPOB depends on GOVT and DUDE
    transposer.reallocate_spob(gd['spob'], gd['desc'], gd['pict'], gd['snd'])

    # FLET depends on SHIP
    transposer.reallocate_flet(gd['flet'])

    # SYST depends on SPOB, DUDE and FLET
    transposer.reallocate_syst(gd['syst'], gd['nebu'], gd['pict'])

    # Others?


    # TODO: Write transposer.data() to new plugin
    build_plugin_manually(transposer.data(), "full_plugin3.txt")
    build_plugin_manually_multifile(transposer.data(), "part.txt")

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
