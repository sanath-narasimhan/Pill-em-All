import os
import requests
#import Reviews_to_tdmatrix as tdm
from flask import Flask, render_template, request
#import back_end as be
import InvertedIndex as ii
 
app = Flask(__name__)

@app.before_first_request
def tdm_generator():
  #if(os.path.isfile('drugDict.dict') and os.path.isfile('drugCorpus.mm')  == False):
  #  tdm.gen_tdm()
  if(os.path.isfile('drugVocab.pickel') == False):
    ii.InvertedIndex()
  
@app.route('/')
def first():
  return render_template("home.html")
 
@app.route('/home')
def home():
    return render_template("home.html")
    
@app.route('/search', methods = ['POST','GET'])
def search():
    return render_template("index.html")

@app.route('/result', methods = ['POST','GET'])
def result():
  if request.method == 'POST':
    query = request.form['search']
    #simmat = be.similarity(str(query))
    #result = be.topk(simmat)
    result = ii.topk(str(query))
    if type(result) != str:
      return render_template("display_result.html", query=query, result=result.to_html())
    else:
      return render_template("display_result.html", query=query, result=result)
    
  
if __name__ == "__main__":
    app.run()