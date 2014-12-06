#!/usr/bin/env python
# encoding: utf-8
import click
from .app import Application as SB6App, IApplicationDelegate as ISB6AppDelegate


class MyApplication(ISB6AppDelegate):

    def __init__(self):
        self._app = SB6App(self)
        self._counter = 0

    def render(self, app, currentTime):
        print "render {!r}".format(self._counter)
        self._counter += 1

    def run(self):
        self._app.run()


@click.command()
def main():
    app = MyApplication()
    app.run()

