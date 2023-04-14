from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

def get_coin_images():
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(""" 
        SELECT ?item ?image
        WHERE 
        {
        VALUES ?item {wd:Q100562299 wd:Q100562428 wd:Q100472435 wd:Q100562710 wd:Q100467755 wd:Q100544414 wd:Q100536696 wd:Q100499045 wd:Q100487199 \
        wd:Q100486776 wd:Q100534481 wd:Q100535215 wd:Q100491370 wd:Q100490930 wd:Q100535224 wd:Q100491992 wd:Q100572052 wd:Q100562921 wd:Q100576954 wd:Q100572348 }
        OPTIONAL { ?item wdt:P18 ?image. }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        """
    )
    images = []
    try:
        ret = sparql.queryAndConvert()
        for r in ret["results"]["bindings"]:
            images.append(r['image']['value'])
    except Exception as e:
        print(e)
    return images