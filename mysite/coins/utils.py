from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

# Runs a SPARQL query to get the images from wikidata
def get_default_images():

    # Handles coins where inception is divided into earliest and latest date
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(""" 
        SELECT ?item ?image ?itemLabel ?earliestdate ?latestdate ?originLabel
        WHERE 
        {
            VALUES ?item {wd:Q100562299 wd:Q100562428 wd:Q100472435 wd:Q100562710 wd:Q100467755 wd:Q100544414 wd:Q100536696 wd:Q100499045 wd:Q100487199 \
            wd:Q100534481 wd:Q100535215 wd:Q100491370 wd:Q100490930 wd:Q100535224 wd:Q100491992 wd:Q100572052 wd:Q100562921 wd:Q100576954 wd:Q100572348}
            ?item wdt:P18 ?image. 
            OPTIONAL {
                   ?item p:P1071 ?tmp.
                   ?tmp ps:P1071 ?origin. 
            }
            OPTIONAL {  ?item p:P571 ?statement. 
                        ?statement ps:P571 ?inception.
                        ?statement pq:P1319 ?earliestdate.
                        ?statement pq:P1326 ?latestdate.}
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        """
    )
    images = []
    origins = set()

    # Parses SPARQL result and puts into array
    try:
        ret = sparql.queryAndConvert()
        for r in ret["results"]["bindings"]:
            item = r['item']['value'].split('/')[-1]
            image = r['image']['value']
            labels = r['itemLabel']['value'].split(",")
            label = labels[0] + "," + labels[1]
            date = convert_to_date(r['earliestdate']['value']) + " - " + convert_to_date(r['latestdate']['value'])
            try:
                origin = r['originLabel']['value']
            except:
                origin = 'NA'
            origins.add(origin)
            images.append([image, label, date, item, origin])
    except Exception as e:
        print(e)
    
    # Handles coins where inception is one date
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(""" 
          SELECT ?item ?image ?itemLabel ?date ?originLabel
            WHERE 
            {
                VALUES ?item {wd:Q100486776}
                OPTIONAL { ?item p:P1071 ?tmp.
                           ?tmp ps:P1071 ?origin. 
                        }
                ?item wdt:P18 ?image.
                ?item p:P571 ?inception.
                ?inception ps:P571 ?date.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
    """
    )

     # Parses SPARQL result and puts into array
    try:
        ret = sparql.queryAndConvert()
        for r in ret["results"]["bindings"]:
            item = r['item']['value'].split('/')[-1]
            image = r['image']['value']
            label = r['itemLabel']['value'].split(",")[0]
            date = convert_to_date(r['date']['value'])
            try:
                origin = r['originLabel']['value']
            except:
                origin = 'NA'
            origins.add(origin)
            images.append([image, label, date, item, origin])
    except Exception as e:
        print(e)

    return [images, origins]


def convert_to_date(date):
    neg = False
    if date[0] == "-":
        date = date[1:]
        neg = True
    date = date.split("-")[0]
    if neg:
        date = str(int(date) + 1) + " B.C."
    else:
        date += " A.D."

    # Get rid of leading zeroes
    while date[0] == "0":
        date = date[1:]
    
    return date

def get_coin(qid):
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    # Handle inception - there's one coin that needs to be done differently due to having a singular date of inception
    dateSPARQL = ""
    if qid == "Q100486776":
        dateSPARQL = """OPTIONAL {?item p:P571 ?inception.
                ?inception ps:P571 ?date.}"""
    else:
        dateSPARQL = """OPTIONAL {  ?item p:P571 ?statement. 
                        ?statement ps:P571 ?inception.
                        ?statement pq:P1319 ?earliestdate.
                        ?statement pq:P1326 ?latestdate.}"""

    sparql.setQuery(""" 
          SELECT ?item ?itemDescription ?itemLabel ?invNum ?image ?period ?materialLabel ?axis ?diameter ?mass ?originLabel ?earliestdate ?latestdate ?date
            WHERE 
            {
                VALUES ?item {wd:""" + qid + """}
                ?item wdt:P18 ?image. 
                OPTIONAL { ?item p:P217 ?inv.
                        ?inv ps:P217 ?invNum.}
                OPTIONAL { ?item p:P2348 ?p.
                        ?p ps:P2348 ?pd.
                        ?pd wdt:P373 ?period}
                OPTIONAL { ?item p:P186 ?m.
                        ?m ps:P186 ?material.}
                OPTIONAL { ?item p:P8751 ?ax.
                        ?ax ps:P8751 ?axis.}
                OPTIONAL { ?item p:P2386 ?dia.
                        ?dia ps:P2386 ?diameter.}
                OPTIONAL { ?item p:P2067 ?ms.
                        ?ms ps:P2067 ?mass.}
                OPTIONAL { ?item p:P1071 ?or.
                        ?or ps:P1071 ?origin.} """ + dateSPARQL + """
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
            }
    """
    )
    try:
        ret = sparql.queryAndConvert()['results']
        r = ret['bindings'][0]
        label = r['itemLabel']['value'].split(",")[0]
        properties = ['image', 'itemDescription', 'originLabel', 'period', 'materialLabel', 'axis', 'diameter', 'mass', 'invNum']
        data = [label]

        # Handle Inception
        date = ""
        if qid == "Q100486776":
            date = convert_to_date(r['date']['value'])
        else:
            date = convert_to_date(r['earliestdate']['value']) + " - " + convert_to_date(r['latestdate']['value'])
        data.append(date)
        for property in properties:
            try:
                temp = r[property]['value']
            except:
                temp = 'NA'
            data.append(temp)

    except Exception as e:
        print("exception")
        print(e)
        data = 0
    return data