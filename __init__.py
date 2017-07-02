from flask import Flask, render_template, request, redirect
import requests, numpy as np, pandas as pd, quandl, plotly, json
from statistics import mean 
# -----------------------------------------------------|
app = Flask(__name__)
app.vars={}
feat = ['Open','Close','Range']
quandl.ApiConfig.api_key = 'qpW1K3dKRmmXSQmqQ6sE'

#FUNCTIONS FOR REGRESSION

def lobfandm(xval, yval):#line of best fit and m value
    top=(mean(xval)*mean(yval))-(mean(xval*yval))
    bottom=((mean(xval)*mean(xval))-(mean(xval*xval)))
    m=top/bottom
    c=mean(yval)-m*(mean(xval))
    return m, c;
    
def squarederror(yval_orig, yval_line):
    return sum((yval_orig-yval_line)**2);

def coefficientofdetermination(yval_orig, yval_line):
    ymeanline=[mean(yval_orig) for y in yval_orig]
    squared_error_regression=squarederror(yval_orig, yval_line)
    squared_error_mean=squarederror(yval_orig, ymeanline)
    return [1-(squared_error_regression/squared_error_mean)];

@app.route('/')
def welcomepage():
		return render_template('welcome.html')

@app.route('/homepage')
def homepage():        
        Paragraph="Welcome to frmdotpy! frm stands for Financial Regression Modelling, dotpy otherwise '.py' is the extension for a python script. This website was made using Flask web framework; the majority of the code is written in python (using numpy and pandas)."
        Paragraph1="Sometimes the tracker goes down due to a high amount of calls to Quandl; if this happens please check back soon. "
        Header1="About"
        Header2="Stock Tracker"
        Paragraph2="This is used to track stock prices. Click the image below for a larger preview of the output for stocktracker."
        Header3="Stock Compare"
        Paragraph3="This pages uses regression analysis on two given stocks (for example NVDA and NDAQ) the variables used are the return prices. Click the image below for a larger preview of the output for stock compare."
        Paragraphdisclaimer="Any information provided by this website is generalised and it cannot guarantee the accuracy or reliability of information provided. This website does not serve as financial advice; by using this website you must not rely on information from this website to make a financial decision."
        Headerdisclaimer="Disclaimer"
        return render_template('index.html',paragraph=Paragraph, header=Header1, paragraph1=Paragraph1,
                               headerdisclaimer=Headerdisclaimer, paragraphdisclaimer=Paragraphdisclaimer,
                               paragraph2=Paragraph2, header2=Header2,paragraph3=Paragraph3, header3=Header3)

@app.route('/aboutme')
def cv():
                return render_template('cv.html')

@app.route('/stocktracker/')
def stocktracker():
        return redirect('/stock_tracker_input')

@app.route('/stock_tracker_input',methods=['GET','POST'])
def input():
        if request.method == 'GET':
		return render_template('stock_tracker_input.html')
	else:
		app.vars['ticker'] = request.form['ticker'].upper()
		app.vars['start_year'] = request.form['year']
		try: 
			int(app.vars['start_year'])
			app.vars['tag'] = 'Start year specified as %s' % app.vars['start_year']
		except ValueError: 
			app.vars['start_year'] = ''
			app.vars['tag'] = 'Start year not specified/recognized'
		app.vars['select'] = [feat[q] for q in range(3) if feat[q] in request.form.values()]
                return redirect('/graph')

@app.route('/graph',methods=['GET','POST'])
def graph():
        quandl.ApiConfig.api_key = 'qpW1K3dKRmmXSQmqQ6sE'
	req = 'https://www.quandl.com/api/v3/datasets/WIKI/'
	req = '%s%s.json?&collapse=weekly' % (req,app.vars['ticker'])
	if not app.vars['start_year']=='':
		req = '%s&start_date=%s-01-01' % (req,app.vars['start_year'])
	r = requests.get(req)
	cols = r.json()['dataset']['column_names'][0:5]
	df = pd.DataFrame(np.array(r.json()['dataset']['data'])[:,0:5],columns=cols)
	df.Date = pd.to_datetime(df.Date)
	df[['Open','High','Low','Close']] = df[['Open','High','Low','Close']].astype(float)
	if not app.vars['start_year']=='':
		if df.Date.iloc[-1].year>int(app.vars['start_year']):
			app.vars['tag'] = '%s, but Quandl record begins in %s' % (app.vars['tag'],df.Date.iloc[-1].year)
	app.vars['desc'] = r.json()['dataset']['name'].split(',')[0]
        
        #Paragraph = df
        #Paragraph = "This page shows a stocks: open, high ,low and close. Data is taken from Quandl." 

        dfclose=df['Close']; dfopen=df['Open']; dfdate=df['Date']
       
        graphs = [dict(data=[dict(x=dfdate,y=dfopen,type='scatter',mode='markers',)],
                         layout=dict(title=app.vars['ticker'],xaxis=dict(title='Date'),yaxis=dict(title='Price'))),
                  dict(data=[dict(x=dfdate,y=dfopen,type='scatter')],
                       layout=dict(title=app.vars['ticker'],xaxis=dict(title='Date'),yaxis=dict(title='Price')))
        ]
      
        ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        
	return render_template('graph.html', ids=ids, graphJSON=graphJSON)

#---STOCKCOMPARE------STOCKCOMPARE------STOCKCOMPARE------STOCKCOMPARE------STOCKCOMPARE------STOCKCOMPARE------STOCKCOMPARE---
@app.route('/stockcompare')
def stockcompare():
        return redirect('/stockcompareinput')

