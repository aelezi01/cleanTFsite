import pandas as pd
import numpy as np
import sqlite3
import base64
from io import BytesIO
from matplotlib.figure import Figure
import seaborn as sns


def get_transcription_factors_df(path_to_db):
    '''function that returns the transcription factors gene symbols in dataframe format'''
    # connect to the database - remember to check path
    conn = sqlite3.connect(path_to_db)
    # the query to execute
    query = "SELECT geneSymbol FROM transcriptionFactors"
    # read into the dataframe
    tfdf = pd.read_sql_query(query, conn)
    # close the connections
    conn.close()
    # return the dataframe
    return tfdf

def TF_expr_heatmap(gds, tfdf):
    '''Plots a heatmap of the top 50 TFs based on the standard deviation of their
    expression across the samples
    '''
    tf_list = tfdf['geneSymbol'].tolist() # get a list of the TFs from the database
    df = gds.table
    df.drop(columns=['ID_REF'], axis=1, inplace = True)
    df = df.dropna() # drop na values if there is any
    genes_gds = df.IDENTIFIER.values.tolist()
    # a list of the TFs in the gds file based on the database
    TFs_in_gds = [x for x in genes_gds if x in tf_list]
    # the dataframe with only expression levels for the TFs
    TFs_expr = df[df['IDENTIFIER'].isin(TFs_in_gds)]
    # In case some of the TFs are duplicated, take the mean expression of the duplicated genes
    TFs_expr2 = TFs_expr.groupby('IDENTIFIER').mean().reset_index()
    # rename identifier to Transcription Factor
    TFs_expr2 = TFs_expr2.rename(columns = {'IDENTIFIER': 'Transcription Factors'})
    # set IDENTIFIER as index and disease_state as columns
    TFs_expr2 = TFs_expr2.set_index('Transcription Factors')
    # Using Goncalo's GEO expertise to pull out the samples' conditions
    Condition = pd.Series(gds.columns.iloc[:, 2])
    TFs_expr2.columns = Condition

    
    # the top 50 TFs with highest SD across the samples just to select something for filtering the very big heatmap
    std_TFs = TFs_expr2.std(axis = 1).sort_values(ascending = False)
    std_50 = pd.DataFrame(std_TFs[0:25])
    df50 = TFs_expr2.loc[std_50.index]

    # using min-max normalization to give relative expression of each TF in each sample
    for sample in TFs_expr2.columns:
        TFs_expr2[sample] = (TFs_expr2[sample] - TFs_expr2[sample].min()) / (TFs_expr2[sample].max() - TFs_expr2[sample].min())
    # displaying only the different conditions    
    condensed_df =  TFs_expr2.groupby(TFs_expr2.columns, axis = 1).mean()
    
    # plotting and saving the figure
    tf_dendo = sns.clustermap(df50, cmap ="coolwarm", figsize = (11,11))
    # save figure in memory for displaying in html
    buf = BytesIO()
    tf_dendo.savefig(buf, format = 'png')
    # embed results in the html output
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    img = f"data:image/png;base64,{data}"
    return [img, condensed_df]




tf_genes = get_transcription_factors_df('tfdata.db') # get the transcription factor genes as a one-column dateframe

