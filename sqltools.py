import sqlite3

def find_TF(TF_name):
    '''Looks for the transcription factor in the transcriptionFactors table
    and returns the name if it is in there. Else return string'''
    symbol = (TF_name,)
    conn = sqlite3.connect("tfdata.db")
    c = conn.cursor()
    c.execute("SELECT * FROM transcriptionFactors WHERE geneSymbol =?", symbol)
    result = c.fetchone()
    if result:
        c.close()
        conn.close()
        return TF_name
    else:
        c.close()
        conn.close()
        return "This transcription factor is not in our database."

def queryTF(TF_name, field):
    '''queries the transcriptionFactors table and returns the value of the
    specified field for the specified transcription factor (must exist in table atm)'''
    # create the tuple for safe querying
    tf = (TF_name,)
    # create the connection and the cursor
    conn = sqlite3.connect("tfdata.db")
    c = conn.cursor()
    # select the whole row, fetch it and close the connection again
    c.execute("SELECT * FROM transcriptionFactors WHERE geneSymbol=?", tf)
    result = c.fetchone()
    c.close()
    conn.close()
    if field == "all":
        return result
    # this is to return the value for the specified field without querying each
    elif field == "geneSymbol":
        return result[0]
    elif field == "proteinNames":
        return result[1]
    elif field == "ensemblID":
        return result[2]
    elif field == "entrezID":
        return result[3]
    elif field == "pdbID":
        return result[4]
    elif field == "uniprotID":
        return result[5]
    elif field == "DBD":
        return result[6]
    else:
        return "This column is not in this table"

#print(find_TF("ARID3B"))
#print(queryTF("TFAP2A", "proteinNames"))

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

#print(TFsearch_functionalities("FOX"))

def drug_search_functionalities(search_term):
    '''Does the same as the TFsearch_functionalities, but for the drug table'''
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


### temporary function exploring the syntax for querying multiple tables
def get_joined_data(drug_name):
    '''queries connections between drugs and transcription factors '''
    conn = sqlite3.connect('tfdata.db')
    c = conn.cursor()
    symbol = (drug_name,)
    c.execute('SELECT * FROM drugs INNER JOIN drugsTF ON drugs.drugChemblID = drugsTF.drugChemblID WHERE name=?', symbol)
    result = c.fetchall()
    c.close()
    conn.close()
    return result

#print(get_joined_data("Desogestrel"))

####functions for getting cross-information for TFs and targets and drugs and TF targets
def get_TF_target_list(TFname):
    '''Function that will return all information on the target genes of a TF as a list of tuples.
    Probably not useful due to length of result'''
    symbol = (TFname, )
    conn = sqlite3.connect('tfdata.db')
    c = conn.cursor()
    c.execute("""SELECT geneSymbol, entrezID, geneName, pseudonyms, uniprotID
    FROM targetGenes INNER JOIN targetsTF
    ON targetGenes.geneSymbol = targetsTF.targetGeneSymbol
    WHERE targetsTF.TFGeneSymbol=?""", symbol)
    result = c.fetchall()
    c.close()
    conn.close()
    return result

#print(get_TF_target_list("ARID3A"))

def get_drug_targets(drug_name):
    '''function that returns information on the TF targets of a drug'''
    symbol = (drug_name,)
    conn = sqlite3.connect('tfdata.db')
    c = conn.cursor()
    c.execute("""SELECT uniprotID, tfName, bindingSiteName, drugMechanism
    FROM drugsTF INNER JOIN drugs ON drugsTF.drugChemblID = drugs.drugChemblID
    WHERE drugs.name=?""", symbol)
    result = c.fetchall()
    result_list = [list(tuple) for tuple in result]
    c.close()
    conn.close()
    return result_list

def get_TF_drug(TFname):
    '''function that returns a nested list of information on drugs that target query TF'''
    symbol = (TFname,)
    conn = sqlite3.connect('tfdata.db')
    c = conn.cursor()
    c.execute("""SELECT drugs.name, drugsTF.drugChemblID, drugsTF.bindingSiteName,
    drugsTF.drugMechanism FROM drugs
    INNER JOIN drugsTF ON drugs.drugChemblID = drugsTF.drugChemblID
    INNER JOIN transcriptionFactors ON drugsTF.uniprotID = transcriptionFactors.uniprotID
    WHERE transcriptionFactors.geneSymbol=?""", symbol)
    result = c.fetchall()
    result_list = [list(tuple) for tuple in result]
    c.close()
    conn.close()
    return result_list

#print(get_TF_drug("PGR"))
#print(get_drug_targets("Mifepristone"))
##### Just some other functions for copy and paste
def get_pdb_url(pdbID):
    '''function that returns the url for an image from a pdb ID'''
    if len(pdbID) > 4: 
        pdbID = pdbID.split(';')[0]
    pdbid = pdbID.lower()
    dbi = pdbid[1:3]
    url = "https://cdn.rcsb.org/images/structures/" + dbi + "/" + pdbid + "/" + pdbid + "_assembly-1.jpeg"
    return url

def get_structure_url(ChemblID):
    '''function that returns the url for an image of the drug structure'''
    url = "https://www.ebi.ac.uk/chembl/api/data/image/" + ChemblID + ".svg"
    return url

#print(get_pdb_url("2KK0"))
#print(get_structure_url("CHEMBL1274"))
