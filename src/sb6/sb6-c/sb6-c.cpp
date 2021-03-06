#include "sb6-c.h"

#include <sb6.h>
#include <object.h>
#include <sb6ktx.h>

// #if __cplusplus > 199711L
#define OVERRIDE override
// #else
// #define OVERRIDE
// #endif

#define SB6_THUNK_0(methodName, returnType)                         \
  virtual returnType methodName() OVERRIDE {                        \
    if (ctx_.methodName != NULL) return ctx_.methodName(ctx_.self); \
  }

#define SB6_THUNK_1(methodName, returnType, argType1)                     \
  virtual returnType methodName(argType1 arg1) OVERRIDE {                 \
    if (ctx_.methodName != NULL) return ctx_.methodName(ctx_.self, arg1); \
  }

#define SB6_THUNK_2(methodName, returnType, argType1, argType2)          \
  virtual returnType methodName(argType1 arg1, argType2 arg2) OVERRIDE { \
    if (ctx_.methodName != NULL)                                         \
        return ctx_.methodName(ctx_.self, arg1, arg2);                   \
  }

struct _sb6_application : sb6::application {
  _sb6_application(const SB6AppContext* context) : ctx_(*context) {}

  SB6_THUNK_1(render, void, double)
  SB6_THUNK_0(startup, void)
  SB6_THUNK_0(shutdown, void)
  SB6_THUNK_2(onResize, void, int, int)

 private:
  const SB6AppContext ctx_;
};

SB6ApplicationRef SB6ApplicationCreate(const SB6AppContext* context) {
  return new _sb6_application(context);
}

void SB6ApplicationRun(SB6ApplicationRef app) { app->run(app); }

void SB6ApplicationDispose(SB6ApplicationRef app) { delete app; }

void SB6TextureLoadFromFile(unsigned textureID, const char* path) {
  sb6::ktx::file::load(path, textureID);
}

struct _sb6_object {
  sb6::object impl_;
};

SB6ObjectRef SB6ObjectCreateFromFile(const char* filePath) {
  SB6ObjectRef obj = new _sb6_object;
  obj->impl_.load(filePath);
  return obj;
}

void SB6ObjectDispose(SB6ObjectRef obj) {

  obj->impl_.free();

  delete obj;
}

void SB6ObjectRender(SB6ObjectRef obj) { obj->impl_.render(); }
