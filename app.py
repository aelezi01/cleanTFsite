from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3 as sql
import functions_for_samar
import graphsFunctions
from sqltools import TFsearch_functionalities

# create a flask application object
app_obj = Flask(__name__)
app_obj.secret_key = 'GroupProject-bioinformatics21'


# homepage page 
@app_obj.route('/')
@app_obj.route('/home')
def home():    
    return render_template('home.html')


# TFs pages

## the search TF page will redirect the user to a page with all the information needed about the specific TF requested
@app_obj.route('/TF/', methods=['GET', 'POST'])
def TF_search():
    if request.method == 'POST':
        protein = request.form['TF_protein'].upper()

        # connect to the database
        con = sql.connect('tfdata.db')
        c = con.cursor()
        # search for the protein within the database
        symbol = (protein,)
        c.execute('SELECT * FROM transcriptionFactors WHERE geneSymbol =?', symbol)
        searchedTF = c.fetchone()

        if searchedTF:
            return redirect(url_for('TF', TF_name = protein))
        else:
            # close the connection to the database
            c.close()
            con.close()
            flash('The protein searched is not present in our database' + '\t')

            similar_results = TFsearch_functionalities(protein)
            if similar_results:
                flash('Did you mean one of these TFs instead?' + '\t')
                for item in similar_results:
                    flash(item)
                

            return render_template('TF_search.html')
    else:
        return render_template('TF_search.html')


@app_obj.route('/TF/<TF_name>/')
def TF(TF_name):
    # connect to the database
    con = sql.connect('tfdata.db')
    with con:
        c = con.cursor()

        # select the whole row and fetch it
        resultTF = (TF_name,)
        c.execute("SELECT * FROM transcriptionFactors WHERE geneSymbol=?", resultTF)
        result = c.fetchone()

        #set up variables with info from the various fields so that they can be called within the html file
        proteinNames = result[1]
        ensemblID = result[2]
        entrezID = result[3]
        pdbID = result[4]
        uniprotID = result[5]
        DBD = result[6]

        c.close()
        # return page with the information fetched from the database
        return render_template('TF.html', TF_name = TF_name, ensemblID = ensemblID, entrezID = entrezID, pdbID = pdbID, uniprotID = uniprotID, DBD = DBD) 


# drugs pages

## the search drugs page will redirect the user to a page with all the information needed about the specific drug requested
@app_obj.route('/drugs/', methods=['GET', 'POST'])
def drugs_search():
    if request.method == 'POST':
        drug = request.form['drugs_search']

        # connect to the database
        con = sql.connect('tfdata.db')
        c = con.cursor()
        # search for the drug within the different tables of the database
        symbol = (drug,)
        c.execute('SELECT * FROM drugs INNER JOIN drugsTF ON drugs.drugChemblID = drugsTF.drugChemblID WHERE name=?', symbol)
        searchedDrug = c.fetchall()

        if searchedDrug:
            return redirect(url_for('drugs', drug_name = drug))
        else:
            # close the connection to the database
            c.close()
            con.close()
            flash('The drug searched is not present in our database')
            return render_template('drugs_search.html')
    else:
        return render_template('drugs_search.html')


@app_obj.route('/drugs/<drug_name>/') 
def drugs(drug_name):
    # connect to the database
    con = sql.connect('tfdata.db')
    with con:
        c = con.cursor()

        # select the whole row and fetch it
        resultDrug = (drug_name,)
        c.execute("SELECT * FROM drugs INNER JOIN drugsTF ON drugs.drugChemblID = drugsTF.drugChemblID WHERE name=?", resultDrug)
        result1 = c.fetchone()

        #set up variables with info from the various fields so that they can be called within the html file
        chemblID = result1[1]
        drugName = result1[2]
        INCHIkey = result1[3]

        # gather information to display in the TF/drugs table
        c.execute("""SELECT drugs.name, drugsTF.drugChemblID, drugsTF.bindingSiteName,
        drugsTF.drugMechanism FROM drugs
        INNER JOIN drugsTF ON drugs.drugChemblID = drugsTF.drugChemblID
        INNER JOIN transcriptionFactors ON drugsTF.uniprotID = transcriptionFactors.uniprotID
        WHERE transcriptionFactors.geneSymbol=?""", resultDrug)
        result2 = c.fetchall()
        result_list = [list(tuple) for tuple in result2]

        return render_template('drugs.html', drug = drug_name, chemblID = chemblID, drugName = drugName, INCHIkey = INCHIkey)


# upload data pages

## this function checks if file is in allowed format
def allowed_file(filename):
    """ returns True if file extension = gds or soft """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ["gds","soft", "tsv", "csv"]

## this page allows the user to upload the GEO dataset
@app_obj.route('/upload_data/', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST':
        new_file = request.form['file']
        if new_file is allowed_file == True:
            return redirect(url_for('stat_analysis', newdata = new_file))
        else:
            flash('The file uploaded is not compatible with our analysis tools.' + '\t' + 'Please upload a gds, soft, tsv or csv file instead.')
            return render_template('upload_data.html')
    else:
        return render_template('upload_data.html')

## this page allows the user to access statistical analysis of their dataset
@app_obj.route('/upload_data/<newdata>/')
def stat_analysis(newdata):
    new_file = request.form['file']

    PCAgraph = request.form['PCA']
    HCAgraph = request.form.ge


    gds = GDSinput(newdata)
    metadata = get_description(gds)
    simpleStatistic = get_sum(gds)
    boxplot = gene_boxplot(gds)
    PCA = pca_plot(gds)
    
    return render_template('stat_analysis.html')
#    return 'you will be able to upload data for %s soon' % newdata_name


# contact us pages

comments = []

@app_obj.route('/contactus/', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        user = request.form['nm']
        email = request.form['email']
        comment = request.form['comments']

        comments.append(f'{user} , {email} , {comment}')

        return redirect(url_for('user', usr=user))
    else:
        return render_template('contactus.html')

@app_obj.route('/contactsus/<usr>') 
def user(usr):
    return render_template('thankyou.html')



# start the web server
if __name__ == '__main__':
    app_obj.run(debug = True)