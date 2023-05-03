from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

# Runs a SPARQL query to get the images from wikidata
def get_images(filter):
    query = """ 
        SELECT DISTINCT ?item ?image ?itemLabel ?earliestdate ?latestdate ?originLabel ?inception ?materialLabel ?diameter ?mass
        WHERE 
        {
            VALUES ?item {wd:Q100562299 wd:Q100562428 wd:Q100472435 wd:Q100562710 wd:Q100467755 wd:Q100544414 wd:Q100536696 wd:Q100499045 wd:Q100487199 wd:Q100486776
            wd:Q100534481 wd:Q100535215 wd:Q100491370 wd:Q100490930 wd:Q100535224 wd:Q100491992 wd:Q100572052 wd:Q100562921 wd:Q100576954 wd:Q100572348}
            ?item wdt:P18 ?image. 
            OPTIONAL {
                   ?item p:P1071 ?tmp.
                   ?tmp ps:P1071 ?origin. 
                   ?origin rdfs:label ?originLabel ; filter(LANG(?originLabel) = "en")
            }
            OPTIONAL {
                   ?item p:P571 ?statement. 
                   ?statement ps:P571 ?inception.
            }
            OPTIONAL {  ?item p:P571 ?statement. 
                        ?statement ps:P571 ?inception.
                        ?statement pq:P1319 ?earliestdate.
                        ?statement pq:P1326 ?latestdate.}
            OPTIONAL { ?item p:P186 ?m.
                       ?m ps:P186 ?material.
                       ?material rdfs:label ?materialLabel ; filter(LANG(?materialLabel) = "en")
                     }
            OPTIONAL { ?item p:P2386 ?dia.
                       ?dia ps:P2386 ?diameter.
                     }
            OPTIONAL { ?item p:P2067 ?ms.
                       ?ms ps:P2067 ?mass.
                     } """ + filter + """
            SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        """
    result = execute_query(query)
    images = []

    origins = set()
    materials = set()

    # Parses SPARQL result and puts into array
    for r in result:
        item = r['item']['value'].split('/')[-1]
        image = r['image']['value']
        labels = r['itemLabel']['value'].split(",")
        label = labels[0] + "," + labels[1]
        date = convert_to_date(r['inception']['value']) if r['inception']['type'] == 'literal' else convert_to_date(r['earliestdate']['value']) + " - " + convert_to_date(r['latestdate']['value'])
        
        try:
            origin = r['originLabel']['value']
        except:
            origin = 'NA'
        origins.add(origin)

        try:
            material = r['materialLabel']['value']
        except:
            material = 'NA'

        materials.add(material)
        images.append([image, label, date, item, origin])

    # Reformat sets for dropdowns
    origins = list(origins)
    origins.sort()
    materials = list(materials)
    materials.sort()
    return [images, origins, materials]


def get_coin(qid, in_arabic = False):

    language_params = f'"{("ar," if in_arabic else "")}[AUTO_LANGUAGE],en"'
    
    query = """ 
          SELECT ?item ?itemDescription ?itemLabel ?invNum ?image ?period ?materialLabel ?axis ?diameter ?mass ?originLabel ?earliestdate ?latestdate ?inception ?coord
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
                           ?or ps:P1071 ?origin.
                           ?origin p:P625 ?co.
                           ?co ps:P625 ?coord.}
                OPTIONAL { ?item p:P571 ?statement. 
                           ?statement ps:P571 ?inception.}
                OPTIONAL { ?item p:P571 ?statement. 
                           ?statement ps:P571 ?inception.
                           ?statement pq:P1319 ?earliestdate.
                           ?statement pq:P1326 ?latestdate.}
                SERVICE wikibase:label { bd:serviceParam wikibase:language """ + language_params + """.}
            }
    """
    result = execute_query(query)
    # Parses SPARQL result and puts into array
    r = result[0]
    label = r['itemLabel']['value'].split(",")[0]
    data = [label]
    properties = ['image', 'itemDescription', 'originLabel', 'period', 'materialLabel', 'axis', 'diameter', 'mass', 'invNum', 'coord']

    # Handle Inception
    date = convert_to_date(r['inception']['value']) if r['inception']['type'] == 'literal' else convert_to_date(r['earliestdate']['value']) + " - " + convert_to_date(r['latestdate']['value'])
    data.append(date)

    for property in properties:
        try:
            temp = r[property]['value']
            if property == 'coord':
                parts = temp.split(" ")
                parts[0] = parts[0][parts[0].index("(") + 1:]
                parts[1] = parts[1][:parts[1].index(")")]
                temp = tuple(parts)
        except:
            temp = 'NA'
        data.append(temp)
    return data


# Helper functions

# Convert SPARQL datetime to year and add A.D/B.C labels
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

# Execute a SPARQL query
def execute_query(query):
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    try:
        result = sparql.queryAndConvert()['results']['bindings']
    except Exception as e:
        print("exception")
        result = e
    return result


def form_filter(params):
    # Get search parameters
    origin = params['origin']
    material = params['material']
    min_date = '' if not params['date_min'] else params['date_min']
    max_date = '' if not params['date_max'] else params['date_max']
    min_mass = '' if not params['mass_min'] else params['mass_min']
    max_mass = '' if not params['mass_max'] else params['mass_max']
    min_dia = '' if not params['dia_min'] else params['dia_min']
    max_dia = '' if not params['dia_max'] else params['dia_max']

    # Create corresponding SPARQL code
    origin = 'FILTER(?originLabel="' + origin + '"@en). ' if origin != 'Coin Origin' else ' '
    material = 'FILTER(?materialLabel="' + material + '"@en). ' if material != 'Material' else ' '
    min_mass = ' ?mass >' + min_mass if min_mass != '' else min_mass
    max_mass = ' ?mass <' + max_mass if max_mass != '' else max_mass

    # Mass
    if (min_mass and max_mass):
        min_mass += " && "
    mass = 'FILTER(' + min_mass + max_mass + ') ' if min_mass or max_mass else ' '

    # Diameter
    min_dia = ' ?diameter >' + min_dia if min_dia != '' else min_dia
    max_dia = ' ?diameter <' + max_dia if max_dia != '' else max_dia
    if (min_dia and max_dia):
        min_dia += " && "
    diameter = 'FILTER(' + min_dia + max_dia + ') ' if min_dia or max_dia else ' '

    # Date
    if min_date:
        while len(min_date) != 4:
            min_date = "0" + min_date
        min_date += "-00-00T00:00:00+00:00"
        min_date = ' FILTER(?earliestdate > "' + min_date + '"^^xsd:dateTime || ?inception > "' + min_date + '"^^xsd:dateTime)' if min_date else ' '

    if max_date:
        while len(max_date) != 4:
            max_date = "0" + max_date
        max_date += "-00-00T00:00:00+00:00"
        max_date = ' FILTER(?earliestdate < "' + max_date + '"^^xsd:dateTime || ?inception < "' + max_date + '"^^xsd:dateTime)' if max_date else ' '


    # Combine into query
    filter = origin + material + mass + diameter + min_date + max_date

    return filter

def get_info(coin_info):

    query="""
        SELECT ?itemLabel ?itemDescription 
        WHERE {
        VALUES ?item {wd:""" + coin_info + """}
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
  }
        """
    result = execute_query(query)
    # Parses SPARQL result and puts into array
    r = result[0]
    label = r['itemLabel']['value'].split(",")[0]
    description = r["itemDescription"]['value']

    return [label, description]