# electoral-codex
A cleaned, formatted dataset of Canadian federal elections from 2004 to 2015.

# Purpose
[Elections Canada](http://www.elections.ca/content.aspx?section=ele&dir=pas&document=index&lang=e) provides datasets for recent federal elections. However, the data is scattered across multiple .csv files and is hard to query and use. This project aims to
collect that data into simple, easy-to-use SQLite databases for each year.

Each SQLite database contains three tables: ridings, candidates, and polling divisions. Further documentation of the database format is available in db_spec.txt.

# Next Steps
Don't like staring at giant tables? A website to visualize this data is coming soon-ish.
Need more data? I also plan to add other data points that may be important, like incumbency status, fundraising, and political experience.


