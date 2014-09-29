import wit
import time

def callback(response):
	print("Response: {}".format(response))

if __name__ == "__main__":
	wit.init()
	wit.text_query_async("show me madonna", "ACCESS_TOKEN", callback)
	time.sleep(5)
	wit.close()
