import common_defs
import sqlite3
import csv
import processor

import raw_data.data_2004.adapter_2004
import raw_data.data_2006.adapter_2006
import raw_data.data_2008.adapter_2008
import raw_data.data_2011.adapter_2011
import raw_data.data_2015.adapter_2015

years = ['2004', '2006', '2008', '2011', '2015']
csv_adapters = {
    '2004' : raw_data.data_2004.adapter_2004.Adapter2004,
    '2006' : raw_data.data_2006.adapter_2006.Adapter2006,
    '2008' : raw_data.data_2008.adapter_2008.Adapter2008,
    '2011' : raw_data.data_2011.adapter_2011.Adapter2011,
    '2015' : raw_data.data_2015.adapter_2015.Adapter2015
}

for year in years:
    processor_obj = processor.Processor(year, csv_adapters[year])
    election = processor_obj.process_data()
    conn = sqlite3.connect(f'{year}.db')
    election.save(conn.cursor())
    conn.commit()
    conn.close()
