import wit

if __name__ == "__main__":
	wit.init()
	response = wit.text_query("show me madonna", "ACCESS_TOKEN")
	print("Response: {}".format(response))
	wit.close()
