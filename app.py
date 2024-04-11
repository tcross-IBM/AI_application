from flask import send_from_directory, Response, Flask, render_template, request, url_for, redirect, send_file
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from io import BytesIO
import base64 
from transformers import pipeline





#DB_HOST = os.environ.get('DB_HOST', "dbConnect.txt")

#file containing sensitive db information (won't be included in GitHub)
with open("C:/Users/7J5720897/dbConnect.txt", "r") as file:
    uri = file.read().replace("\n", "")


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
fixed = ""
paragraph = ""
bytes = {} #Empty dictionary
#decodedFiles = []
#names = []



def allowed_file(filename):
    print("filename.rsplit('.', 1)[1].lower() = " + filename.rsplit('.', 1)[1].lower())
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/rephrase', methods=('GET', 'POST'))
def rephrase():

    global fixed
    global paragraph

    if request.method=='GET':
        fixed=""

    if request.method=='POST':
        try:
            fixed=""
            paragraph = request.form['resumeParagraph']
            fix_spelling = pipeline("text2text-generation",model="oliverguhr/spelling-correction-english-base")
            fixed = str(fix_spelling(str(paragraph),max_length=2048))
            
            #add pop up message for when I delete from db
            #add loading message when submitting sentence

            fixed = fixed.removeprefix("[{'generated_text': '")
            fixed = fixed.removesuffix("'}]")
            fixed = fixed.removeprefix('[{\'generated_text\': "')
            fixed = fixed.removesuffix('"}]')

        except:
            print("didn't work")

    return render_template('/rephrase.html', fixed = fixed, paragraph = paragraph)

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
                resumes.insert_one({'content': rv, 'filename': content.filename})     #saves to DB    

                #need to add error handling for if same file name was saved to db

                
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

@app.route('/history/', methods=('GET', 'POST'))
def history():

    try:
        allResumes = resumes.find()
        
        #unencrypt pdf 
        for doc in allResumes:
            #dictionary object
            bytes[doc["filename"]] = doc["content"]
            #create two lists , one of names another of decoded strings
            #names.append(doc["filename"])
            #decodedFiles.append(base64.b64decode(doc["content"]))
            

        #need to create delete functionality for pdfs 
 
        return render_template('history.html', resumeNames = bytes)
    except Exception as e:
        return "error!"

@app.route('/pdf/', methods=('GET', 'POST'))
def pdf():
    print(request.args.get('key'))
    if(request.args.get('key')):
        #takes key argument from html
        key = request.args.get('key')
        
        #decrypts pdf
        pdf = base64.b64decode(bytes[key])

        """response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] =  \
            'inline; filename=%s.pdf' % 'yourfilename' """

        return send_file(BytesIO(pdf), 
                     download_name=key, as_attachment=True)

@app.route('/delete/', methods=('GET', 'POST'))
def delete():
    print(request.args.get('key'))
    if(request.args.get('key')):
        #takes key argument from html
        key = request.args.get('key')
        
        try:
            resumes.delete_one({'content': bytes[key], 'filename': key})
            del bytes[key]
        except:
            print("didnt work")
        
        return render_template('history.html', resumeNames = bytes)