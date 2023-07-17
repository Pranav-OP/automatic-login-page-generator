from flask import Flask, request, jsonify, render_template, flash, redirect,url_for, send_from_directory
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import os
import pandas as pd
from urllib import response
from main import final

import urllib.request
import json
import cv2
import datetime

app = Flask(__name__, static_url_path='/uploads')
app.secret_key = "secret key"
app.config["DEBUG"] = True
api = Api(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    print(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)


@app.route('/', methods=['GET'])
def home():
    return render_template('upload.html')


@app.route('/uploader', methods = ['GET','POST'])
def upload_file():
   if request.method == 'POST':
      
      img = request.files['img']
      json = request.files['json']
      bg_img = request.files['bg_img']


      if img.filename == '' or json.filename == '' or bg_img.filename == '':
        column1_text = "Please Enter Valid Input Files"
        column2_text = "Please Enter Valid Input Files"
        flash('No file selected for uploading')
        return render_template('display.html', column1_text=column1_text, column2_text=column2_text)
      

      if img and allowed_file(img.filename):
          
          filename = secure_filename(img.filename)
          img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
          img.save(img_path)

          filename = secure_filename(json.filename)
          json_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
          json.save(json_path)

          filename = secure_filename(bg_img.filename)
          bg_img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
          bg_img.save(bg_img_path)

          try:
            lst = final(img_path, json_path, bg_img_path)
            
            if lst[0]=='' or lst[1]=='':
              column1_text = "Please Enter Valid Input Files"
              column2_text = "Please Enter Valid Input Files"
            else:
              column1_text = lst[0]
              column2_text = lst[1]
            return render_template('display.html', column1_text=column1_text, column2_text=column2_text)
          
          except Exception as e:
            print(e)
            flash('Something went wrong, please try again',e)
            return render_template('display.html')
          

      else:
          flash('Allowed file types are png, jpg, jpeg')
          return redirect(request.url)
   else:
        flash('')
  


if __name__ == '__main__':
    app.run()