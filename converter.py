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

    def transpose(self, r_type, r_id, n_id):
        target = self.maps.get(r_type, {})
        target[r_id] = n_id
        self.allocated[r_type].append(n_id)
        print('transpose {}: {}->{}'.format(r_type, r_id, n_id))
        self.maps[r_type] = target

    def update_resource(self, resource, r_id):
        r_type = resource['Resource Type']
        o_id = resource['ID']
        resource['ID'] = r_id
        self.transpose(r_type, o_id, r_id)
        self.game_data[r_type][r_id] = resource

    def get_updated(self, resource_type, old_id):
        new_id = self.game_data[resource_type][old_id]
        return new_id

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
            avail = int(rsc['TODO'])

            if not is_reserved(resource_type, r_id):
                self.update_resource(rsc, r_id)
                continue

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

def transpose_stuff():
#   file_name = 'EV Override - Copy/Nova Files/Override Data 1.txt'
    file_dir = os.path.join('EV Override - Copy', 'Nova Files')
    files = os.listdir(file_dir)
    gd = {}
    for f_name in files:
        if f_name.endswith('.txt'):
            fd = build_file_data(os.path.join(file_dir, f_name))
            gd.update(fd)

    for key in gd:
        print(key, len(gd[key]))

    time.sleep(1)
    transposer = Transposer(gd)

    # GOVT depends on PICT
    transposer.reallocate_govt(gd['govt'])

    # DESC dependencies?
    transposer.reallocate_desc(gd['desc'])

    # WEAP depends on GOVT

    # SHIP depends on GOVT and WEAP

    # DUDE depends on SHIP and GOVT

    # TODO: Write transposer.data() to new plugin

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
