from pycoreimage.pyci import *
import numpy as np
import objc
import Vision
import ctypes

from Quartz import *
import CoreMedia
from Foundation import NSDictionary
import time
import cv2
# Press the green button in the gutter to run the script.
#notice: the numpy to CIImage that range need to [0~1]

def topbottomConv (height, y):
    return height - y

def make_request_handler(results, width, height):
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
                textrect = text_observation.boundingBox()
                textrect.origin.x *= width
                textrect.origin.y *= height
                textrect.size.width *= width
                textrect.size.height *= height
                results.append([recognized_text.string(), recognized_text.confidence(), textrect])
    return handler

class BodyStatus:

    # Initializing
    def __init__(self):
        self.vision_handler = Vision.VNImageRequestHandler.alloc()
        self.vision_request = Vision.VNRecognizeTextRequest.alloc()
    def inputimage(self, cimage, recrect):
        width, height = cimage.size
        #origin blx = 74, bly = 92, trx = 218 try = 28 (base on 1200, 983)
        body_image = cimage.crop(recrect)
        self.vision_handler.initWithCIImage_options_(body_image.ciimage, None)
        results = []
        handler = make_request_handler(results, width, height)
        self.vision_request.initWithCompletionHandler_(handler)
        error = self.vision_handler.performRequests_error_([self.vision_request], None)
        return results
    # Calling destructor
    def __del__(self):
        self.vision_handler.dealloc()
        self.vision_request.dealloc()

class TargetTrajectory:
    # Initializing
    def __init__(self):
        self.OpticalRequest = Vision.VNGenerateOpticalFlowRequest.alloc()
        self.ContourRequest = Vision.VNDetectContoursRequest.alloc()
        self.vision_handler = Vision.VNImageRequestHandler.alloc()
        self.GetMaxFilter = CIFilter.filterWithName_("CIMaximumComponent")
        self.GetMaxFilter = CIFilter.filterWithName_("CIMaximumComponent")
        self.BinaryFilter = CIFilter.filterWithName_("CIColorThreshold")
        self.GetMaxFilter.setDefaults()
        self.first_flag = True
        self.optical_result = None
    def get_flag(self):
        return self.first_flag
    def rest_flag(self):
        self.first_flag = True
    def detectlist(self, cur_image): # CIImage
        box_list = []
        if self.first_flag :
            self.first_flag = False
            self.optical_result = self.OpticalRequest.initWithTargetedCIImage_options_(cur_image, None)
        else :
            self.vision_handler.initWithCIImage_options_(cur_image, None)
            self.vision_handler.performRequests_error_([self.OpticalRequest], None)
            # VNPpixelobservations is kCVPixelFormatType_TwoComponent32Float
            VNPpixelobservations = self.optical_result.results()[0]
            ciimage = CIImage.imageWithCVPixelBuffer_(VNPpixelobservations.pixelBuffer())
            self.GetMaxFilter.setValue_forKey_(ciimage, "inputImage")
            self.BinaryFilter.setValue_forKey_(self.GetMaxFilter.outputImage(), kCIInputImageKey)
            self.BinaryFilter.setValue_forKey_(1, "inputThreshold")
            self.vision_handler.initWithCIImage_options_(self.BinaryFilter.outputImage(), None)
            contours_results = self.ContourRequest.init()
            self.vision_handler.performRequests_error_([self.ContourRequest], None)

            origin_width, origin_height = cur_image.extent().size
            for contours_observation in contours_results.results():
                # print("totual courtor: ", contours_observation.contourCount(),
                      # " top counts: ", contours_observation.topLevelContourCount())
                for idx_cour in range(contours_observation.contourCount()):
                    contour, contour_err = contours_observation.contourAtIndex_error_(idx_cour, None)
                    raw_bounding = CGPathGetBoundingBox(contour.normalizedPath())
                    if raw_bounding.size.width < 0.4 and raw_bounding.size.height < 0.4:
                        raw_bounding.origin.x *= origin_width
                        raw_bounding.origin.y *= origin_height
                        raw_bounding.size.width *= origin_width
                        raw_bounding.size.height *= origin_height
                        box_list.append(raw_bounding) # this is for current
            self.optical_result = self.OpticalRequest.initWithTargetedCIImage_options_(cur_image, None)
        return box_list
    # Calling destructor
    def __del__(self):
        self.OpticalRequest.dealloc()
        self.ContourRequest.dealloc()
        self.vision_handler.dealloc()
if __name__ == '__main__':
    count = 800
    timeaverage = 0
    i = 1
    targetlock = TargetTrajectory()
    while i < count:
        img_cur = cimg.fromFile("/Users/xuzhilei/Desktop/flyff_pic/screenshot_" + str(i) + ".jpg")
        s_time = time.time()
        target_list = targetlock.detectlist(img_cur.ciimage)
        e_time = time.time()
        if target_list :
            context = CIContext.contextWithOptions_(None)
            origin_width, origin_height = img_cur.ciimage.extent().size
            drawImage = context.createCGImage_fromRect_(img_cur.ciimage, img_cur.ciimage.extent())
            width = CGImageGetWidth(drawImage)
            height = CGImageGetHeight(drawImage)
            bits_per_component = CGImageGetBitsPerComponent(drawImage)
            bits_per_pixel = CGImageGetBitsPerPixel(drawImage)
            bytes_per_row = CGImageGetBytesPerRow(drawImage)
            color_space = CGImageGetColorSpace(drawImage)
            bitmap_info = CGImageGetBitmapInfo(drawImage)
            provider = CGImageGetDataProvider(drawImage)
            data = CGDataProviderCopyData(provider)

            context = CoreGraphics.CGBitmapContextCreate(data, width, height, bits_per_component,
                                                         bytes_per_row,  color_space, bitmap_info)
            CoreGraphics.CGContextSetRGBFillColor(context, 1, 0, 0, 1)
            for target_box in target_list:
                CoreGraphics.CGContextStrokeRect(context,  target_box)
                CoreGraphics.CGContextSetLineWidth(context, 5.0)

            cimg(CIImage.imageWithCGImage_(drawImage)).save("/Users/xuzhilei/Desktop/flyff_optical/optical_" + str(i) + ".png")
        # outputImage.save("/Users/xuzhilei/Desktop/flyff_optical/optical_" + str(i) + ".png")
        print( "fig: " + str(i), "Tims :" + str(e_time - s_time))
        # for result in results:
        #     print(result)
        i = i + 1

    print("average time : ", timeaverage/70.0)



    # average_filter = CIFilter.filterWithName_("CIAreaAverage")
    # average_filter.setValue_forKey_(GetMaxFilter.outputImage(), kCIInputImageKey)
    # average_filter.setValue_forKey_(
    #     CIVector.vectorWithX_Y_Z_W_(0, 0, ciimage.extent().size.width,ciimage.extent().size.height),
    #     kCIInputExtentKey)
    # aver_raw = average_filter.outputImage()
    # average = cimg.realize_numpy_from_ciimage(average_filter.outputImage())
    # thres = average[0][0][0]