from flask import Flask,jsonify,request
from datetime import datetime
import icr_parser
import json

app = Flask(__name__)


@app.route('/api/healthstatus', methods = ['GET'])
def getHealthstatus():
    return "service is executing"

@app.route('/api/ocrparser', methods = ['POST'])
def extractfields():
    #print(datetime.now())
    req = request.json
    x = req['inputfolder']
    y = req['inputfile']
    response = ''
    try:
        resValues = icr_parser.parse(inputfolder, inputfile);
        response = {'status':1,'response':resValues}
    except ValueError:
           response = {'status':0}
    
    #response=jsonify(response)
    response=json.dumps(response)
    #print(datetime.now())
    print(response)
    return response

   
if __name__ == "__main__":
    app.run(debug=True)
