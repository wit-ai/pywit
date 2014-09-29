#ifndef WIT_H
#define WIT_H

#include <stdlib.h>

struct wit_context;
typedef void (*wit_resp_callback)(const char *);

struct wit_context *wit_init(const char *device_opt);
void wit_close(struct wit_context *context);
const char *wit_text_query(struct wit_context *context, const char *text, const char *access_token);
void wit_text_query_async(struct wit_context *context, const char *text, const char *access_token, wit_resp_callback cb);
const char *wit_voice_query_auto(struct wit_context *context, const char *access_token);
void wit_voice_query_auto_async(struct wit_context *context, const char *access_token, wit_resp_callback cb);
void wit_voice_query_start(struct wit_context *context, const char *access_token);
const char *wit_voice_query_stop(struct wit_context *context);
void wit_voice_query_stop_async(struct wit_context *context, wit_resp_callback cb);

#endif
