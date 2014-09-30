import wit
import time

def callback(response):
	print("Response: {}".format(response))

if __name__ == "__main__":
	wit.init()
	wit.text_query_async("turn on the lights in the kitchen", "ACCESS_TOKEN", callback)
	time.sleep(5)
	wit.close()
