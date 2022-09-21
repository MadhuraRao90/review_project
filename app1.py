from flask import Flask,jsonify,request,render_template
import requests
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as ureq
import logging as lg
from csv import DictWriter
lg.basicConfig(filename='flipkart.log',level=lg.DEBUG)

app=Flask(__name__)

@app.route('/',methods=['GET']) # route to display the home page
@cross_origin()
def home_page():
    return render_template('index.html')

@app.route('/review',methods=['GET','POST'])
@cross_origin()
def index():
     if request.method=='POST':
        try:
            searchstring=request.form['content'].replace(" ","")
            flipkarturl="https://www.flipkart.com/search?q="+searchstring

            uclient=ureq(flipkarturl)
            flipkart_page=uclient.read()
            uclient.close()

            flipkart_html=bs(flipkart_page,"html.parser")
            bigboxes=flipkart_html.find_all('div',{"class":"_1AtVbE col-12-12"})
            box=bigboxes[4]
            prod_link="https://www.flipkart.com"+box.div.div.div.a['href']
            prod_res=requests.get(prod_link)
            prod_res.encoding='utf-8'
            prod_html=bs(prod_res.text,'html.parser')
            product_name=prod_html.find_all('span',{'class':'B_NuCI'})[0].text
            reviews=[]
            headers="Product,Name,Rating,CommentHead,comment \n"
            headers_lst=['Product','Name','Rating','CommentHead','Comment']
            filename=searchstring+".csv"
            fw=open(filename,"a+")
            fw.write(headers)

            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            for comments in commentboxes:
                try:
                    rating = comments.div.div.div.div.text
                except:
                    print("no rating")
                try:
                    comment_head = comments.div.div.div.p.text
                except:
                    print("no comment head")
                try:
                    long_comments = comments.div.div.find_all('div', {"class": ""})[0].text
                except:
                    print("no long comments")
                try:
                    name = commentboxes[0].div.div.find_all('p', {"class": "_2sc7ZR _2V5EHH"})[0].text
                except:
                    print("no name of the person")
                try:
                    my_dict = {'Product':product_name,"Name": name, "Rating": rating, "CommentHead": comment_head, "Comment": long_comments}
                    reviews.append(my_dict)
                    dictwriter_object=DictWriter(fw,fieldnames=headers_lst)
                    dictwriter_object.writerow(my_dict)

                except Exception as e:
                    print("error in creating a dictionary", e)
            fw.close()
            return render_template('results.html',reviews=reviews[0:len(reviews)])


        except Exception as e:
            print(e)

if __name__=='__main__':
    app.run(debug=True)