@app.route('/stockcompareinput',methods=['GET','POST'])
def stockcompareinput():
        if request.method == 'GET':
		return render_template('stockcompareinput.html')
	else:
		app.vars['ticker1'] = request.form['ticker1'].upper()
                app.vars['ticker2'] = request.form['ticker2'].upper()
		app.vars['start_year'] = request.form['year']
		try: 
			int(app.vars['start_year'])
			app.vars['tag'] = 'Start year specified as %s' % app.vars['start_year']
		except ValueError: 
			app.vars['start_year'] = ''
			app.vars['tag'] = 'Start year not specified/recognized'
		app.vars['select'] = [feat[q] for q in range(3) if feat[q] in request.form.values()]
                return redirect('/stockcomparedata1')

@app.route('/stockcomparedata1',methods=['GET','POST'])
def stockcomparedata1():
        quandl.ApiConfig.api_key = 'qpW1K3dKRmmXSQmqQ6sE'
	req = 'https://www.quandl.com/api/v3/datasets/WIKI/'
	req = '%s%s.json?&collapse=weekly' % (req,app.vars['ticker1'])
	if not app.vars['start_year']=='':
		req = '%s&start_date=%s-01-01' % (req,app.vars['start_year'])
	r = requests.get(req)
	cols = r.json()['dataset']['column_names'][0:5]
	df = pd.DataFrame(np.array(r.json()['dataset']['data'])[:,0:5],columns=cols)
	df.Date = pd.to_datetime(df.Date)
	df[['Open','High','Low','Close']] = df[['Open','High','Low','Close']].astype(float)
	if not app.vars['start_year']=='':
		if df.Date.iloc[-1].year>int(app.vars['start_year']):
			app.vars['tag'] = '%s, but Quandl record begins in %s' % (app.vars['tag'],df.Date.iloc[-1].year)
	app.vars['desc'] = r.json()['dataset']['name'].split(',')[0]

        dfclose=df['Close']
        dfopen=df['Open']
        dfdate=df['Date']
        dfdata1=df
        
	req = 'https://www.quandl.com/api/v3/datasets/WIKI/'
	req = '%s%s.json?&collapse=weekly' % (req,app.vars['ticker2'])
	if not app.vars['start_year']=='':
		req = '%s&start_date=%s-01-01' % (req,app.vars['start_year'])
	r = requests.get(req)
	cols = r.json()['dataset']['column_names'][0:5]
	df = pd.DataFrame(np.array(r.json()['dataset']['data'])[:,0:5],columns=cols)
	df.Date = pd.to_datetime(df.Date)
	df[['Open','High','Low','Close']] = df[['Open','High','Low','Close']].astype(float)
	if not app.vars['start_year']=='':
		if df.Date.iloc[-1].year>int(app.vars['start_year']):
			app.vars['tag'] = '%s, but Quandl record begins in %s' % (app.vars['tag'],df.Date.iloc[-1].year)
	app.vars['desc'] = r.json()['dataset']['name'].split(',')[0]

        df2date=df['Date'];df2open=df['Open'];dfdata2=df
        
        newdf=pd.merge(dfdata1,dfdata2,how='inner',on='Date')

        #Drop Date and nans values
        newdf=newdf.drop(['Date'],axis=1)
        newdf=newdf.pct_change()# find percentage change      

        newdf.fillna(0,inplace=True)
               
        xval=newdf['High_x']
        yval=newdf['High_y']
        
        m,c=lobfandm(xval,yval)
        yrval=[(m*x)+c for x in xval]#regression line y=mx+c
        squared_error_regression=coefficientofdetermination(yval,yrval)
        squared_error_mean=coefficientofdetermination(yval,yval)   
        rsquared=coefficientofdetermination(yval,yrval)
        
        graphs=[dict(data=[dict(x=xval,y=yval,type='scatter',mode='markers'),],
                     layout=dict(title=app.vars['ticker1'],xaxis=dict(title='Return % of independent variable'),
                                 yaxis=dict(title='Return % of dependent variable'))),
                        
                dict(data=[dict(x=xval,y=yrval,type='scatter')],
                     layout=dict(title=app.vars['ticker2'],xaxis=dict(title='Date'),yaxis=dict(title='Price'))),
                
                dict(data=[dict(x=dfdate,y=dfopen,type='scatter'),],
                     layout=dict(title=app.vars['ticker1'],xaxis=dict(title='Date'),yaxis=dict(title='Price'))),
                
                dict(data=[dict(x=df2date,y=df2open,type='scatter'),],
                     layout=dict(title=app.vars['ticker2'],xaxis=dict(title='Date'),yaxis=dict(title='Price'))),
        ]
        
        ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('graph.html', ids=ids, graphJSON=graphJSON, rsquared=rsquared)

@app.route('/websitestatistics',methods=['GET','POST'])
def statsinput():
        
        return render_template('comingsoon.html')
            
#---NEW-SECTION------NEW-SECTION------NEW-SECTION------NEW-SECTION------NEW-SECTION------NEW-SECTION------NEW-SECTION----
@app.route('/untitled2')
def untitled2():
        return render_template("comingsoon.html")
#---ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION---
@app.errorhandler(500)
def error_handler(e):
	return render_template('error.html',ticker=app.vars['ticker'],year=app.vars['start_year'])
@app.errorhandler(404)
def page_not_found(e):
        return render_template("404.html")
#---ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION------ERRORS-SECTION---
if __name__ == '__main__':
  app.run(debug=False)
  
