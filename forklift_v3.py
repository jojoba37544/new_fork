from collections import defaultdict
from termcolor import cprint
from map_array import new_list, bin_list, material_name_dict
from datetime import date, timedelta


def default_dict_creation(list_name):
    default_dict = defaultdict(list)
    for k, v in list_name:
        default_dict[k].append(v)
    return dict(default_dict)


def tuple_to_int(dat, quant):
    # return int(''.join((str(tup[0]), f'{(tup[1]):0>5}')))
    return int(''.join((str(dat.strftime('%Y%m%d')), f'{quant:0>5}')))


def interpreter(word, typ='date'):
    if typ == 'date':
        return f'{word[6:8]}.{word[4:6]}.{word[:4]}'
    if typ == 'quant':
        return int(f'{word[8:]}')
    if typ == 'reverse':
        return f'{int(str(word[8:]))} {word[6:8]}.{word[4:6]}.{word[:4]}'


class BinNotFound(Exception):

    def __init__(self):
        self.message = 'Проблема с поиском бина в строке(такого нет в таблице)'

    def __str__(self):
        return self.message


class MapCreator:

    def __init__(self, path):
        self.warehouse_dict = {}
        self.path = path
        self.dict = {}
        self.container = []
        self._reader()

    def _reader(self):
        with open(self.path, 'r', encoding='utf8') as lx02:
            for line in lx02:
                for material in new_list:
                    upd_line = line.split('\t')
                    if material in upd_line:
                        self._look_for_items(upd_line)

    def _look_for_items(self, line):
        material = line[2]
        bin_pos = line[5]
        dat = line[6][:-1]
        bin_quantity = line[4].split(' ')[-1:][0]  # splits and returns the last elem as member of list
        date_reversed = date(int(dat[-4:]), int(dat[-7:-5]), int(dat[-10:-8]))  # as the only member so [0]
        if bin_quantity == '0':
            return
        self.container.append((material, (bin_pos, (bin_quantity, date_reversed))))

    def _dictionary(self):
        self.dict = default_dict_creation(self.container)
        log_file = open('log_file.txt', 'w', encoding='utf8')
        for material_code, value in self.dict.items():
            date_set = sorted(list({x for x in value}))  # without sorted func algorithm would work wrong
            print(date_set)
            log_file.write(f'{material_code:_^18}\n')
            for dat in date_set:
                log_file.write(f'Check {dat[1][1]} in {date_set}\n')
                for index_y, y in enumerate(date_set):
                    if y == dat:
                        continue
                    if (y[0], y[1][1]) == (dat[0], dat[1][1] + timedelta(days=1)):
                        date_set[index_y] = dat
                        # date_set[index_y] = 0
                        log_file.write(f'{"Removed":18}[{y}]\n{"":18}')
                        log_file.write(f'{date_set}\n')
                    elif y[1][1] == dat[1][1] + timedelta(days=1):
                        date_set[index_y] = (y[0], (y[1][0], dat[1][1]))
                        cprint(date_set, 'red')
                        log_file.write(f'{"Changed":18}[{y}]\n{"":18}')
                        log_file.write(f'{date_set}\n')
            for dat in date_set:
                condition_1 = (dat[0], (dat[1][0], dat[1][1] + timedelta(days=1)))
                condition_2 = (dat[0], (dat[1][0], dat[1][1] - timedelta(days=1)))
                for index, item in enumerate(value):
                    if item == dat or item == condition_1 or item == condition_2:
                        value[index] = dat
        for material_code, bin_name in self.dict.items():
            self.dict[material_code] = default_dict_creation(bin_name)
        log_file.close()

    def data_return(self):
        self._dictionary()
        for material_code, bin_name in self.dict.items():
            for bin_name_l, value in bin_name.items():
                date_set = {x[1] for x in value}
                bin_name[bin_name_l] = []
                if len(date_set) > 1:
                    quantity = sum([int(x[0]) for x in value])
                    bin_name[bin_name_l] = tuple_to_int(max(date_set), quantity)
                elif len(date_set) == 1:
                    quantity = sum([int(x[0]) for x in value])
                    bin_name[bin_name_l] = tuple_to_int(date_set.pop(), quantity)
        return self.dict


fork_map = MapCreator('lx05.txt')


def result(dict):
    res = f'{(min(dict, key=dict.get))}'
    dat_quantity = str(dict.get(res))
    dat_interpretation = interpreter(dat_quantity)
    quantity = interpreter(dat_quantity, 'quant')
    return res, quantity, dat_interpretation


with open('map.txt', 'w', encoding='utf8') as map_file:
    for key, bin_value in fork_map.data_return().items():
        print(bin_value)
        print(key, [f"{x} ({interpreter(str(bin_value.get(x)), 'reverse')})" for x in bin_value])
        result_1 = result(bin_value)
        result_2 = ''
        cprint(f'{result_1[0]} {result_1[1]} {result_1[2]}', 'red')
        if len(bin_value) >= 2:
            bin_value.pop(result_1[0])
            result_2 = result(bin_value)
            cprint(f'{result_2[0]} {result_2[1]} {result_2[2]}', 'magenta')
        try:
            map_file.write(f'\n{result_1[0]:6} --> {result_2[0]:6} {material_name_dict[key]}' if result_2
                           else f'\n{result_1[0]:17} {material_name_dict[key]} ')
        except KeyError:
            map_file.write(f'\n{result_1[0]:6} --> {result_2[0]} {key}' if result_2 else f'\n{result_1[0]:17} {key} ')

