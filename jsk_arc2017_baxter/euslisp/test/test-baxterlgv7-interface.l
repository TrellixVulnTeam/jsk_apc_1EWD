#!/usr/bin/env roseus

(require :unittest "lib/llib/unittest.l")
(require "package://jsk_arc2017_baxter/euslisp/lib/baxterlgv7-interface.l")

(init-unit-test)

(setq *ri* (instance jsk_arc2017_baxter::baxterlgv7-interface :init))

(deftest
  test-speak

  (send *ri* :speak "Hello" :wait t)
  (send *ri* :speak "Hello")
  )

(run-all-tests)
(exit)