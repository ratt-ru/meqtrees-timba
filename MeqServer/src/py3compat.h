#ifndef PY3COMPAT_H
#define PY3COMPAT_H
    #include <Python.h>
    #include <pyconfig.h>

    #include <string>
    #include <locale>
    #include <codecvt>
    #include <iostream>

    #if PY_MAJOR_VERSION < 3
        // Typedef string_t helper functions to unicode
        #include <unicodeobject.h>
        #define string_t string_t
        #define char_t char
    #else //PY_MAJOR_VERSION >= 3
        #define char_t wchar_t
        #define string_t std::wstring //fantastically hacky kludge because python3 is all unicode
        #define PyString_FromString(p) PyUnicode_FromString(p)
        #define PyString_AS_STRING(p) \
                (char*) PyUnicode_AsUTF8(PyUnicode_AsUnicode(p)).c_str()
        #define PyString_AsString(p) \
                (char*) PyUnicode_AsUTF8(PyUnicode_AsUnicode(p)).c_str()
        #define PyUnicode_Check(op) \
                PyType_FastSubclass(Py_TYPE(op), Py_TPFLAGS_UNICODE_SUBCLASS)
        #define PyString_Check PyUnicode_Check
        #define PyString PyUnicode
        #define unicode2utf8(p) std::wstring_convert<std::codecvt_utf8<wchar_t>>().to_bytes(p)
        #define utf82unicode(p) std::wstring_convert<std::codecvt_utf8<wchar_t>>().from_bytes(p)
        #define PyDict_SetItemString(rec, name, item) \
                PyDict_SetItemString(rec,unicode2utf8(name).c_str(), item)
        #define PyErr_SetString(errobj, err) PyErr_SetString(errobj, unicode2utf8(err))

        // Now typedef all ints to longs...
        #include <longobject.h>
        #define PyInt_FromString PyLong_FromString
        #ifdef Py_USING_UNICODE
        #define PyInt_FromUnicode PyLong_FromUnicode
        #endif
        #define PyInt_FromLong PyLong_FromLong
        #define PyInt_FromSize_t PyLong_FromSize_t
        #define PyInt_FromSsize_t PyLong_FromSsize_t
        #define PyInt_AsLong PyLong_AsLong
        #define PyInt_AsSsize_t PyLong_AsSsize_t
        #define _PyInt_AsInt PyLong_AsLong
        #define PyInt_AsUnsignedLongMask PyLong_AsUnsignedLongMask
        #ifdef HAVE_LONG_LONG
        #define PyInt_AsUnsignedLongLongMask PyLong_AsUnsignedLongLongMask
        #endif
        #define PyLong_Check(op) \
                PyType_FastSubclass(Py_TYPE(op), Py_TPFLAGS_LONG_SUBCLASS)
        #define PyInt_Check PyLong_Check
        #define PyInt_AS_LONG = PyLong_AsLong;

        /* Convert an integer to the given base.  Returns a string.
        If base is 2, 8 or 16, add the proper prefix '0b', '0o' or '0x'.
        If newstyle is zero, then use the pre-2.6 behavior of octal having
        a leading "0" */
        #define _PyInt_Format _PyLong_Format

        /* Format the object based on the format_spec, as defined in PEP 3101
        (Advanced String Formatting). */
        //const auto _PyInt_FormatAdvanced = _PyLong_FormatAdvanced;
    #endif
#endif