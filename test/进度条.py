import time
import sys
for i in range(60):
    sys.stdout.write('*')   #print()内部调用
    time.sleep(0.1)
    sys.stdout.flush()  #刷新缓存