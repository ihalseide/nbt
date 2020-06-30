;;;; dev-load.lisp

(in-package :cl-user)

(fresh-line)
(princ "Starting dev-load.")
(fresh-line)


(fresh-line)
(princ "Loading macro-utils files...")
(fresh-line)

(load "c:/Users/ihals/Desktop/macro-utils/packages.lisp")
(load "c:/Users/ihals/Desktop/macro-utils/macro-utils.lisp")

(fresh-line)
(princ "Successfully loaded macro-utils.")
(fresh-line)

(fresh-line)
(princ "Loading binary-data files...")
(fresh-line)

(load "c:/Users/ihals/Desktop/binary-data/packages.lisp")
(load "c:/Users/ihals/Desktop/binary-data/binary-data.lisp")

(fresh-line)
(princ "Successfully loaded binary-data files.")
(fresh-line)

(fresh-line)
(princ "Loading nbt-explorer files...")
(fresh-line)

(load "c:/Users/ihals/Desktop/nbt-explorer/packages.lisp")
(load "c:/Users/ihals/Desktop/nbt-explorer/macros.lisp")
(load "c:/Users/ihals/Desktop/nbt-explorer/nbt-explorer.lisp")

(fresh-line)
(princ "Successfully loaded nbt-explorer files.")
(fresh-line)

(fresh-line)
(princ "Completely done with dev-load!")
(fresh-line)
