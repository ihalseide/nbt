;;;; nbt-explorer.lisp

(in-package #:com.div0.nbt-explorer)

;; Base for the byte, short, integer, and long types
;; Big Endian, Signed Integer
(define-binary-type signed-integer (num-bytes)
  (:reader (in)
   nil)
  (:writer (out value)
   nil))

(define-binary-type unsigned-integer (num-bytes)
  (:reader (in)
   nil)
  (:writer (out value)
   nil))

;; Single precision float
(define-binary-type float-ieee-754-2008 ()
  (:reader (in))
  (:writer (out value)))

;; Double precision float
(define-binary-type double-iee-754-2008 ()
  (:reader (in))
  (:writer (out value)))

;; "byte" data type
(define-binary-type s1 () (signed-integer :num-bytes 1))

;; "short" data type
(define-binary-type s2 () (signed-integer :num-bytes 2))

;; "integer" data type
(define-binary-type s4 () (signed-integer :num-bytes 4))

;; "long" data type
(define-binary-type s8 () (signed-integer :num-bytes 8))
