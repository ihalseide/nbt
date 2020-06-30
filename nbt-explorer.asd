;;;; nbt-explorer.asd

(asdf:defsystem #:nbt-explorer
  :description "For exploring Named Binary Tag files."
  :author "Izak Halseide"
  :license  "MIT License"
  :version "0.0.1"
  :serial t
  :depends-on (#:binary-data)
  :components ((:file "packages")
               (:file "macros"
                :depends-on ("packages"))
               (:file "nbt-explorer" 
                :depends-on ("packages" "macros"))))
