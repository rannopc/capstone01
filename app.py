from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2023-01-01,2023-7-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister-list'})
data_list = table.find_all('div', attrs={'class':'lister-item'})

row_length = len(table.find_all('h3', attrs={'class':'lister-item-header'}))

temp = [] #initiating a list 

for i in range(0, row_length):
#insert the scrapping process here
    judul       = data_list[i].find('h3', attrs={'class':'lister-item-header'})
    if judul is None:
        judul = '-'
    else:
        judul = judul.text

    imdb_rating = data_list[i].find('div', attrs={'class':'inline-block ratings-imdb-rating'})
    if imdb_rating is None:
        imdb_rating = '0'
    else:
        imdb_rating = imdb_rating.text
    
    metascore   = data_list[i].find('span', attrs={'class':'metascore'})
    if metascore is None:
        metascore = '0'
    else:
        metascore = metascore.text

    votes       = data_list[i].find('span', attrs={'name':'nv'})
    if votes is None:
        votes = '0'
    else:
        votes = votes.text
        
    temp.append((judul,imdb_rating,metascore,votes))

# temp 

#change into dataframe
data = pd.DataFrame(temp, columns=('judul','imdb_rating','metascore','votes'))

#insert data wrangling here

# 2.a. REMOVE "\n"
data = data.replace('\n','', regex=True)

# 2.b. REMOVE ","
data['votes'] = data['votes'].replace(',','', regex=True)

# 3.a. MENGHAPUS NOMOR DI KOLOM JUDUL (INDEX 0-9)
data10 = data.iloc[0:9,:]
data10['judul'] = data10['judul'].str[2:100]

# 3.b. MENGHAPUS NOMOR DI KOLOM JUDUL (INDEX 10-55)
data11 = data.iloc[9:55,:]
data11['judul'] = data11['judul'].str[3:100]

# 3.c. MENGGABUNGKAN 2 DATAFRAME HASIL SYNTAX DI ATAS
data_union = pd.concat([data10,data11])

# 4. MENGUBAH TIPE KOLOM
data_union['imdb_rating'] = data_union['imdb_rating'].astype('float')
data_union['metascore'] = data_union['metascore'].astype('float')
data_union['votes'] = data_union['votes'].astype('float')
# data_union.dtypes
#end of data wranggling 


# 1. UBAH JUDUL MENJADI INDEX
data_union = data_union.set_index('judul')
# data_union

# # ----------- PLOTTING CHART BY IMDB_RATING -----------
df_imdb_rating = data_union.sort_values('imdb_rating',ascending=False).head(7)
df_imdb_rating = df_imdb_rating.drop(columns=['metascore','votes']).sort_values('imdb_rating',ascending=True)
# # df_imdb_rating

# # ----------- PLOTTING CHART BY METASCORE -----------
df_metascore = data_union.sort_values('metascore',ascending=False).head(7)
df_metascore = df_metascore.drop(columns=['imdb_rating','votes']).sort_values('metascore',ascending=True)
# # df_metascore

# # ----------- PLOTTING CHART BY VOTES -----------
df_votes = data_union.sort_values('votes',ascending=False).head(7)
df_votes = df_votes.drop(columns=['imdb_rating','metascore']).sort_values('votes',ascending=True)
# # df_votes

@app.route("/")
def index():
	
	card_data1 = f'{data_union["imdb_rating"].mean().round(2)}' #be careful with the " and ' 
	card_data2 = f'{data_union["metascore"].mean().round(2)}'
	card_data3 = f'{data_union["votes"].mean().round(2)}'


	# generate plot 1 (by IMDB Rating)
	df_imdb_rating.plot(figsize = (20,9), kind='barh')
	figfile1 = BytesIO()
	plt.savefig(figfile1, format='png', transparent=True)
	figdata_png1 = base64.b64encode(figfile1.getvalue())
    
	# generate plot 2 (by Metascore)
	df_metascore.plot(figsize = (20,9), kind='barh')    
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figdata_png2 = base64.b64encode(figfile.getvalue())
    
	# generate plot 3 (by Votes)
	df_votes.plot(figsize = (20,9), kind='barh')    
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figdata_png3 = base64.b64encode(figfile.getvalue())
    
	# Rendering plot
	# # Do not change this
	# figfile1.seek(0)
	# figfile2.seek(1)
	# figfile3.seek(2)
	plot_result1 = str(figdata_png1)[2:-1]
	plot_result2 = str(figdata_png2)[2:-1]
	plot_result3 = str(figdata_png3)[2:-1]
    
	# render to html
	return render_template('index.html',
		card_data1 = card_data1, 
		plot_result1=plot_result1,
		card_data2 = card_data2, 
		plot_result2=plot_result2,
		card_data3 = card_data3, 
		plot_result3=plot_result3
	)

if __name__ == "__main__": 
    app.run(debug=True)