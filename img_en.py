from PIL import Image
#LSB
import cv2

# Convert encoding data into 8-bit binary
# form using ASCII value of characters
def genData(data):

        # list of binary codes
        # of given data
        newd = []

        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

# Pixels are modified according to the
# 8-bit binary data and finally returned
def modPix(pix, data):

    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)

    for i in range(lendata):

        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]

        # Pixel value should be made
        # odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j]% 2 != 0):
                pix[j] -= 1

            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1
                # pix[j] -= 1

        # Eighth pixel of every set tells
        # whether to stop ot read further.
        # 0 means keep reading; 1 means thec
        # message is over.
        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if(pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modPix(newimg.getdata(), data):

        # Putting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

# Encode data into image
def lsbimg_encode(imgpath,secret):
    image = Image.open(imgpath, 'r')
    data = secret
    if(len(data) == 0):
        raise ValueError('Data is empty')
    else:
        newimg = image.copy()
        encode_enc(newimg, data)
        imgname = imgpath.split("/")[-1].split(".")[0]
        imgext = imgpath.split("/")[-1].split(".")[1]
        print("saved as ",imgname)
        newimg.save(str(imgname+imgpath[-4:]), "PNG")

# Decode the data in the image
def lsbimg_decode(imgpath):
    # img = input("Enter image name(with extension) : ")
    image = Image.open(imgpath, 'r')

    data = ''
    imgdata = iter(image.getdata())

    while (True):
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]

        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if (i % 2 == 0):
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            return data

def mask(imagepath,maskpath):
    img = cv2.imread(imagepath)
    watermark = cv2.imread(maskpath)
    print("Image: ",img)
    print("watermark: ",watermark)
        #encoding
    #scaling images
    percent_of_scaling = 20
    new_width = int(img.shape[1] * percent_of_scaling/100)
    new_height = int(img.shape[0] * percent_of_scaling/100)
    new_dim = (new_width, new_height)
    resized_img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)

    wm_scale = 40
    wm_width = int(watermark.shape[1] * wm_scale/100)
    wm_height = int(watermark.shape[0] * wm_scale/100)
    wm_dim = (wm_width, wm_height)

    resized_wm = cv2.resize(watermark, wm_dim, interpolation=cv2.INTER_AREA)

    h_img, w_img, _ = resized_img.shape
    center_y = int(h_img/2)
    center_x = int(w_img/2)
    h_wm, w_wm, _ = resized_wm.shape
    top_y = center_y - int(h_wm/2)
    left_x = center_x - int(w_wm/2)
    bottom_y = top_y + h_wm
    right_x = left_x + w_wm

    #output
    roi = resized_img[top_y:bottom_y, left_x:right_x]
    result = cv2.addWeighted(roi, 1, resized_wm, 0.3, 0)
    resized_img[top_y:bottom_y, left_x:right_x] = result


    imgname = imagepath.split("/")[-1].split(".")[0]
    imgext = imagepath.split("/")[-1].split(".")[1]
    cv2.imwrite(str(imgname+imagepath[-4:]),resized_img)