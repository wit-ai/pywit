import wit

if __name__ == "__main__":
	wit.init()
	response = wit.voice_query_auto("ACCESS_TOKEN")
	print("Response: {}".format(response))
	wit.close()
