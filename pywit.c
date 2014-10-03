#include <Python.h>
#include "wit.h"

struct wit_context *context;

static PyObject *WitError;

static PyObject *pywit_init(PyObject *self, PyObject *args)
{
	const char *device_opt = NULL;
	if (!PyArg_ParseTuple(args, "|s", &device_opt))
		return NULL;
	context = wit_init(device_opt, 4);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *pywit_close()
{
	if (context != NULL)
		wit_close(context);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *pywit_text_query(PyObject *self, PyObject *args)
{
	const char *text;
	const char *access_token;
	char *res;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	if (!PyArg_ParseTuple(args, "ss", &text, &access_token))
		return NULL;
	res = wit_text_query(context, text, access_token);
	PyObject *obj = Py_BuildValue("s", res);
	Py_XDECREF(res);
	return obj;
}

static PyObject *pywit_voice_query_start(PyObject *self, PyObject *args)
{
	const char *access_token;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	if (!PyArg_ParseTuple(args, "s", &access_token))
		return NULL;
	wit_voice_query_start(context, access_token);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *pywit_voice_query_stop()
{
	char *res;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	res = wit_voice_query_stop(context);
	PyObject *obj = Py_BuildValue("s", res);
	Py_XDECREF(res);
	return obj;
}

static PyObject *pywit_voice_query_auto(PyObject *self, PyObject *args)
{
	const char *access_token;
	char *res;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	if (!PyArg_ParseTuple(args, "s", &access_token))
		return NULL;
	res = wit_voice_query_auto(context, access_token);
	PyObject *obj = Py_BuildValue("s", res);
	Py_XDECREF(res);
	return obj;
}

static PyObject *saved_py_cb = NULL;

PyGILState_STATE state;

void my_wit_resp_callback(char *res) {
	PyObject *result;
	state = PyGILState_Ensure();
	PyObject *args = Py_BuildValue("(s)", res);
	Py_XDECREF(res);
	result = PyObject_CallObject(saved_py_cb, args);
	Py_XDECREF(args);
	Py_XDECREF(result);
	PyGILState_Release(state);
}

static PyObject *pywit_text_query_async(PyObject *self, PyObject *args)
{
	const char *text;
	const char *access_token;
	PyObject *py_cb;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	if (!PyArg_ParseTuple(args, "ssO", &text, &access_token, &py_cb))
		return NULL;
	if (!PyCallable_Check(py_cb)) {
		PyErr_SetString(WitError, "Parameter must be callable.");
		return NULL;
	}
	Py_XINCREF(py_cb);
	Py_XDECREF(saved_py_cb);
	saved_py_cb = py_cb;
	wit_text_query_async(context, text, access_token, my_wit_resp_callback);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *pywit_voice_query_auto_async(PyObject *self, PyObject *args)
{
	const char *access_token;
	PyObject *py_cb;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	if (!PyArg_ParseTuple(args, "sO", &access_token, &py_cb))
		return NULL;
	if (!PyCallable_Check(py_cb)) {
		PyErr_SetString(WitError, "Parameter must be callable.");
		return NULL;
	}
	Py_XINCREF(py_cb);
	Py_XDECREF(saved_py_cb);
	saved_py_cb = py_cb;
	wit_voice_query_auto_async(context, access_token, my_wit_resp_callback);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *pywit_voice_query_stop_async(PyObject *self, PyObject *args)
{
	PyObject *py_cb;
	if (context == NULL) {
		PyErr_SetString(WitError, "Wit context uninitialized (did you call wit.init()?)");
		return NULL;
	}
	if (!PyArg_ParseTuple(args, "O", &py_cb))
		return NULL;
	if (!PyCallable_Check(py_cb)) {
		PyErr_SetString(WitError, "Parameter must be callable.");
		return NULL;
	}
	Py_XINCREF(py_cb);
	Py_XDECREF(saved_py_cb);
	saved_py_cb = py_cb;
	wit_voice_query_stop_async(context, my_wit_resp_callback);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef WitMethods[] = {
	{"init", pywit_init, METH_VARARGS, "Initialize wit."},
	{"close", pywit_close, METH_NOARGS, "Close wit."},
	{"text_query", pywit_text_query, METH_VARARGS, "Get intent via text."},
	{"voice_query_start", pywit_voice_query_start, METH_VARARGS, "Start recording."},
	{"voice_query_stop", pywit_voice_query_stop, METH_NOARGS, "Get intent via voice."},
	{"voice_query_auto", pywit_voice_query_auto, METH_VARARGS, "Get intent via voice, and detect end of speech."},
	{"text_query_async", pywit_text_query_async, METH_VARARGS, "Get intent via text asynchronously."},
	{"voice_query_auto_async", pywit_voice_query_auto_async, METH_VARARGS, "Get intent via voice with automatic end-of-speech detection,  asynchronously."},
	{"voice_query_stop_async", pywit_voice_query_stop_async, METH_VARARGS, "Get intent via voice asynchronously."},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initwit(void)
{
	PyObject *m;
	m = Py_InitModule("wit", WitMethods);
	if (m == NULL)
		return;
	WitError = PyErr_NewException("wit.error", NULL, NULL);
	Py_INCREF(WitError);
	PyModule_AddObject(m, "error", WitError);
	PyEval_InitThreads();
}
