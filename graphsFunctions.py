# # Packages

import GEOparse
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn import preprocessing
import base64
from io import BytesIO
from matplotlib.figure import Figure
import seaborn as sns


# # Import GDS file

def GDSinput(file):
    """Function that takes a GDS file as an input and returns a gds object with 3 
    3 main attributes: metadata, table and columns"""
    
    gds = GEOparse.get_GEO(filepath = file)
    
    return gds


# # Summary table and boxplot

def get_description(gds):
    """Function that takes gds object as input and outputs metadata related to the GDS file"""
    
    description = gds.metadata
    return description  ########change this to a nice table ##########



def get_sum(gds):
    """Function that takes gds object as input and outputs a table with simple summary statistics
    of the gene expression data set"""
    df = gds.table
    sumTable = df.describe()
    sumTable = sumTable.rename(index = {"count":"genes"})

    
    return sumTable.to_dict()


def gene_boxplot(gds):

    """Function that takes a gds object as input and outputs a boxplot 
        of gene expression data for each of the samples in the dataset."""   

    #preparing data and convert DF to a  2D numpy array

    data2 = gds.table
    data2 = pd.DataFrame(data2[data2.columns[2::]])
    data2 = data2.dropna()
    disease_state = pd.Series(gds.columns.iloc[:, 2])
    data2.columns = disease_state
    npArray = data2.to_numpy()
  

    #colours and colour vector

    colors = ["blue","darkorange","red","green","darkorange","dodgerblue","yellow","deeppink","royalblue","aqua","palegreen","coral"]
    emptyDict = {label:col for col,label in zip(colors,np.unique(data2.columns))}
    colourVector = [emptyDict[label] for label in data2.columns]


    fig = Figure(figsize = (17,17))
    ax1 = fig.subplots()
    ax1.set_xlabel("Samples",fontsize=20,weight='bold')
    ax1.set_ylabel("Gene Expression Level",fontsize=20,weight='bold')
    box = ax1.boxplot(npArray,patch_artist=True)
    ax1.legend(np.unique(data2.columns),loc="upper right",labelcolor=colors[0:len(np.unique(data2.columns))])

    for patch, color in zip(box['boxes'], colourVector):
        patch.set_facecolor(color)

    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    img = f"data:image/png;base64,{data}"
    return img


# # PCA

def pca_plot(gds):
    
    """Function that takes a gds object as input and
    outputs a PCA plot"""
    
    df_pca = gds.table
    df_pca = df_pca.drop("ID_REF", axis=1)
    df_pca = df_pca.set_index("IDENTIFIER")
    
    #changing column names to disease state
    disease_state = pd.Series(gds.columns.iloc[:, 2])
    df_pca.columns = disease_state
    df_pca = df_pca.dropna() #DROP NaN????
    
    #center, scale and transform
    #scale function expects samples to be rows
    scaled_df = preprocessing.scale(df_pca.T)
    
    #create pca object
    pca = PCA()
    
    #call fitt method to calculate loading scores
    pca.fit(scaled_df)
    
    #generate coordenates for PCA graph based on loading scores and scaled data
    pca_data = pca.transform(scaled_df)
    
    #calculate % of variation that each PC accounts for
    per_var = np.round(pca.explained_variance_ratio_*100, decimals=1)
    
    #create labels for Scree Plot. One label per PC
    labels = ["PC" + str(x) for x in range(1, len(per_var)+1)]
    
    #Put new coordinates, created by pca.transform into a matrix
    pca_df = pd.DataFrame(pca_data, index = labels, columns=labels)
    
    ######not sure if this is correct ########
    # Label to color dict (automatic)
    label_color_dict = {label:idx for idx,label in enumerate(np.unique(df_pca.columns))}
    # Color vector creation
    cvec = [label_color_dict[label] for label in df_pca.columns]
    
    #plotting
    fig = Figure(figsize=(17, 17), dpi=100)
    ax = fig.subplots()
    xxx = ax.scatter(pca_df.PC1, pca_df.PC2, c=cvec)

    ax.set_xlabel("PC1 - {0}%".format(per_var[0]),fontsize=16,weight='bold')
    ax.set_ylabel("PC2 - {0}%".format(per_var[1]),fontsize=16,weight='bold')
    h,l = xxx.legend_elements()
    cond = np.unique(df_pca.columns)
    ax.legend(h,cond)
    
    # save figure in memory for displaying in html
    buf = BytesIO()
    fig.savefig(buf, format='png')
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    img = f"data:image/png;base64,{data}"
   
    #####getting variation####
    Variation_df = pd.DataFrame(per_var,index = labels, columns = ["% Variation"])
    Variation_df = Variation_df.transpose()
    
    
    return [img, Variation_df]


def hca(gds):

    """This function takes a gds object as input and
    outputs a a heatmap/dendrogram which allows the user to have a first
    general overview of the data"""
  
    df = gds.table
    df = df.set_index('IDENTIFIER')
    df.drop(columns=['ID_REF'], axis=1, inplace = True)
    df = df.dropna() #if there are any

    disease_state = pd.Series(gds.columns.iloc[:, 2])
    df.columns = disease_state

    df2 = df[~df.index.duplicated(keep="first")] #find the mean     

    # transposing

    df2_trans = df2.T 
    std_genes = df2_trans.std()

    # sorting highest to lowest

    std_genes = std_genes.sort_values(ascending=False)
    std_100genes = pd.DataFrame(std_genes[0:100])
    df100 = df2.loc[std_100genes.index]

    buf = BytesIO()
    
    heatmap_dendo = sns.clustermap(df100, cmap="coolwarm", figsize= (17,17))
    heatmap_dendo.savefig(buf, format = "png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    img = f"data:image/png;base64,{data}"

    return img