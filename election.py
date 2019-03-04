class Election:
    def __init__(self):
        self.candidates = dict()
        self.ridings = dict()
        self.poll_divs = dict()
        self.summary = dict()
        self.riding_swings = dict()
        self.div_swings = dict()

    def candidate_to_tuple(self, candidate):
        return (candidate.cand_id, candidate.riding_id, candidate.name, candidate.party.name)

    def save_candidates(self, c):
        #since candidates is a double-nested list we have to unpack it separately
        cand_list = list()
        for riding_cands in self.candidates.values():
            cand_list.extend(riding_cands.values())
        c.execute(r'DROP TABLE IF EXISTS candidates')
        c.execute(r'CREATE TABLE candidates (cand_id INTEGER, riding_id INTEGER, name TEXT, party TEXT)')
        c.executemany(r'INSERT INTO candidates VALUES (?, ?, ?, ?)', map(self.candidate_to_tuple, cand_list))

    def calc_margin(self, results, riding_cands):
        if len(results) == 0:
            return ('UNK', 0)
        sorted_cands = sorted(riding_cands.values(), key=lambda x: results[x.cand_id])
        winning_party = sorted_cands[-1].party
        margin = results[sorted_cands[-1].cand_id] - results[sorted_cands[-2].cand_id]
        return (str(winning_party), margin)

    def riding_to_tuple(self, riding):
        winner, margin = self.calc_margin(riding.results, self.candidates[riding.riding_id])
        return (riding.riding_id, riding.name, winner, margin, riding.total_votes)

    def save_ridings(self, c):
        c.execute(r'DROP TABLE IF EXISTS ridings')
        c.execute(r'CREATE TABLE ridings (riding_id INTEGER, name TEXT, winning_party TEXT, margin REAL, total_votes INTEGER)')
        c.executemany(r'INSERT INTO ridings VALUES (?, ?, ?, ?, ?)', map(self.riding_to_tuple, self.ridings.values()))

    def polling_div_to_tuple(self, polling_div):
        winner, margin = self.calc_margin(polling_div.results, self.candidates[polling_div.riding_id])
        return (polling_div.div_num, polling_div.div_suffix, polling_div.riding_id, polling_div.name, winner, margin, polling_div.total_votes)

    def save_poll_divs(self, c):
        c.execute(r'DROP TABLE IF EXISTS poll_divisions')
        c.execute(r'CREATE TABLE poll_divisions (div_num INTEGER, div_suffix INTEGER, riding_id INTEGER, name TEXT, winning_party TEXT, margin REAL, total_votes INTEGER)')
        c.executemany(r'INSERT INTO poll_divisions VALUES (?, ?, ?, ?, ?, ?, ?)', map(self.polling_div_to_tuple, self.poll_divs))

    def generate_riding_candidates(self):
        riding_candidates = list()
        for riding in self.ridings.values():
            for cand_id, result in riding.results.items():
                riding_candidates.append((cand_id, riding.riding_id, result))
        return riding_candidates

    def generate_poll_candidates(self):
        poll_candidates = list()
        for poll in self.poll_divs:
            for cand_id, result in poll.results.items():
                poll_candidates.append((cand_id, poll.riding_id, poll.div_num, poll.div_suffix, result))
        return poll_candidates

    def save_cand_results(self, c):
        c.execute(r'DROP TABLE IF EXISTS riding_candidates')
        c.execute(r'CREATE TABLE riding_candidates (cand_id INTEGER, riding_id INTEGER, result INTEGER)')
        c.execute(r'DROP TABLE IF EXISTS poll_candidates')
        c.execute(r'CREATE TABLE poll_candidates (cand_id INTEGER, riding_id INTEGER, div_num INTEGER, div_suffix INTEGER, result INTEGER)')
        c.executemany(r'INSERT INTO riding_candidates VALUES (?, ?, ?)', self.generate_riding_candidates())
        c.executemany(r'INSERT INTO poll_candidates VALUES (?, ?, ?, ?, ?)', self.generate_poll_candidates())

    def summary_to_tuple(self, summary):
        return (summary.party, summary.seats, summary.votes, summary.leader)

    def save_summary(self, c):
        c.execute(r'DROP TABLE IF EXISTS summary')
        c.execute(r'CREATE TABLE summary (party TEXT, seats INTEGER, votes INTEGER, leader TEXT)')
        c.executemany(r'INSERT INTO summary VALUES (?, ?, ?, ?)', map(self.summary_to_tuple, self.summary.values()))

    def save_swings(self, c):
        c.execute(r'DROP TABLE IF EXISTS riding_swings')
        c.execute(r'CREATE TABLE riding_swings (riding_id INTEGER, party TEXT, swing REAL)')
        #no map here since we need info from the keys too
        riding_swing_list = list()
        for riding_id, swings in self.riding_swings.items():
            for party, swing in swings.items():
                riding_swing_list.append((riding_id, party, swing))
        c.executemany(r'INSERT INTO riding_swings VALUES (?, ?, ?)', riding_swing_list)
        c.execute(r'DROP TABlE IF EXISTS poll_div_swings')
        c.execute(r'CREATE TABLE poll_div_swings (riding_id INTEGER, div_num INTEGER, div_suffix INTEGER, party TEXT, swing REAL)')
        #ditto
        div_swing_list = list()
        for div_info, swings in self.div_swings.items():
            for party, swing in swings.items():
                div_swing_list.append((div_info[0], div_info[1], div_info[2], party, swing))
        c.executemany(r'INSERT INTO poll_div_swings VALUES (?, ?, ?, ?, ?)', div_swing_list)

    def save(self, c):
        self.save_ridings(c)
        self.save_candidates(c)
        self.save_poll_divs(c)
        self.save_cand_results(c)
        self.save_summary(c)
        self.save_swings(c)
