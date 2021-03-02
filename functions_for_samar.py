import sqlite3
import pandas as pd

def get_transcription_factors_df(path_to_db):
    '''function that returns the transcription factors gene symbols in dataframe format'''
    # connect to the database - remember to check path
    conn = sqlite3.connect('web design/tfdata.db')
    # the query to execute
    query = "SELECT geneSymbol FROM transcriptionFactors"
    # read into the dataframe
    tfdf = pd.read_sql_query(query, conn)
    # close the connections
    conn.close()
    # return the dataframe
    return tfdf


def get_target_genes():
    '''function that returns the target genes of all transcription factors'''
    # connect to the database
    conn = sqlite3.connect(path_to_db)
    # the query to execute
    query = "SELECT geneSymbol FROM targetGenes"
    # read into the dataframe
    targetdf = pd.read_sql_query(query, conn)
    # close the connection
    conn.close()
    return targetdf

def get_TF_target(path_to_db):
    '''function that returns a dataframe containing the transcription factors
    and their target genes'''
    # connect to the database
    conn = sqlite3.connect(path_to_db)
    # the query to execute
    query = "SELECT TFGeneSymbol, targetGeneSymbol FROM targetsTF"
    # read into the dataframe
    tftargetdf = pd.read_sql_query(query, conn)
    # close the connection
    conn.close()
    return tftargetdf

###code for checking the functions
# df1 = get_transcription_factors_df()
# print(len(df1))
# print(df1.head(10))
#
# df2 = get_target_genes()
# print(len(df2))
# print(df2.head(10))
# 
# df3 = get_TF_target()
# print(len(df3))
# print(df3.head(10))
