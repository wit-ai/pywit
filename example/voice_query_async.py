import wit
import time

def callback(response):
	print("Response: {}".format(response))

if __name__ == "__main__":
	wit.init()
	wit.voice_query_start("ACCESS_TOKEN")
	time.sleep(2)
	wit.voice_query_stop_async(callback)
	time.sleep(5)
	wit.close()
