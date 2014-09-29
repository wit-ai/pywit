import wit
import time

if __name__ == "__main__":
	wit.init()
	wit.voice_query_start("ACCESS_TOKEN")
	time.sleep(2)
	response = wit.voice_query_stop()
	print("Response: {}".format(response))
	wit.close()
