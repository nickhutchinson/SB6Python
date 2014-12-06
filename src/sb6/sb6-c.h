#pragma once

#ifdef __cplusplus
#define SB6_EXTERN extern "C" __attribute__((visibility("default")))
#else
#define SB6_EXTERN __attribute__((visibility("default")))
#endif

struct SB6AppContext {
  void* self;
  void (*render)(void* self, double currentTime);
};

typedef struct __SB6Application* SB6ApplicationRef;

SB6_EXTERN
SB6ApplicationRef SB6ApplicationCreate(const struct SB6AppContext*);

SB6_EXTERN
void SB6ApplicationRun(SB6ApplicationRef);

SB6_EXTERN
void SB6ApplicationDispose(SB6ApplicationRef);

