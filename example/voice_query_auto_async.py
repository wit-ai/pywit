import wit
import time

def callback(response):
	print("Response: {}".format(response))

if __name__ == "__main__":
	wit.init()
	wit.voice_query_auto_async("ACCESS_TOKEN", callback)
	time.sleep(5)
	wit.close()
