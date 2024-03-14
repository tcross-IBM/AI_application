from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
import base64 
#from transformers import pipeline


#fix_spelling = pipeline("text2text-generation",model="oliverguhr/spelling-correction-english-base")

#fixed = fix_spelling("Worked as a Full-stack Developer in an Agile environment. Converted batch processes from Java Struts to Java Spring Framework. Worked on front and back-end of GUI application using Struts 2 Framework with languages/technologies including  JSP (Jakarta Server Pages), JavaScript, Java and DB2 SQL. Used user stories to create/modify additional back-end and front-end functionality for both batch processes and GUI application.",max_length=2048)

#file containing sensitive db information (won't be included in GitHub)
with open('C:\\Users\\7J5720897\\dbConnect.txt', "r") as file:
    uri = file.read().replace("\n", "")

print(uri)


#db 
try:
    client = MongoClient(uri, 27017)
    print("\n ******************Connected to DB successfully!****************** \n")
except:
    print("\n ******************Unable to connect to DB****************** \n")

db = client.flask_db
resumes = db.resumes
#end db


app = Flask(__name__)

#global variables & funcs
ALLOWED_EXTENSIONS = ['pdf']
prevLoaded = False
uploaded = False

def allowed_file(filename):
    print("filename.rsplit('.', 1)[1].lower() = " + filename.rsplit('.', 1)[1].lower())
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/rephrase')
def rephrase():
    return render_template('/rephrase.html')

@app.route('/resume', methods=('GET', 'POST'))
def resume():

    global prevLoaded
    global uploaded

    try:
        uploaded = False
        if request.method=='POST': 
            prevLoaded = True

            content = request.files['content']  

            if allowed_file(content.filename):        #calls function to check file type
                rv = base64.b64encode(content.read())  # encodes pdf
                resumes.insert_one({'content': rv})    #saves to DB      
                print("file extension allowed")
            else:
                uploaded = True
                print("file extension not allowed")

            #return redirect(url_for('resume'))
            render_template('/resume.html', value = uploaded, value2 = prevLoaded)
    except:
        print("didnt work")
        #return redirect(url_for('resume'))
        render_template('/resume.html', value = uploaded, value2 = prevLoaded)
    return render_template('/resume.html', value = uploaded, value2 = prevLoaded)

@app.route('/about')
def about():
    return render_template('/about.html')

@app.route('/history', methods=('GET', 'POST'))
def history():
    try:
        allResumes = resumes.find()
        #unencode
        return render_template('history.html',tasks=list(allResumes))
    except Exception as e:
        return "error!"
