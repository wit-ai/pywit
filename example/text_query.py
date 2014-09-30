import wit

if __name__ == "__main__":
	wit.init()
	response = wit.text_query("turn on the lights in the kitchen", "ACCESS_TOKEN")
	print("Response: {}".format(response))
	wit.close()
