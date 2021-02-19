#!/usr/bin/env python
# coding: utf-8

# # Packages

# In[12]:


import GEOparse
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn import preprocessing


# # Import GDS file

# In[13]:


def GDSinput(file):
    """Function that takes a GDS file as an input and returns a gds object with 3 
    3 main attributes: metadata, table and columns"""
    
    gds = GEOparse.get_GEO(filepath = file)
    
    return gds


# # Summary table and boxplot

# In[15]:


def get_description(gds):
    """Function that takes gds object as input and outputs metadata related to the GDS file"""
    
    description = gds.metadata
    return description  ########change this to a nice table ##########


# In[17]:


def get_sum(gds):
    """Function that takes gds object as input and outputs a table with simple summary statistics
    of the gene expression data set"""
    df = gds.table
    sumTable = df.describe()
    sumTable = sumTable.rename(index = {"count":"genes"})

    
    return sumTable


# In[21]:


def gene_boxplot(gds):
    """Function that takes a gds object as input and outputs a boxplot 
        of gene expression data for each of the samples in the dataset."""
    
    #preparing data and convert DF to a  2D numpy array
    data2 = gds.table
    data2 = pd.DataFrame(data2[data2.columns[2::]])
    data2 = data2.dropna() #DROP NaN????
    disease_state = pd.Series(gds.columns.iloc[:, 2])
    data2.columns = disease_state
    npArray = data2.to_numpy()
    
    #colours and colour vector
    colors = ["blue","darkorange","red","green","darkorange","dodgerblue","yellow","deeppink","royalblue","aqua","palegreen","coral"]
    emptyDict = {label:col for col,label in zip(colors,np.unique(data2.columns))}
    colourVector = [emptyDict[label] for label in data2.columns]
    
    fig1, ax1 = plt.subplots(figsize=(20,10))
    ax1.set_title("Distribution of Gene Expression Across All Samples",fontsize=20,weight='bold' )
    ax1.set_xlabel("Samples",fontsize=20,weight='bold')
    ax1.set_ylabel("Gene Expression Level",fontsize=20,weight='bold')
    box = ax1.boxplot(npArray,patch_artist=True)
    ax1.legend(np.unique(data2.columns),loc="upper right",labelcolor=colors[0:len(np.unique(data2.columns))])

    for patch, color in zip(box['boxes'], colourVector):
        patch.set_facecolor(color)
    
    bxplot = plt.show()
    
    
    return bxplot


# # PCA

# In[24]:


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
    plt.figure(figsize=(10, 6), dpi=100)
    xxx = plt.scatter(pca_df.PC1, pca_df.PC2, c=cvec)

    plt.title("Principal Component Analysis",fontsize=20,weight='bold')
    plt.xlabel("PC1 - {0}%".format(per_var[0]),fontsize=16,weight='bold')
    plt.ylabel("PC2 - {0}%".format(per_var[1]),fontsize=16,weight='bold')
    h,l = xxx.legend_elements()
    cond = np.unique(df_pca.columns)
    plt.legend(h,cond)
    
   
    #####getting variation####
    Variation_df = pd.DataFrame(per_var,index = labels, columns = ["% Variation"])
    Variation_df = Variation_df.transpose()
    
    
    
    return [xxx, Variation_df]


# In[ ]:



