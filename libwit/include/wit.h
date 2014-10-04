#ifndef WIT_H
#define WIT_H

#include <stdlib.h>

struct wit_context;
typedef void (*wit_resp_callback)(char *);

/**
 * Initialize the resources for audio recording and Wit API requests.
 * This function returns a context object used by all the other functions
 * in the library.
 * The resources can be released using wit_close.
 */
struct wit_context *wit_init(const char *device_opt, unsigned int verbosity);

/**
 * Release the resources allocated by wit_init.
 * The context object should not be used for any other purpose after this function
 * has been called.
 */
void wit_close(struct wit_context *context);

/**
 * Send a text query to the Wit instance identified by the access_token.
 * This function is blocking, and returns the response from the Wit instance.
 */
char *wit_text_query(struct wit_context *context, const char *text, const char *access_token);

/**
 * Send a text query to the Wit instance identified by the access_token.
 * This function is non-blocking. When a response is received from the Wit instance, the
 * given callback is called with the response given as an argument.
 */
void wit_text_query_async(struct wit_context *context, const char *text, const char *access_token, wit_resp_callback cb);

/**
 * Send a voice query to the Wit instance identified by the access_token.
 * This function is blocking, and returns the response from the Wit instance.
 *
 * The function attempts to automatically detect when the user stops speaking. If this
 * fails, the wit_voice_query_stop or wit_voice_query_stop_async functions below can
 * be used to trigger the end of the request and receive the response.
 */
char *wit_voice_query_auto(struct wit_context *context, const char *access_token);

/**
 * Send a voice query to the Wit instance identified by the access_token.
 * This function is non-blocking. When a response is received from the Wit instance, the
 * given callback is called with the response given as an argument.
 *
 * The function attempts to automatically detect when the user stops speaking. If this
 * fails, the wit_voice_query_stop or wit_voice_query_stop_async functions below can
 * be used to trigger the end of the request and receive the response.
 */
void wit_voice_query_auto_async(struct wit_context *context, const char *access_token, wit_resp_callback cb);

/**
 * Send a voice query to the Wit instance identified by the access_token.
 * This function returns immediately: the recording session stops only when either
 * wit_voice_query_stop or wit_voice_query_stop_async is called. No end-of-speech
 * detection is performed.
 */
void wit_voice_query_start(struct wit_context *context, const char *access_token);

/**
 * Stop the ongoing recording session and receive the response.
 * This function is blocking, and returns the response from the Wit instance.
 * This function has no effect if there is no ongoing recording session.
 */
char *wit_voice_query_stop(struct wit_context *context);

/**
 * Stop the ongoing recording session and receive the response.
 * This function is non-blocking. When a response is received from the Wit instance, the
 * given callback is called with the response given as an argument.
 * This function has no effect if there is no ongoing recording session.
 */
void wit_voice_query_stop_async(struct wit_context *context, wit_resp_callback cb);

#endif
