from flask import Flask, jsonify, render_template, request, Response, send_from_directory
from python._infer import run_model, run_model_img
import time
import json
from flask_cors import CORS
from waitress import serve
import os
import base64
import shutil
import re
import io
from PIL import Image, ImageDraw, ImageFont

application = app = Flask(__name__)
CORS(app)

public_dir = 'public'

def image_to_data_uri(image_path):
    with open(image_path, 'rb') as image_file:
        data = image_file.read()
        data_uri = 'data:image/png;base64,' + base64.b64encode(data).decode('utf-8')
    return data_uri


@app.route('/public/<path:filename>')
def serve_public_file(filename):
    return send_from_directory(public_dir, filename)

def datauri_to_image(datauri):
    # Extract the base64 part of the data URI
    image_data = re.sub("^data:image/.+;base64,", "", datauri)
    # Decode the base64 image data
    image_data = base64.b64decode(image_data)
    # Create an image from the decoded data
    image = Image.open(io.BytesIO(image_data))
    return image

def superimpose_image_to_datauri(image1_datauri, image2_path, x, y, scale_width, displayed_width, displayed_height):

    # Decode image1 from data URI
    x= int(x)
    y = int(y)
    image1 = datauri_to_image(image1_datauri)
    # Open image2 from file path
    image2 = Image.open(image2_path)
    #display scale:
    display_ratio = image1.width/displayed_width
    display_ratio_height = image1.height/displayed_height
    x = int(x*display_ratio)
    y= int(y*display_ratio)
    # Calculate the scaling factor to maintain aspect ratio
    aspect_ratio = image2.height / image2.width
    new_width = scale_width*display_ratio*0.9
    new_height = int(new_width * aspect_ratio)
    
    # Resize image2
    image2 = image2.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
    
    # Paste image2 on image1 at the specified coordinate
    print(x," y:",y)

    image1.paste(image2, (x, y), image2.convert("RGBA"))
    
    # Save image to a bytes buffer
    buffered = io.BytesIO()
    image1.save(buffered, format="PNG")
    buffered.seek(0)
    
    # Encode as base64 and convert to data URI
    img_str = base64.b64encode(buffered.read()).decode('utf-8')
    data_uri = f"data:image/png;base64,{img_str}"
    # with open("current.txt","w") as f:
    #     f.write(data_uri)
    return data_uri


@app.route('/')
def home():
	return render_template('index.html')

# @app.route('/generate', methods=['POST'])
# def generate():
# 	# receive post
# 	graph_str = request.data.decode('utf-8')
# 	graph_data = json.loads(graph_str)
# 	return Response(run_model(graph_data), mimetype='text/plain')
# serve(app, host='127.0.0.1', port=5000)

@app.route('/generate_floorplans/<session_id>', methods=['GET'])
def create_session_folder(session_id):
    
    session_folder_path = os.path.join(public_dir, session_id)
    image_files = ['V1.png', 'V2.png', 'V3.png', 'V4.png']
    
    if not os.path.exists(session_folder_path):
        os.makedirs(session_folder_path)
    # main(session_folder_path)
    
    images_data_uri = {}
    for image_file in image_files:
        image_path = os.path.join(session_folder_path, image_file)
        if os.path.exists(image_path):
            images_data_uri[image_file.replace(".png","")] = {"dataUri":image_to_data_uri(image_path), "text": "1 BR | 1 BA"}
            # images_data_uri[image_file.replace(".png","")] = image_to_data_uri(image_path)
        else:
            images_data_uri[image_file.replace(".png","")] = None

    
    # if os.path.exists(session_folder_path):
    #     shutil.rmtree(session_folder_path)

    return jsonify(images_data_uri)
# {"nodes":{"0":"bedroom","1":"bedroom","2":"bathroom","3":"bathroom","4":"balcony","5":"living","6":"outside"},"edges":[[2,0],[3,1],[5,0],[5,1],[5,3],[5,4],[6,5]]}


@app.route('/generate_floorplans_test/', methods=['POST'])
def create_session_folder_test():
    session_id= request.data.session_id
    graph_str = request.data.graph_str.decode('utf-8')
    
    run_model_img(graph_str, session_id)
    
    session_folder_path = os.path.join(public_dir, session_id)
    image_files = ['V1.png', 'V2.png', 'V3.png', 'V4.png']
    
    if not os.path.exists(session_folder_path):
        os.makedirs(session_folder_path)
    # main(session_folder_path)
    
    images_data_uri = {}
    for image_file in image_files:
        image_path = os.path.join(session_folder_path, image_file)
        if os.path.exists(image_path):
            images_data_uri[image_file.replace(".png","")] = {"dataUri":image_to_data_uri(image_path), "text": "1 BR | 1 BA"}
            # images_data_uri[image_file.replace(".png","")] = image_to_data_uri(image_path)
        else:
            images_data_uri[image_file.replace(".png","")] = None

    return jsonify(images_data_uri)

@app.route('/generate', methods=['POST'])
def generate():
	# receive post
	graph_str = request.data.decode('utf-8')
	print(graph_str)
	graph_data = {'nodes': {'0': 'bedroom', '1': 'bedroom', '2': 'bathroom', '3': 'bathroom', '4': 'kitchen', '5': 'living', '6': 'outside', '7': 'balcony'}, 'edges': [[0, 5], [0, 2], [0, 3], [1, 5], [1, 2], [1, 3], [2, 5], [2, 0], [2, 1], [3, 5], [3, 0], [3, 1], [4, 5], [6, 5], [7, 5]]}
	# graph_data = json.loads(graph_str)
	print("/n")
	print(graph_data)
	run_model_img(graph_data,"123")
	return "gigi"



serve(app, host='0.0.0.0', port=3200)
