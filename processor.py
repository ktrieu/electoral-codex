import csv
import os
import common_defs
import re
import collections

POLL_DIV_FOLDER = 'poll_by_poll/'

class Processor:

    def __init__(self, year, csv_adapter):
        self.year = year
        self.data_path = f'raw_data/data_{year}/'
        self.csv_adapter = csv_adapter

    def extract_english(self, text):
        slash_idx = text.rfind('/')
        if slash_idx == -1:
            return text
        else:
            return text[0:slash_idx]

    def load_candidates(self):
        candidates = collections.defaultdict(dict)
        cand_id = 0
        with open(self.data_path + 'candidates.tsv', 'r', encoding=self.csv_adapter.CAND_ENCODING) as cand_file:
            cand_reader = csv.DictReader(cand_file, delimiter='\t')
            for line in cand_reader:
                cand = common_defs.Candidate()
                cand.riding_id = int(self.csv_adapter.cand_get_riding_num(line))
                cand.cand_id = cand_id
                cand.party = common_defs.Party.from_string(self.csv_adapter.cand_get_party(line))
                #join together first, middle and last
                cand.name = self.csv_adapter.cand_get_name(line)
                candidates[cand.riding_id][cand.name] = cand
                cand_id += 1
        return candidates

    def candidates_from_fields(self, fields, cand_dict, riding_id):
        candidates = list()
        parties_used = set()
        #start enumerating at candidate names
        for item in fields:
            if item in cand_dict[riding_id]:
                candidates.append(cand_dict[riding_id][item])
                parties_used.add(cand_dict[riding_id][item].party)
        if common_defs.Party.LIB not in parties_used or common_defs.Party.NDP not in parties_used or common_defs.Party.CON not in parties_used:
            print(f'Major party candidate missing in riding number {riding_id}. Check party enum mappings.')
        if (len(candidates) != len(cand_dict[riding_id])):
            for cand, _ in candidates[riding_id].items():
                if cand not in candidates:
                    print(f'Unmatched candidate {cand} in riding number {riding_id}. Verify candidate list.')
        return candidates

    def load_riding_from_poll_csv(self, id, ridings, line):
        riding = common_defs.Riding()
        riding.riding_id = id
        name_raw = self.csv_adapter.poll_get_riding_name(line)
        #deal with ridings that have different names in French and English
        slash_idx = name_raw.find('/')
        if slash_idx == -1:
            riding.name = name_raw.strip()
        else:
            riding.name = name_raw[0:slash_idx]
        ridings[riding.riding_id] = riding
        ridings[id] = riding

    def reject_poll(self, result_info):
        return ('Void' in result_info or 'No poll held' in result_info or 'Electors voted' in result_info)

    def riding_num_from_file_name(self, file_name):
        match = re.search(r'\d+', file_name)
        return int(match.group(0))

    def find_merge_id(self, result_info):
        if 'Merged with' in result_info or 'Combined with' in result_info:
            #match possible riding ids
            return re.search(r'\d+[A-Z]?(-\d+[A-Z]?)?', result_info).group(0)
        else:
            return None

    def read_poll_div(self, riding_id, merged_dict, candidates, line):
        result_info = line[candidates[0].name]
        if self.reject_poll(result_info):
            return None
        poll_div = common_defs.PollDivision()
        poll_div.name = self.csv_adapter.poll_get_name(line)
        poll_div.div_id = self.csv_adapter.poll_get_id(line)
        poll_div.riding_id = riding_id
        merged_id = self.find_merge_id(result_info)
        if merged_id:
            merged_dict[merged_id].append(poll_div.div_id)
        else:
            for cand in candidates:
                poll_div.results[cand.cand_id] = int(line[cand.name])
        return poll_div

    def poll_divs_from_file(self, ridings, candidates, file_name):
        riding_id = self.riding_num_from_file_name(file_name)
        merged_dict = collections.defaultdict(list)
        poll_divs = dict()
        with open(self.data_path + POLL_DIV_FOLDER + file_name, 'r', encoding=self.csv_adapter.POLL_ENCODING) as poll_div_file:
            poll_div_reader = csv.DictReader(poll_div_file)
            #load the riding
            self.load_riding_from_poll_csv(riding_id, ridings, next(poll_div_reader))
            #reset the file and skip the header
            poll_div_file.seek(0)
            next(poll_div_reader)
            cand_list = self.candidates_from_fields(poll_div_reader.fieldnames, candidates, riding_id)
            for line in poll_div_reader:
                poll_div = self.read_poll_div(riding_id, merged_dict, cand_list, line)
                if poll_div is None:
                    continue
                poll_divs[poll_div.div_id] = poll_div
                #add results to the riding-wide total
                for cand_id, result in poll_div.results.items():
                    ridings[riding_id].results[cand_id] += result
        self.split_merged_poll_divs(poll_divs, merged_dict)
        return poll_divs

    def split_merged_poll_divs(self, poll_divs, merged_dict):
        for merged, merge_to in merged_dict.items():
            #plus one because the merged poll division gets a share as well
            divisor = len(merge_to) + 1
            merged_div = poll_divs[merged]
            for cand_id, result in merged_div.results.items():
                merged_div.results[cand_id] = result / divisor
                for merge_to_id in merge_to:
                    poll_div = poll_divs[merge_to_id]
                    poll_div.results[cand_id] = result / divisor

    def load_poll_divs(self, ridings, candidates):
        poll_divs = list()
        for poll_file_name in os.listdir(self.data_path + POLL_DIV_FOLDER):
            divs_from_file = self.poll_divs_from_file(ridings, candidates, poll_file_name)
            poll_divs.extend(divs_from_file.values())
        return poll_divs

    def process_data(self):
        print(f'Loading data for {self.year}...')
        print('Loading candidates...')
        cand_dict = self.load_candidates()
        print('Candidates loaded.')
        ridings_dict = dict()
        #there is no global list of ridings and their ids
        #so we have to load them along with poll divisions
        print('Loading poll divisions and ridings....')
        poll_divs = self.load_poll_divs(ridings_dict, cand_dict)
        print('Poll divisions and ridings loaded.')
        print(f'{self.year} data loaded.')
        return cand_dict, ridings_dict, poll_divs
