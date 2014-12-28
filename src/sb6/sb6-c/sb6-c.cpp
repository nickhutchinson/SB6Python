#include "sb6-c.h"

#include <sb6.h>

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

struct  _sb6_application : sb6::application {
    _sb6_application(const SB6AppContext* context) : ctx_(*context) {}

    SB6_THUNK_1(render, void, double)
    SB6_THUNK_0(startup, void)
    SB6_THUNK_0(shutdown, void)
    SB6_THUNK_2(onResize, void, int, int)

private:
    const SB6AppContext ctx_;
};



SB6ApplicationRef SB6ApplicationCreate(const SB6AppContext* context)
{
    return new _sb6_application(context);
}

void SB6ApplicationRun(SB6ApplicationRef app)
{
    app->run(app);
}

void SB6ApplicationDispose(SB6ApplicationRef app)
{
    delete app;
}


