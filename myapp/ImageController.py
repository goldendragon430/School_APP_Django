import cv2
import fitz
import numpy as np
import easyocr
def extract_image_pdf(pdfpath):
    doc = fitz.open(pdfpath)
    # for page in doc:
    for i in range(12,20) :
        pix = doc[i].get_pixmap()
        pix.save(f'outfile{i}.png')
    # break
def is_true_image(thresh):
    # Count the number of black pixels
    black_pixels = np.count_nonzero(thresh == 0)
    # Calculate the total number of pixels
    total_pixels = thresh.shape[0] * thresh.shape[1]
    # Calculate the percentage of black pixels
    percent_black = (black_pixels / total_pixels) * 100
    
    return percent_black > 40 and percent_black < 70
def extract_border_lines(image):
    height, width, _ = image.shape
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize=3)
    lines = cv2.HoughLinesP(edges,1,np.pi/180,threshold=140,minLineLength=100,maxLineGap=10)
    min_x = 9999 
    min_y = 9999
    max_x = 0
    max_y = 0
    for line in lines:
        x1, y1, x2, y2 = line[0]  # Extract line endpoints
        if y1 > height * 0.3:
            if min_x > x1:
                min_x = x1
            if min_x > x2:
                min_x = x2
            if max_x < x1:
                max_x = x1
            if max_x < x2:
                max_x = x2
            
            if min_y > y1:
                min_y = y1
            if min_y > y2:
                min_y = y2
            if max_y < y1:
                max_y = y1
            if max_y < y2:
                max_y = y2
    cv2.line(image, (min_x, min_y), (max_x, min_y), (0, 255, 0), 1)
    cv2.line(image, (min_x, min_y), (min_x, max_y), (0, 255, 0), 1)
    cv2.line(image, (min_x, max_y), (max_x, max_y), (0, 255, 0), 1)
    cv2.line(image, (max_x, min_y), (max_x, max_y), (0, 255, 0), 1)
    cv2.line(image, ( int((min_x + max_x)/2), min_y), (int((min_x + max_x)/2), max_y), (0, 255, 0), 1)
    
    
    return min_x,max_x,min_y,max_y
def get_line_info(reader, solution_image,flag = False):

    original_height, original_width, _ = solution_image.shape
    solution_image = cv2.resize(solution_image, (8 * original_width, 8 * original_height))
    for i in [200,180,160,140,120]:
        ret, thresh = cv2.threshold(solution_image, i, 255, 0)
        result2 = reader.readtext(thresh)
        if len(result2) > 0 and (result2[0][1] == 'A' or result2[0][1] == 'B' or result2[0][1] == 'C' or result2[0][1] == 'D' or result2[0][1] == 'E' or result2[0][1] == '8' or result2[0][1] == '9' ):
            break
        # if flag == True:
        #     print(result2)
    result_letter = ''
    try:
        result_letter = result2[0][1]
        if result_letter == '8' or result_letter == '9' :
            result_letter = 'B'
    except:
        pass
    return result_letter

def OCR_TEST_IMG(img_path):
    reader = easyocr.Reader(['en'])
    image = cv2.imread(img_path)
    min_x,max_x,min_y,max_y = extract_border_lines(image)
    height, width, _ = image.shape
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 180, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    result = []
    for i in range(25):
        result.append('')
    for contour in contours:
         if len(contour) > 8:
            ellipse = cv2.fitEllipse(contour) 
            (x, y), (major_axis, minor_axis), angle = ellipse

            # Calculate the aspect ratio of the ellipse
            aspect_ratio = major_axis / minor_axis

            # Check if the aspect ratio is within a certain range to consider it as an ellipse
            if  0.3 < aspect_ratio and major_axis > 10 and angle < 160 and y > height/3:
                # Draw the contour
                x, y, w, h = cv2.boundingRect(contour)
                # Extract the subimage within the bounding rectangle
                subimage = thresh[y:y+h, x:x+w]
                # Display the subimage
                if is_true_image(subimage) == True:
                    line_number = int((y - min_y - 20) * 13 /(max_y - min_y - 20)) + 1
                    if x > (min_x + max_x)/2:
                        line_number = line_number + 13
                    solution_image = image[y - 20 : y, x:x+w]
                    
                    result_letter = get_line_info(reader,solution_image,line_number == 8)
                    
                    if result_letter != '':
                        cv2.drawContours(image, [contour], -1, (0, 255, 0), 1)
                        result[line_number - 1] = result_letter
                    else:
                        if line_number < 20:
                            cv2.drawContours(image, [contour], -1, (0, 255, 0), 1)
                            # print(f'Line {line_number} : A')
                            result[line_number - 1] = result_letter

    return result;