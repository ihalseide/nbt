;;;; nbt-explorer.lisp

(in-package #:nbt-explorer)

;; Base for the byte, short, integer, and long types
;; Big Endian, Signed Integer
(define-binary-type signed-integer (num-bytes)
                    (:reader (in)
                     (loop with value = 0
                           with first-bit = nil ; Becomes the first bit that is read, for sign
                           for low-bit downfrom (* 8 (1- bytes)) to 0 by 8
                           do (let ((byte (read-byte in)))
                                ;; When getting the first byte, get the first bit and only
                                ;; write the next 7 bits to the value.
                                (cond ((null first-bit)
                                       (setf first-bit ())
                                       (setf (ldb (byte 7? low-bit) value) byte)) 
                                      (t 
                                       (setf (ldb (byte 8 low-bit) value) byte))))
                           finally (return value)))
                    (:writer (out value)
                     (loop for low-bit downfrom (* 8 (1- bytes)) to 0 by 8
                           do (write-byte (ldb (byte 8 low-bit) value) out))))

;; "byte" data type
(define-binary-type s1 () (signed-integer :num-bytes 1))

;; "short" data type
(define-binary-type s2 () (signed-integer :num-bytes 2))

;; "integer" data type
(define-binary-type s4 () (signed-integer :num-bytes 4))

;; "long" data type
(define-binary-type s8 () (signed-integer :num-bytes 8))

;; Single precision float
(define-binary-type float-ieee-754-2008 ()
                   (:reader (in))
                   (:writer (out value)))

;; Double precision float
(define-binary type double-iee-754-2008 ()
               (:reader (in))
               (:writer (out value)))


