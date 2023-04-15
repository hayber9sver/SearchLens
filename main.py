from pycoreimage.pyci import *
import numpy as np
import objc
import Vision
import CoreML
import Quartz
from Foundation import NSDictionary
import time
import cv2
# Press the green button in the gutter to run the script.
#notice: the numpy to CIImage that range need to [0~1]

def make_request_handler(results):
    """ results: list to store results """
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    def handler(request, error):
        if error:
            print(f"Error! {error}")
        else:
            observations = request.results()
            for text_observation in observations:
                recognized_text = text_observation.topCandidates_(1)[0]
                results.append([recognized_text.string(), recognized_text.confidence()])
    return handler

if __name__ == '__main__':
    count = 70
    timeaverage = 0
    i = 0
    while i < 70:
        img = cimg.fromFile("/Users/xuzhilei/Desktop/flyff_pic/screenshot_" + str(i) +".jpg")
        width, height = img.size
        print("width: ", width, "height: ", height)
        body_image = img.crop(206, 1292 - 200, 514 - 206, 200 - 64)
        start_time = time.time()
        vision_options = NSDictionary.dictionaryWithDictionary_({})
        vision_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
            body_image.ciimage, vision_options
        )
        results = []
        handler = make_request_handler(results)
        vision_request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
        error = vision_handler.performRequests_error_([vision_request], None)
        end_time = time.time()
        timeaverage = timeaverage + (end_time - start_time)
        print("cost time :", (end_time - start_time))
        for result in results:
            print(result)
        i = i + 1
    print("average time : ", timeaverage/70.0)
    # show(body_image, title='body')