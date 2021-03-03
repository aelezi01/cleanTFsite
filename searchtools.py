import sqlite3

def TFsearch_functionalities(search_term):
    '''function that returns a list of gene symbols in the database similar to
     gene symbol that was searched for. I would recommend checking that the search
     term parameter is more than 1 character long, otherwise it will return everything
     containing that letter'''
    # create the tuple, the connection and the cursor
    # this query will allow 0, 1 or multiple characters in front of and after the pattern seached for
    if len(search_term) >= 3:
        query = ('%'+search_term+'%',)
        conn = sqlite3.connect("tfdata.db")
        c = conn.cursor()
        # search for the query and return the genesymbols from transcriptionFactors
        c.execute("SELECT geneSymbol FROM transcriptionFactors WHERE geneSymbol LIKE ?", query)
        results = c.fetchall()
        c.close()
        conn.close()
        # convert the list of tuples to one list
        result_list = []
        for i in results:
            result_list.append(i[0])
        return result_list
    else:
        return None

def drug_search_functionalities(search_term):
    '''Does the same as the TFsearch_functionalities, but for the drug table'''
    if len(search_term) >= 3:
        # create the tuple, the connection and the cursor
        # this query will allow 0, 1 or multiple characters in front of and after the pattern seached for
        query = ('%'+search_term+'%',)
        conn = sqlite3.connect("tfdata.db")
        c = conn.cursor()
        # search for the query and return the genesymbols from transcriptionFactors
        c.execute("SELECT name FROM drugs WHERE name LIKE ?", query)
        results = c.fetchall()
        c.close()
        conn.close()
        # convert the list of tuples to one list
        result_list = []
        for i in results:
            result_list.append(i[0])
        # if there are no result it returns an empty list.
        return result_list
    else:
        return None


##### Just some other functions for copy and paste
def get_pdb_url(pdbID):
    '''function that returns the url for an image from a pdb ID'''
    if len(pdbID) > 4: 
        pdbID = pdbID.split(';')[0]
    pdbid = pdbID.lower()
    dbi = pdbid[1:3]
    url = "https://cdn.rcsb.org/images/structures/" + dbi + "/" + pdbid + "/" + pdbid + "_assembly-1.jpeg"

    # the alternative url is in the case there is no assembly picture
    alt_url = "https://cdn.rcsb.org/images/structures/" + dbi + "/" + pdbid + "/" + pdbid + "_models.jpeg"
    
    return [url, alt_url]


def get_structure_url(ChemblID):
    '''function that returns the url for an image of the drug structure'''
    url = "https://www.ebi.ac.uk/chembl/api/data/image/" + ChemblID + ".svg"
    return url