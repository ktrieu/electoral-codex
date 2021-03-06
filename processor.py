import csv
import os
import common_defs
import election
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
            for cand in cand_dict[riding_id].values():
                if cand not in candidates:
                    print(f'Unmatched candidate {cand.name} in riding number {riding_id}. Verify candidate list.')
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
        if 'Merged with' in result_info or 'Combined with' in result_info or 'Results combined with' in result_info:
            #match possible riding ids
            return re.search(r'\d+[A-Z]?(-\d+[A-Z]?)?', result_info).group(0)
        else:
            return None

    #this parses a id in the form 12-1A into 12, 1, and A. Returns the number, the suffix, and the letter
    #if they exist.
    def parse_poll_div_id(self, div_id):
        if '-' in div_id:
            items = div_id.split('-')
            num = items[0]
            suffix = items[1]
            if suffix[-1].isalpha():
                return int(num), int(suffix[0:-1]), suffix[-1]
            else:
                return int(num), int(suffix), None
        elif div_id[-1].isalpha():
            return int(div_id[0:-1]), None, div_id[-1]
        else:
            return int(div_id), None, None

    def read_poll_div(self, riding_id, merged_dict, candidates, line):
        result_info = line[candidates[0].name]
        if self.reject_poll(result_info):
            return None, None
        poll_div = common_defs.PollDivision()
        poll_div.name = self.csv_adapter.poll_get_name(line)
        div_id = self.csv_adapter.poll_get_id(line)
        #assign the name if there's no id
        if div_id == '':
            poll_div.div_num = None
            poll_div.div_suffix = None
            alpha = poll_div.name
        else:
            num, suffix, alpha = self.parse_poll_div_id(div_id)
            poll_div.div_num = num
            poll_div.div_suffix = suffix
        poll_div.riding_id = riding_id
        merged_id = self.find_merge_id(result_info)
        if merged_id:
            poll_ids = self.parse_poll_div_id(merged_id)
            merged_dict[poll_ids].append(poll_ids)
        else:
            for cand in candidates:
                votes = int(line[cand.name])
                poll_div.total_votes += votes
                poll_div.results[cand.cand_id] = votes
        return poll_div, alpha

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
                poll_div, alpha = self.read_poll_div(riding_id, merged_dict, cand_list, line)
                if poll_div is None:
                    continue
                poll_divs[(poll_div.div_num, poll_div.div_suffix, alpha)] = poll_div
                #add results to the riding-wide total
                ridings[riding_id].total_votes += poll_div.total_votes
                for cand_id, result in poll_div.results.items():
                    ridings[riding_id].results[cand_id] += result
        self.split_merged_poll_divs(poll_divs, merged_dict)
        poll_divs = self.deduplicate_poll_divs(poll_divs)
        return poll_divs

    def split_merged_poll_divs(self, poll_divs, merged_dict):
        for merged, merge_to in merged_dict.items():
            #plus one because the merged poll division gets a share as well
            divisor = len(merge_to) + 1
            merged_div = poll_divs[merged]
            for merge_to_id in merge_to:
                poll_divs[merge_to_id].total_votes = merged_div.total_votes / divisor
            merged_div.total_votes /= divisor
            for cand_id, result in merged_div.results.items():
                merged_div.results[cand_id] = result / divisor
                for merge_to_id in merge_to:
                    poll_div = poll_divs[merge_to_id]
                    poll_div.results[cand_id] = result / divisor

    def deduplicate_poll_divs(self, poll_divs):
        deduplicated = dict()
        for poll_info, poll_div in poll_divs.items():
            num = poll_info[0]
            suffix = poll_info[1]
            if (num, suffix) in deduplicated:
                original = deduplicated[(num, suffix)]
                for cand_id, votes in poll_div.results.items():
                    original.results[cand_id] += votes
                original.total_votes += poll_div.total_votes
            else:
                deduplicated[(num, suffix)] = poll_div
        return deduplicated

    def load_poll_divs(self, ridings, candidates):
        poll_divs = list()
        for poll_file_name in os.listdir(self.data_path + POLL_DIV_FOLDER):
            divs_from_file = self.poll_divs_from_file(ridings, candidates, poll_file_name)
            poll_divs.extend(divs_from_file.values())
        return poll_divs

    def load_summary(self):
        summary_dict = dict()
        with open(f'{self.data_path}/summary.csv') as summary_file:
            summary_csv = csv.reader(summary_file)
            for line in summary_csv:
                summary = common_defs.Summary()
                summary.party = line[0]
                summary.seats = int(line[1])
                summary.votes = int(line[2])
                summary.leader = line[3]
                summary_dict[summary.party] = summary
        return summary_dict

    def calc_swings(self, election_data):
        summary_percents = dict()
        for party, summary in election_data.summary.items():
            if party is not 'ALL':
                summary_percents[party] = summary.votes / election_data.summary['ALL'].votes
        riding_swings = dict()
        for riding_id, riding in election_data.ridings.items():
            swings = self.calc_result_swing(riding, summary_percents, election_data.candidates)
            riding_swings[riding_id] = swings
        div_swings = dict()
        for div in election_data.poll_divs:
            swings = self.calc_result_swing(div, summary_percents, election_data.candidates)
            #don't add swings for divisions with no votes
            if swings is not None:
                div_swings[(div.riding_id, div.div_num, div.div_suffix)] = swings
        return riding_swings, div_swings

    # NOTE: division here means EITHER a riding or a poll division
    def calc_result_swing(self, division, summary_percents, candidates):
        if division.total_votes == 0:
            return None
        result_percents = collections.Counter()
        swings = dict()
        for _, cand in candidates[division.riding_id].items():
            party = cand.party
            result_percents[party] += division.results[cand.cand_id]
        for party, vote in result_percents.items():
            swings[str(party)] = (vote / division.total_votes) - summary_percents[str(party)]
        return swings

    def process_data(self):
        election_data = election.Election()
        print(f'Loading data for {self.year}...')
        print('Loading candidates...')
        election_data.candidates = self.load_candidates()
        print('Candidates loaded.')
        ridings_dict = dict()
        #there is no global list of ridings and their ids
        #so we have to load them along with poll divisions
        print('Loading poll divisions and ridings....')
        election_data.poll_divs = self.load_poll_divs(ridings_dict, election_data.candidates)
        election_data.ridings = ridings_dict
        print('Poll divisions and ridings loaded.')
        print('Loading summary data...')
        election_data.summary = self.load_summary()
        print('Summary data loaded.')
        print('Calculating vote swings...')
        election_data.riding_swings, election_data.div_swings = self.calc_swings(election_data)
        print('Vote swings calculated.')
        print(f'{self.year} data loaded.')
        return election_data