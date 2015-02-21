import os
import time

times = 0
while times < 10:
	startTime = time.time()
	os.system('python amazon_top_50.py')
	duration = time.time()-startTime
	if duration<3:
		times = times + 1
	else:
		times = 0
	os.system('/etc/init.d/tor restart')
	
