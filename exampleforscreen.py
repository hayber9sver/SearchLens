import time
from Quartz import *
from AppKit import *
from selenium import webdriver
import re
# 啟動 Chrome 瀏覽器
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--user-data-dir=/Users/xuzhilei/Library/Application Support/Google/Chrome")
chrome_options.add_argument('--app=https://universe.flyff.com/play') #關掉任何網址，工具列與分頁等等
chrome_options.add_experimental_option("useAutomationExtension", False);
chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
driver = webdriver.Chrome(options=chrome_options)

# 前往網頁
time.sleep(5)

window_size = driver.get_window_size()
print('瀏覽器視窗大小:', window_size)
canvas = driver.find_element("css selector", "canvas")
style_attr = canvas.get_attribute("style")
style_height = int(re.search(r"height:\s*(\d+)px", style_attr).group(1))
style_width = int(re.search(r"width:\s*(\d+)px", style_attr).group(1))

print("Canvas style:", style_height, " ", style_width)



# 等待網頁載入完成
wl = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements, kCGNullWindowID)

wl = sorted(wl, key=lambda k: k.valueForKey_('kCGWindowOwnerPID'))

#print wl

print('PID'.rjust(7) + ' ' + 'WinID'.rjust(5) + '  ' + 'x,y,w,h'.ljust(21) + ' ' + '\t[Title] SubTitle')
print('-'.rjust(7,'-') + ' ' + '-'.rjust(5,'-') + '  ' + '-'.ljust(21,'-') + ' ' + '\t-------------------------------------------')

window_id = -1
rect = ""
for v in wl:
    print(str(v.valueForKey_('kCGWindowOwnerPID')), " ", str(v.valueForKey_('kCGWindowNumber')), " " ,str(v.valueForKey_('kCGWindowOwnerName'))," ", str(v.valueForKey_('kCGWindowName')))
    print(str(int(v.valueForKey_('kCGWindowBounds').valueForKey_('X'))),"," ,str(int(v.valueForKey_('kCGWindowBounds').valueForKey_('Y'))) )
    print(str(int(v.valueForKey_('kCGWindowBounds').valueForKey_('Width'))),"," ,str(int(v.valueForKey_('kCGWindowBounds').valueForKey_('Height'))) )
    if "Google" in str(v.valueForKey_('kCGWindowOwnerName')):
        window_id = int(str(v.valueForKey_('kCGWindowNumber')))
        print("google chrome :" , window_id)
        print(v.valueForKey_('kCGWindowBounds'))
        reduce_height = int(v.valueForKey_('kCGWindowBounds').valueForKey_('Height')) - style_height
        rect = CGRectMake(int(v.valueForKey_('kCGWindowBounds').valueForKey_('X')),
                         int(v.valueForKey_('kCGWindowBounds').valueForKey_('Y')) + reduce_height,
                         int(v.valueForKey_('kCGWindowBounds').valueForKey_('Width')),
                         style_height
                         )
        break


s_time = time.time()
image = CGWindowListCreateImage(rect, kCGWindowListOptionIncludingWindow, window_id, kCGWindowImageBoundsIgnoreFraming)
e_time = time.time()

print("time cost  :", (e_time -s_time ))
# 將 CGImageRef 物件轉換為 NSImage 物件
ns_image = NSImage.alloc().initWithCGImage_(image)

# 將 NSImage 物件轉換為 PNG 格式的二進位資料
bitmap = NSBitmapImageRep.imageRepWithData_(ns_image.TIFFRepresentation())
png_data = bitmap.representationUsingType_properties_(NSBitmapImageFileTypePNG, None)

# 儲存 PNG 格式的畫面至檔案
with open("screenshot.png", "wb") as f:
    f.write(png_data)

# 關閉瀏覽器
driver.quit()
