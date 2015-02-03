import indexing
import re
import pseudo_querying
import difflib
from nltk.corpus import stopwords
import MySQLdb as mdb
import sys
from collections import defaultdict
index=indexing.build_index()

#while True:

input_query=" ".join(sys.argv[1:])
#print input_query
input_query=input_query.lower().replace(" cell","").replace(" neuron","")
in_quotes = '"[A-Za-z0-9_ ]+"'

quoted_words=re.findall(in_quotes,input_query)

prev=""

while prev!=input_query:
    prev=input_query
    input_query=re.sub(in_quotes, "", input_query)

other_words='[0-9a-z]+'
#print "quoted words",quoted_words
words = re.findall(other_words,input_query)

words.extend(quoted_words)
#print words

neurolex_ids=[]    
key_words = filter(lambda x: x not in stopwords.words('english'),words)

#print "keywords",key_words
keys=index.keys()
for keyword in key_words:
    candidates=difflib.get_close_matches(keyword,keys)
#print candidates
candidates=set(candidates)
candidates=list(candidates)
#print candidates
#for keyword in key_words:
#    candidates = [s for s in candidates if keyword in s]
#print candidates
for keyword in candidates:
	if index[keyword] not in neurolex_ids:
		neurolex_ids.append(index[keyword])

#print "ids",neurolex_ids    
results=pseudo_querying.find_relationships(neurolex_ids,index)
#print results
if results!=None:
	con = mdb.connect("localhost","neuromldb2","neuromldbv2","neuroml_dev");
	cur = con.cursor();
	result_json=defaultdict(list)
	for key,values in results.items():
		values=list(set(values))
		for value in values:
			cur.execute("select Model_ID from model_metadata_associations where Metadata_ID in (select NeuroLex_ID from neurolexes where NeuroLex_URI=\""+value+"\") order by Model_ID desc")
			r=cur.fetchone()
			if r !=None:
				result_json[key].append(r[0])		
	print result_json

'''if num==2:
    for r in result:
        print r[0],r[1],r[2]

if num==3:
    for r in result:
        print r[0],r[1],r[2],r[3],r[4],r[5]
'''