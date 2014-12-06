#include "sb6-c.h"

#include <sb6.h>

#if __cplusplus > 199711L
#define OVERRIDE override
#else
#define OVERRIDE
#endif

#define SB6_THUNK_0(methodName, returnType)                         \
  returnType methodName() OVERRIDE {                                \
    if (ctx_.methodName != NULL) return ctx_.methodName(ctx_.self); \
  }

#define SB6_THUNK_1(methodName, returnType, argType1)                     \
  returnType methodName(argType1 arg1) OVERRIDE {                         \
    if (ctx_.methodName != NULL) return ctx_.methodName(ctx_.self, arg1); \
  }

struct  __SB6Application : sb6::application {
    __SB6Application(const SB6AppContext* context) : ctx_(*context) {}

    SB6_THUNK_1(render, void, double)
    SB6_THUNK_0(startup, void)
    SB6_THUNK_0(shutdown, void)

private:
    const SB6AppContext ctx_;
};



SB6ApplicationRef SB6ApplicationCreate(const SB6AppContext* context)
{
    return new __SB6Application(context);
}

void SB6ApplicationRun(SB6ApplicationRef app)
{
    app->run(app);
}

void SB6ApplicationDispose(SB6ApplicationRef app)
{
    delete app;
}


