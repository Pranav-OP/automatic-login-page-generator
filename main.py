import cv2
import json
import numpy as np
import cv2
from PIL import Image
import pytesseract
from pytesseract import Output
# import matplotlib.pyplot as plt

def final(imgpath, json_file, bg_img):


    # Reading an image
    # imgpath = input("Enter the path of the Figma / Image :")

    # # Input for metadata
    # json_file = input("Enter the path of the metadata json file :")

    # # Input for background Image
    # bg_img = input("Enter the path of the background Image :")
    # bg_img = bg_img.replace("\\", "//")

    # -------------------------------------------------------------------------------------------- #

    # Reading image through opencv to avoid numpy reading conflicts
    img = cv2.imread(imgpath)
    print(img.shape)

    # convert to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Canny Edge Detection
    img_canny = cv2.Canny(image=img_gray, threshold1=50, threshold2=100)

    # dialation
    kernel = np.ones((3, 3), np.uint8)
    img_dilate = cv2.dilate(img_canny, kernel, iterations=1) 

    # erosion
    kernel = np.ones((3, 3), np.uint8)
    img_erode = cv2.erode(img_dilate, kernel, iterations=1) 

    # Thresholding
    ret, img_thresh = cv2.threshold(img_erode, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)

    # --------------------------------------------------------------------------------------------------------------------- #

    # Finding rectangle co-ordinates in image

    # Find contours in the image
    contours, _ = cv2.findContours(img_thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

    rectangles = []

    for cnt in contours:
        # Approximate the contour to a polygon
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)   
        
        if len(approx) == 4:
            x,y,w,h = cv2.boundingRect(cnt)
            if (w > 300 and w < 400 and h > 40 and h < 100):
                rectangles.append([(x, y), (x+w, y), (x, y+h), (x+w, y+h)])


    for i, rect in enumerate(rectangles):
        print("Rectangle", i+1)
        print("Top left corner: ({}, {})".format(rect[0][0], rect[0][1]))
        print("Top right corner: ({}, {})".format(rect[1][0], rect[1][1]))
        print("Bottom left corner: ({}, {})".format(rect[2][0], rect[2][1]))
        print("Bottom right corner: ({}, {})".format(rect[3][0], rect[3][1]))
        print('\n')

    print(rectangles)

    # --------------------------------------------------------------------------------------------------------------------- #

    # Detecting the button by applying OCR on rectangles to check whether it consists the text or not

    button_list = ['signin', 'signup', 'login', 'submit']
    button_details = []

    img = Image.open(imgpath)

    for i in range(len(rectangles)):
        
        img_crop = img.crop((rectangles[i][0][0], rectangles[i][0][1], rectangles[i][-1][0], rectangles[i][-1][1]))
        img_crop.save(f'C:/Users/Star/Desktop/Prismatic/Images/Button_OCR_{i}.png', quality=95)
        
        # display(img_crop)
        
        tempp = np.array(Image.open(f'C:/Users/Star/Desktop/Prismatic/Images/Button_OCR_{i}.png'))
        text = pytesseract.image_to_string(tempp)
        
        for k in button_list:
            if ( (text.lower().replace(" ", "") ).find(k) != -1 ):
                print(f"Button {i+1} -> Text : {text.strip()}, Location: Top left - ({rectangles[i][0][0]}, {rectangles[i][0][1]}), Bottom Right - ({rectangles[i][-1][0]}, {rectangles[i][-1][1]})")
                button_details.append([text.strip(), (rectangles[i][0][0], rectangles[i][0][1]), (rectangles[i][-1][0], rectangles[i][-1][1])])

    print(button_details)

    # --------------------------------------------------------------------------------------------------------------------- #

    # Finding Text co-ordinates of text from image


    
    # Read image to extract text from image
    # img = cv2.imread(r'C:/Users/Star/Desktop/Prismatic/Images/signup.png')
    img = cv2.imread(imgpath)
    
    # Convert image to grey scale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Converting grey image to binary image by Thresholding
    thresh_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # configuring parameters for tesseract
    custom_config = r'--oem 3 --psm 6'

    # Get all OCR output information from pytesseract
    ocr_output_details = pytesseract.image_to_data(thresh_img, output_type = Output.DICT, config=custom_config, lang='eng')

    # Total bounding boxes
    n_boxes = len(ocr_output_details['level'])

    text_details = [] 
    possible_list = ['login', 'password', 'username', 'submit', 'signup', 'signin', 'email']

    # Extract and draw rectangles for all bounding boxes
    for i in range(n_boxes):
        (x, y, w, h) = (ocr_output_details['left'][i], ocr_output_details['top'][i], ocr_output_details['width'][i], ocr_output_details['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        if (len(ocr_output_details['text'][i])>4) and (ocr_output_details['text'][i].isalnum()==True):
            for j in possible_list:
                if( (ocr_output_details['text'][i].strip().lower()).find(j) != -1):
                    print(f"Text : {ocr_output_details['text'][i]}, Location: Top left- ({x},{y}), Bottom Right-({x+w},{y+h})")
                    text_details.append([ocr_output_details['text'][i], (x,y), (w,h)])

    print()
    print(text_details)

    # --------------------------------------------------------------------------------------------------------------------- #

    # Creating the HTML file
    file_html = open("templates/exam_demo.html", "w")

    # Adding the input data to the HTML file
    file_html.write(f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Form 1</title>
        <link rel="stylesheet" href="exam_demo.css">
    </head>
    <body>
        <div class="left"></div>

        <div class="right">
            <div class="box">
                <h1>{text_details[0][0]}</h1>
                <form class="form">
                    <label for="email" id="email_label"> {text_details[1][0]} </label><br>
                    <input type="text" id="email"><br><br>

                    <label for="password" id="password_label"> {text_details[2][0]} </label><br>
                    <input type="text" id="password" ><br><br>

                    <input type="checkbox" id="rem" value="yes">
                    <label for="rem">Remember</label><br><br>

                    <input type="submit" id="butt" value="{button_details[0][0]}"><br>
                </form>
            </div> 
        </div>
    </body>
    </html>
    ''')

    # Saving the data into the HTML file
    file_html.close()

    # --------------------------------------------------------------------------------------------------------------------- #

    # Input meta-data from figma

    with open(json_file) as f:
        figma_data = json.load(f)

    # figma_data = {
    #     "theme_id": 1 ,
    #     "body_details": {"width":"1920px","height":"1080px","background":"#E8EAE0"},
    #     "img_details" : {"background":"url('./background.png')"},
    #     "box_details" : {"background":"#FFFFFF", "border-radius":"10px", "box-shadow":"0px 0px 10px rgba(99, 88, 220, 0.2)"},
    #     "button_details" : {"width":"350px","height":"50px","font-weight":"400","font-size":"14px","background":"#637A30","color":"#FFFFFF","line-height":"22px"}
    # }

        # figma_data["img_details"]["background"] = f"url('{bg_img}')"

    print(figma_data)


    # --------------------------------------------------------------------------------------------------------------------- #

    
    bgg = '../uploads/background.png'

    # Creating the CSS file
    file_css = open("templates/exam_demo.css", "w")

    # Adding the input data to the CSS file
    file_css.write(f'''

    :root {{
        --w: {figma_data["body_details"]['width']};
        --h: {figma_data["body_details"]['height']};
        --font: 'Helvetica';
        --bg_url: "url('{bgg}')";

        --body_color: {figma_data["body_details"]['background']};
        --button_color: {figma_data["button_details"]['background']};
        --button_text_color: {figma_data["button_details"]['color']};

        --box_color: {figma_data["box_details"]['background']};
        --box_shadow: {figma_data["box_details"]['box-shadow']};
        --box_w: 684px;
        --box_h: 682px;
    }}

    body{{
        margin: 0;              
        padding: 0;             
        position: relative;     
        font-style: normal;     

        width: var(--w);
        height: var(--h);
        background: var(--body_color);
        font-family: var(--font);
    }}

    .left{{
        width: 40%;       /*ASSUMED*/
        height: 100%;     /*ASSUMED*/
        float: left;      /*ASSUMED*/

        background: url("{bgg}");
    }}

    /*ASSUMED*/
    .right{{
        width: 60%;
        height: 100%;
        float: right;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    /*ASSUMED*/
    input[type="checkbox"]{{
        transform: scale(1.3);
    }}

    .right .box{{
        padding: 150px;   /*ASSUMED*/

        border-radius: {figma_data["box_details"]['border-radius']};
        background: var(--box_color);
        box-shadow: var(--box_shadow);
    }}

    .right .box .form #email{{
        width: {rectangles[1][1][0]-rectangles[1][0][0]}px;
        height: {rectangles[1][-1][1]-rectangles[1][0][1]}px;
    }}

    .right .box .form #password{{
        width: {rectangles[2][1][0]-rectangles[2][0][0]}px;
        height: {rectangles[2][-1][1]-rectangles[2][0][1]}px;
    }}

    .right .box .form #email_label{{
        font-weight: 600;
        font-size: 16px;
        line-height: 22px;
    }}

    .right .box .form #password_label{{
        font-weight: 600;
        font-size: 16px;
        line-height: 22px;
    }}

    .right .box #butt{{
        width: {figma_data["button_details"]['width']};
        height: {figma_data["button_details"]['height']};
        padding: 10px;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        background: var(--button_color);
        color: var(--button_text_color);

        font-weight: {figma_data["button_details"]['font-weight']};
        font-size: {figma_data["button_details"]['font-size']};
        line-height: {figma_data["button_details"]['line-height']};
    }}

    ''')

    # Saving the data into the CSS file
    file_css.close()

    # ----------------------- Returning the created code data ----------------------- #

    with open("templates/exam_demo.html", "r") as f:
        html_code = f.read()
    
    with open("templates/exam_demo.css", "r") as f:
        css_code = f.read()

    return [html_code, css_code]
    