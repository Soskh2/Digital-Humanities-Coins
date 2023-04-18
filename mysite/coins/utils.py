from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

# Runs a SPARQL query to get the images from wikidata
def get_coin_images():
    # Handles coins where inception is divided into earliest and latest date
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(""" 
        SELECT ?item ?image ?itemLabel ?earliestdate ?latestdate
        WHERE 
        {
            VALUES ?item {wd:Q100562299 wd:Q100562428 wd:Q100472435 wd:Q100562710 wd:Q100467755 wd:Q100544414 wd:Q100536696 wd:Q100499045 wd:Q100487199 \
            wd:Q100534481 wd:Q100535215 wd:Q100491370 wd:Q100490930 wd:Q100535224 wd:Q100491992 wd:Q100572052 wd:Q100562921 wd:Q100576954 wd:Q100572348}
            OPTIONAL {  ?item wdt:P18 ?image. 
                        ?item p:P571 ?statement. 
                        ?statement ps:P571 ?inception.
                        ?statement pq:P1319 ?earliestdate.
                        ?statement pq:P1326 ?latestdate.}
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        """
    )
    images = []
    try:
        ret = sparql.queryAndConvert()
        for r in ret["results"]["bindings"]:
            image = r['image']['value']
            label = r['itemLabel']['value'].split(",")[0]
            date = convert_to_date(r['earliestdate']['value']) + " - " + convert_to_date(r['latestdate']['value'])
            images.append([image, label, date])
    except Exception as e:
        print(e)
    
    # Handles coins where inception is one date
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(""" 
          SELECT ?item ?image ?itemLabel ?date
            WHERE 
            {
                VALUES ?item {wd:Q100486776}
                OPTIONAL {  ?item wdt:P18 ?image. 
                            ?item p:P571 ?inception.
                            ?inception ps:P571 ?date}
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }
    """
    )

    try:
        ret = sparql.queryAndConvert()
        for r in ret["results"]["bindings"]:
            image = r['image']['value']
            label = r['itemLabel']['value'].split(",")[0]
            date = convert_to_date(r['date']['value'])
            print(date)
            images.append([image, label, date])
    except Exception as e:
        print(e)

    return images


def convert_to_date(date):
    neg = False
    if date[0] == "-":
        date = date[1:]
        neg = True
    date = date.split("-")[0]
    if neg:
        date += " BC"
    else:
        date += " AD"

    # Get rid of leading zeroes
    while date[0] == "0":
        date = date[1:]
    
    return date
