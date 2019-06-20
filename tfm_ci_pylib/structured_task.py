#!/usr/bin/env python3

""" structured_task.py:

    A generic abstraction class for executing a task with prerequesites and
    post execution action """

from __future__ import print_function

__copyright__ = """
/*
 * Copyright (c) 2018-2019, Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 */
 """
__author__ = "Minos Galanakis"
__email__ = "minos.galanakis@linaro.org"
__project__ = "Trusted Firmware-M Open CI"
__status__ = "stable"
__version__ = "1.1"

import abc
import time
import multiprocessing


class structuredTask(multiprocessing.Process):
    """ A class that defined well structured chained execution of commands """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):

        self._stopevent = multiprocessing.Event()
        self._exec_sleep_period = 1.0
        self._join_timeout = 1.0
        self._exec_timeout = 0.0
        self._task_name = name

        # multiprocessing safe shared memory variables
        self._mprc_manager = multiprocessing.Manager()

        # Dictionary used to store objects between stages
        self._mprc_stash = self._mprc_manager.dict()

        # Integer variable that stores status of flow
        self._mprc_status = multiprocessing.Value('i', False)
        super(structuredTask, self).__init__(name=name)

        # Perform initialization
        # If user code raises exception, class memory will not be allocated
        # Variables can be safely shared in the pre stages, use stash for
        # next stages
        self.pre_exec(self.pre_eval())

    # Class API/Interface

    @abc.abstractmethod
    def pre_eval(self):
        """ Tests that need to be run in set-up state """

    @abc.abstractmethod
    def pre_exec(self, eval_ret):
        """ Tasks that set-up execution enviroment """

    @abc.abstractmethod
    def task_exec(self):
        """ Main tasks """

    @abc.abstractmethod
    def post_eval(self, eval_ret):
        """ Tests that need to be run after main task """

    @abc.abstractmethod
    def post_exec(self):
        """ Tasks that are run after main task """

    def stash(self, key, data):
        """ Store object in a shared memory interface """

        self._mprc_stash[key] = data

    def unstash(self, key):
        """ Retrieve object from a shared memory interface """

        try:
            return self._mprc_stash[key]
        except KeyError:
            return None

    def get_name(self):
        """" Return name label of class """
        return self._task_name

    def get_status(self):
        """ Return the status of the execution flow """
        with self._mprc_status.get_lock():
            return self._mprc_status.value

    def set_status(self, status):
        """ Return the status of the execution flow """
        with self._mprc_status.get_lock():
            self._mprc_status.value = status

    def run(self):
        try:

            # Run Core code
            while not self._stopevent.is_set():
                self.task_exec()
                time.sleep(self._exec_sleep_period)
                break
            # print("Stop Event Detected")
            # TODO Upgrade reporting to a similar format
            print("%s ==> Stop Event Detected" % self.get_name())

            # Post stage
            # If something faifs in post the user should set the correct status
            self.set_status(0)
            print("%s ==> Stop Event Set OK Status" % self.get_name())
        except Exception as exc:
            print(("ERROR: Stopping %s "
                  "with Exception: \"%s\"") % (self.get_name(), exc))
            self.set_status(1)
        # Always call post, and determine success failed by get_status
        self.post_exec(self.post_eval())

    def _t_stop(self):
        """ Internal class stop to be called through thread """

        if(self.is_alive()):
            print("%s =========> STOP" % self.get_name())
            self._stopevent.set()
            print("Thead is alive %s" % self.is_alive())
            print("Stop Event Triggered")

    def stop(self):
        """ External stop to be called by user code """

        self._t_stop()
        super(structuredTask, self).join(self._join_timeout)
