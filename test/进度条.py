import time
import sys
for i in range(30):
    sys.stdout.write('**')   #print()内部调用
    time.sleep(0.5)
    sys.stdout.flush()  #刷新缓存